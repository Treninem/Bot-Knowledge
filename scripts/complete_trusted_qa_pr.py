"""Isolated maintainer-only completion gate for a reviewed qa.v1 publisher PR.

No BotHost code imports this file. No write token is passed to consumers.
Do not use it to finalize arbitrary PRs: it only accepts the two-file,
append-only draft created by trusted_publish_qa.py, with a pinned head SHA.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

try:
    from scripts.validate_qa_v1 import validate_qa_pack
except ModuleNotFoundError:  # direct python scripts/complete_trusted_qa_pr.py
    from validate_qa_v1 import validate_qa_pack

REPO = "Treninem/Bot-Knowledge"
API = "https://api.github.com"
HEAD = re.compile(r"[0-9a-f]{40}\Z")
MARKER = "Reviewed qa.v1 publication candidate."
EXACT = (".github/workflows/trusted-qa-publisher.yml", "Trusted qa.v1 publisher exact-head")
QUALITY = (".github/workflows/quality.yml", "Bot-Knowledge quality")


class FinalizeError(RuntimeError):
    pass


def request(path: str, *, token: str, method: str = "GET", data=None):
    if not path.startswith("/") or path.startswith("//"):
        raise FinalizeError("unsafe API path")
    payload = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(
        API + path, data=payload, method=method,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Bot-Knowledge-Trusted-Finalizer/1.0",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            data_bytes = response.read(8 * 1024 * 1024 + 1)
    except urllib.error.HTTPError as exc:
        # Do not include submitted credentials or request headers in a report.
        raise FinalizeError(f"GitHub HTTP {exc.code} on {method} {path.split('?')[0]}") from exc
    except urllib.error.URLError as exc:
        raise FinalizeError("GitHub request unavailable") from exc
    if len(data_bytes) > 8 * 1024 * 1024:
        raise FinalizeError("GitHub response too large")
    return json.loads(data_bytes) if data_bytes else {}


def content(path: str, *, token: str, ref: str):
    metadata = request(f"/repos/{REPO}/contents/{quote(path, safe='/')}?ref={quote(ref, safe='')}", token=token)
    if not isinstance(metadata, dict) or metadata.get("encoding") != "base64":
        raise FinalizeError("unexpected file representation")
    raw = base64.b64decode(metadata.get("content", ""), validate=False)
    return json.loads(raw.decode("utf-8")), raw


def trusted_environment(token: str) -> None:
    if not token or os.getenv("BK_TRUSTED_PUBLISHER") != "1":
        raise FinalizeError("isolated maintainer token and BK_TRUSTED_PUBLISHER=1 required")
    if os.getenv("BOT_TOKEN") or os.getenv("IMPULS_BOT_TOKEN"):
        raise FinalizeError("refusing to run with bot runtime credentials")


def guard_pr(pr: dict, *, number: int, expected_head: str, base: str, expected_base_sha: str | None = None) -> str:
    if not HEAD.fullmatch(expected_head) or not isinstance(pr, dict):
        raise FinalizeError("invalid pinned expected-head SHA")
    if pr.get("number") != number or pr.get("state") != "open":
        raise FinalizeError("PR is missing or no longer open")
    h, b = pr.get("head") or {}, pr.get("base") or {}
    if h.get("sha") != expected_head or (h.get("repo") or {}).get("full_name") != REPO:
        raise FinalizeError("PR head SHA/repository changed; refuse stale approval")
    if b.get("ref") != base or base != "main":
        raise FinalizeError("unexpected PR base")
    if expected_base_sha is not None and b.get("sha") != expected_base_sha:
        raise FinalizeError("PR base SHA changed during validation")
    if MARKER not in (pr.get("body") or ""):
        raise FinalizeError("PR is not a reviewed qa.v1 publisher candidate")
    return b["sha"]


def verify_append_only(number: int, *, token: str, base_sha: str, head_sha: str) -> dict:
    files = request(f"/repos/{REPO}/pulls/{number}/files?per_page=100", token=token)
    if not isinstance(files, list) or len(files) != 2:
        raise FinalizeError("publisher PR must change exactly a pack and manifest")
    names = {f.get("filename") for f in files}
    packages = [p for p in names if isinstance(p, str) and re.fullmatch(r"packs/ru/[A-Za-z0-9._-]+\.json", p)]
    if len(packages) != 1 or names != {"manifest.json", packages[0]}:
        raise FinalizeError("unexpected files in publisher PR")
    if any(f.get("status") != "modified" for f in files):
        raise FinalizeError("publisher only appends to an already registered package")
    path = packages[0]
    before, _ = content("manifest.json", token=token, ref=base_sha)
    after, _ = content("manifest.json", token=token, ref=head_sha)
    old_entries, new_entries = before.get("packs"), after.get("packs")
    if not isinstance(old_entries, list) or not isinstance(new_entries, list) or len(old_entries) != len(new_entries):
        raise FinalizeError("manifest pack list changed")
    if set(before) != set(after) or any(
        before.get(key) != after.get(key)
        for key in before if key not in {"packs", "knowledge_version", "generated_at"}
    ):
        raise FinalizeError("unrelated manifest metadata changed")
    old_by_path = {p["path"]: p for p in old_entries}
    new_by_path = {p["path"]: p for p in new_entries}
    if len(old_by_path) != len(old_entries) or set(old_by_path) != set(new_by_path) or path not in old_by_path:
        raise FinalizeError("unexpected manifest path changes")
    for other in old_by_path:
        if other != path and old_by_path[other] != new_by_path[other]:
            raise FinalizeError("unrelated manifest digest changed")
    if set(old_by_path[path]) != {"path", "sha256"} or set(new_by_path[path]) != {"path", "sha256"}:
        raise FinalizeError("unexpected target manifest metadata")
    old_pack, _ = content(path, token=token, ref=base_sha)
    new_pack, raw = content(path, token=token, ref=head_sha)
    digest = hashlib.sha256(raw).hexdigest()
    if digest != new_by_path[path]["sha256"]:
        raise FinalizeError("manifest SHA-256 does not match actual new pack bytes")
    if new_pack.get("pack_version") != after.get("knowledge_version"):
        raise FinalizeError("pack and manifest versions disagree")
    if new_pack.get("catalog", {}).get("adapter") != "qa.v1":
        raise FinalizeError("target package is not qa.v1")
    validate_qa_pack(new_pack)
    old_catalog, new_catalog = old_pack.get("catalog", {}), new_pack.get("catalog", {})
    if old_catalog != new_catalog:
        raise FinalizeError("publisher must not modify catalog permissions")
    rows_name = new_catalog.get("records", "records")
    old_rows, new_rows = old_pack.get(rows_name), new_pack.get(rows_name)
    if not isinstance(old_rows, list) or not isinstance(new_rows, list) or new_rows[:-1] != old_rows:
        raise FinalizeError("publisher must append one record without changing old entries")
    if len(new_rows) != len(old_rows) + 1:
        raise FinalizeError("publisher must add exactly one reviewed record")
    for key in old_pack:
        if key not in {"pack_version", rows_name} and old_pack.get(key) != new_pack.get(key):
            raise FinalizeError("publisher modified unrelated pack metadata")
    if set(old_pack) != set(new_pack):
        raise FinalizeError("publisher changed pack structure")
    if not isinstance(new_rows[-1].get("source"), str) or not new_rows[-1]["source"].startswith("https://"):
        raise FinalizeError("appended record lacks reviewed HTTPS source")
    return {"path": path, "added_records": 1, "pack_sha256": digest,
            "knowledge_version": after["knowledge_version"], "record_id": new_rows[-1]["id"]}


def choose_run(runs: list, expected_head: str, branch: str, expected: tuple[str, str]) -> dict | None:
    path, name = expected
    matches = [r for r in runs if isinstance(r, dict)
               and r.get("path") == path and r.get("name") == name
               and r.get("head_sha") == expected_head and r.get("head_branch") == branch
               and r.get("event") == "pull_request"]
    if not matches:
        return None
    return max(matches, key=lambda r: (r.get("created_at") or "", int(r.get("id") or 0)))


def public_run(run: dict | None) -> dict:
    if run is None:
        return {"status": "not_started"}
    return {key: run.get(key) for key in ("id", "status", "conclusion", "head_sha", "html_url")}


def wait_ci(head: str, branch: str, *, token: str, timeout: int, interval: int, post_main: bool = False) -> dict:
    target = (".github/workflows/quality.yml", "Bot-Knowledge quality") if post_main else None
    event = "push" if post_main else "pull_request"
    deadline = time.monotonic() + timeout
    last = {}
    while True:
        response = request(f"/repos/{REPO}/actions/runs?head_sha={head}&event={event}&per_page=100", token=token)
        all_runs = response.get("workflow_runs", [])
        if post_main:
            matches = [r for r in all_runs if isinstance(r, dict) and
                       r.get("path") == target[0] and r.get("name") == target[1] and
                       r.get("head_sha") == head and r.get("event") == "push"]
            found = max(matches, key=lambda r: (r.get("created_at") or "", int(r.get("id") or 0))) if matches else None
            last = {"post_main_quality": public_run(found)}
            required = [found]
        else:
            exact = choose_run(all_runs, head, branch, EXACT)
            quality = choose_run(all_runs, head, branch, QUALITY)
            last = {"exact_head": public_run(exact), "quality": public_run(quality)}
            required = [exact, quality]
        if all(r is not None and r.get("status") == "completed" and r.get("conclusion") == "success" for r in required):
            return last
        if any(r is not None and r.get("status") == "completed" and r.get("conclusion") not in {"success"} for r in required):
            raise FinalizeError("required CI failed: " + json.dumps(last, ensure_ascii=False))
        if time.monotonic() >= deadline:
            raise FinalizeError("required CI not completed before bounded timeout: " + json.dumps(last, ensure_ascii=False))
        time.sleep(min(interval, max(0.0, deadline - time.monotonic())))


def make_ready(pr: dict, *, token: str) -> None:
    node_id = pr.get("node_id")
    if not isinstance(node_id, str) or not node_id:
        raise FinalizeError("missing pull request node ID")
    result = request("/graphql", token=token, method="POST", data={
        "query": "mutation($id:ID!){markPullRequestReadyForReview(input:{pullRequestId:$id}){pullRequest{id,isDraft}}}",
        "variables": {"id": node_id},
    })
    if result.get("errors") or result.get("data", {}).get("markPullRequestReadyForReview", {}).get("pullRequest", {}).get("isDraft") is not False:
        raise FinalizeError("could not mark reviewed PR ready")


def finalize(*, number: int, expected_head: str, token: str, base: str, merge: bool,
             ready: bool, timeout: int, post_timeout: int, interval: int, report: dict) -> dict:
    trusted_environment(token)
    pr = request(f"/repos/{REPO}/pulls/{number}", token=token)
    base_sha = guard_pr(pr, number=number, expected_head=expected_head, base=base)
    report.update({"repository": REPO, "pr": number, "head_sha": expected_head,
                   "base_sha": base_sha, "status": "verifying", "merged": False})
    base_ref = request(f"/repos/{REPO}/git/ref/heads/{quote(base)}", token=token)
    if base_ref.get("object", {}).get("sha") != base_sha:
        raise FinalizeError("base moved; reopen review against current main")
    report["content"] = verify_append_only(number, token=token, base_sha=base_sha, head_sha=expected_head)
    report["pre_merge_ci"] = wait_ci(expected_head, pr["head"]["ref"], token=token, timeout=timeout, interval=interval)
    current = request(f"/repos/{REPO}/pulls/{number}", token=token)
    guard_pr(current, number=number, expected_head=expected_head, base=base, expected_base_sha=base_sha)
    latest_main = request(f"/repos/{REPO}/git/ref/heads/{quote(base)}", token=token)
    if latest_main.get("object", {}).get("sha") != base_sha:
        raise FinalizeError("main advanced since exact-head verification; review and retest")
    if current.get("draft"):
        if not ready or not merge:
            raise FinalizeError("draft remains; require explicit --ready after trusted review")
        make_ready(current, token=token)
        current = request(f"/repos/{REPO}/pulls/{number}", token=token)
        guard_pr(current, number=number, expected_head=expected_head, base=base, expected_base_sha=base_sha)
    if current.get("draft"):
        raise FinalizeError("PR still draft")
    if current.get("mergeable") is not True:
        raise FinalizeError("GitHub does not consider PR mergeable")
    if not merge:
        report["status"] = "checked_ready_not_merged"
        return report
    # PUT merge is an opt-in maintainer action; sha guards unexpected head movement.
    result = request(f"/repos/{REPO}/pulls/{number}/merge", token=token, method="PUT",
                     data={"sha": expected_head, "merge_method": "squash"})
    if result.get("merged") is not True or not HEAD.fullmatch(str(result.get("sha", ""))):
        raise FinalizeError("GitHub did not confirm the guarded merge")
    report["merged"] = True
    report["merge_sha"] = result["sha"]
    report["status"] = "merged_post_main_pending"
    report["post_main_ci"] = wait_ci(result["sha"], base, token=token, timeout=post_timeout,
                                   interval=interval, post_main=True)
    report["status"] = "merged_post_main_pass"
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Finish one reviewed qa.v1 PR only from an isolated trusted maintainer")
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--expected-head", required=True, help="Pinned 40-character PR head SHA")
    parser.add_argument("--base", default="main")
    parser.add_argument("--merge", action="store_true", help="Opt in to guarded squash merge")
    parser.add_argument("--ready", action="store_true", help="Mark reviewed draft ready before merge")
    parser.add_argument("--timeout", type=int, default=900, help="Bounded exact-head CI wait (seconds)")
    parser.add_argument("--post-timeout", type=int, default=900, help="Bounded post-main CI wait (seconds)")
    parser.add_argument("--interval", type=int, default=15)
    parser.add_argument("--report", type=Path, default=Path("trusted_qa_publish_report.json"))
    args = parser.parse_args()
    if args.pr <= 0 or not HEAD.fullmatch(args.expected_head) or args.timeout < 0 or args.post_timeout < 0 or args.interval < 1:
        parser.error("invalid PR/head/poll limits")
    report = {"created_at": datetime.now(timezone.utc).isoformat(), "status": "blocked",
              "repository": REPO, "pr": args.pr, "head_sha": args.expected_head, "merged": False}
    failure = None
    try:
        finalize(number=args.pr, expected_head=args.expected_head, token=os.getenv("GITHUB_TOKEN", ""),
                 base=args.base, merge=args.merge, ready=args.ready, timeout=args.timeout,
                 post_timeout=args.post_timeout, interval=args.interval, report=report)
    except (FinalizeError, ValueError, KeyError, TypeError, UnicodeError, OSError) as exc:
        failure = str(exc)
        report["reason"] = failure
        report["status"] = "merged_post_main_unconfirmed" if report.get("merged") else "blocked"
    finally:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
    if failure:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
