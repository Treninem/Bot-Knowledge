"""Trusted maintainer publisher for one reviewed qa.v1 record.

This module is deliberately NOT imported by bot runtime. It requires an
explicit maintainer opt-in and a GitHub token supplied only to the isolated
publisher process. It never accepts raw chat logs.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote, urlsplit

REPO = "Treninem/Bot-Knowledge"
API = "https://api.github.com"
RAW_KEYS = {"chat_id","user_id","telegram_id","username","first_name","last_name","phone","email",
            "password","cookie","token","raw_message","raw_chat","chat_history","private_quote"}
PII = (
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"(?<!\d)(?:\+?\d[\s().-]*){10,}(?!\d)"),
    re.compile(r"\b(?:token|password|secret|api[_-]?key)\s*[:=]", re.I),
    re.compile(r"(?<![\w@])@[A-Za-z][A-Za-z0-9_]{4,31}\b"),
    re.compile(r"\b(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me|telegram\.dog)/[^\s\"']+", re.I),
    re.compile(r"\btg://(?:resolve|user|privatepost|join)\b[^\s\"']*", re.I),
)
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}\Z")
QA_AUDIENCES = frozenset({"all_ai_bots", "community_bots", "chat_moderators", "impuls"})
QA_CONTEXTS = frozenset({"direct", "private", "group_addressed"})
QA_LANGUAGES = frozenset({"ru", "en", "multilingual"})
QA_CONSTRAINTS = {"read_only": True, "requires_direct_address": True, "no_personal_data": True}


class PublishError(RuntimeError):
    pass


def _api(path: str, *, token: str, method: str = "GET", data: dict | None = None, accept: str = "application/vnd.github+json") -> dict:
    body = None if data is None else json.dumps(data).encode()
    request = urllib.request.Request(
        API + path, data=body, method=method,
        headers={
            "Authorization": "Bearer " + token,
            "Accept": accept,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Bot-Knowledge-Trusted-Publisher/1.0",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = response.read(8 * 1024 * 1024)
    except urllib.error.HTTPError as exc:
        detail = exc.read(2000).decode("utf-8", "replace")
        raise PublishError(f"GitHub HTTP {exc.code}: {detail}") from exc
    value = json.loads(payload.decode("utf-8")) if payload else {}
    if not isinstance(value, dict):
        raise PublishError("unexpected GitHub response")
    return value


def _contents(path: str, *, token: str, ref: str) -> tuple[dict, bytes]:
    value = _api(f"/repos/{REPO}/contents/{quote(path)}?ref={quote(ref)}", token=token)
    raw = base64.b64decode(value.get("content", ""), validate=False)
    return value, raw


def _safe_text(value: object, limit: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise PublishError("invalid text")
    text = value.strip()
    if any(pattern.search(text) for pattern in PII):
        raise PublishError("potential personal data or secret")
    return text


def _scope_list(value: object, allowed: frozenset[str], maximum: int, field: str) -> list[str]:
    if (not isinstance(value, list) or not 1 <= len(value) <= maximum
            or any(not isinstance(item, str) or item not in allowed for item in value)
            or len(set(value)) != len(value)):
        raise PublishError(f"invalid {field}")
    return list(value)


def _safe_constraints(value: object) -> dict[str, bool]:
    if (not isinstance(value, dict) or set(value) != set(QA_CONSTRAINTS)
            or any(type(value[key]) is not bool or value[key] is not expected
                   for key, expected in QA_CONSTRAINTS.items())):
        raise PublishError("invalid constraints")
    return dict(QA_CONSTRAINTS)


def validate_payload(data: dict) -> tuple[str, dict, str]:
    if not isinstance(data, dict) or set(data) != {"section_path","record","source","origin","reviewed","knowledge_version"}:
        raise PublishError("candidate fields must be section_path, record, source, origin, reviewed, knowledge_version")
    if data["reviewed"] is not True or data["origin"] not in {"synthetic","approved_aggregate","verified_source"}:
        raise PublishError("candidate must be reviewed and have an allowed origin")
    path = data["section_path"]
    if not isinstance(path, str) or not re.fullmatch(r"packs/[A-Za-z0-9._/-]+\.json", path) or ".." in path:
        raise PublishError("unsafe section path")
    version = data["knowledge_version"]
    if not isinstance(version, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,62}", version):
        raise PublishError("invalid knowledge_version")
    source = _safe_text(data["source"], 500)
    parsed = urlsplit(source)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise PublishError("source must be public HTTPS")
    record = data["record"]
    if not isinstance(record, dict) or set(record) - {"id","question","aliases","answer","variants","source","audiences","contexts","language","constraints"}:
        raise PublishError("unsupported qa.v1 record fields")
    rid = record.get("id")
    if not isinstance(rid, str) or not ID.fullmatch(rid):
        raise PublishError("invalid record id")
    normalized = {
        "id": rid,
        "question": _safe_text(record.get("question"), 500),
        "aliases": [_safe_text(x, 500) for x in record.get("aliases", [])],
        "answer": _safe_text(record.get("answer"), 1600),
        "variants": [_safe_text(x, 1600) for x in record.get("variants", [])],
        "source": source,
    }
    if not isinstance(record.get("aliases", []), list) or len(normalized["aliases"]) > 16:
        raise PublishError("invalid aliases")
    if not isinstance(record.get("variants", []), list) or len(normalized["variants"]) > 8:
        raise PublishError("invalid variants")
    if "audiences" in record:
        normalized["audiences"] = _scope_list(record["audiences"], QA_AUDIENCES, 12, "audiences")
    if "contexts" in record:
        normalized["contexts"] = _scope_list(record["contexts"], QA_CONTEXTS, 3, "contexts")
    if "language" in record:
        if not isinstance(record["language"], str) or record["language"] not in QA_LANGUAGES:
            raise PublishError("invalid language")
        normalized["language"] = record["language"]
    if "constraints" in record:
        normalized["constraints"] = _safe_constraints(record["constraints"])
    raw = json.dumps(normalized, ensure_ascii=False).casefold()
    if any(pattern.search(raw) for pattern in PII):
        raise PublishError("potential personal data or secret")
    if any(key in raw for key in RAW_KEYS):
        raise PublishError("raw/private metadata marker detected")
    return path, normalized, version


def _normalized_question(text: str) -> str:
    return " ".join(re.findall(r"[a-zа-яё0-9]+", text.casefold().replace("ё","е")))


def prepare_changes(candidate: dict, *, token: str, base: str) -> tuple[str, str, str, str]:
    path, record, version = validate_payload(candidate)
    pack_meta, pack_raw = _contents(path, token=token, ref=base)
    manifest_meta, manifest_raw = _contents("manifest.json", token=token, ref=base)
    pack = json.loads(pack_raw.decode("utf-8"))
    manifest = json.loads(manifest_raw.decode("utf-8"))
    catalog = pack.get("catalog", {})
    if not isinstance(catalog, dict):
        raise PublishError("invalid target catalog")
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("packs"), list):
        raise PublishError("unsupported manifest")
    target_entries = [row for row in manifest["packs"] if isinstance(row, dict) and row.get("path") == path]
    if len(target_entries) != 1:
        raise PublishError("target package must already be registered exactly once")
    if target_entries[0].get("sha256") != hashlib.sha256(pack_raw).hexdigest():
        raise PublishError("target package SHA-256 differs from manifest")
    declared = target_entries[0].get("catalog")
    if declared is not None and declared != catalog:
        raise PublishError("target catalog metadata conflicts with manifest")
    rows_name = catalog.get("records", "records")
    if catalog.get("adapter") != "qa.v1" or pack.get("schema_version") != 1 or not isinstance(pack.get(rows_name), list):
        raise PublishError("target is not a supported qa.v1 package")
    section_audiences = _scope_list(catalog.get("audiences", ["all_ai_bots"]), QA_AUDIENCES, 12, "target audiences")
    section_contexts = _scope_list(catalog.get("contexts", ["direct"]), QA_CONTEXTS, 3, "target contexts")
    section_language = catalog.get("language")
    if not isinstance(section_language, str) or section_language not in QA_LANGUAGES:
        raise PublishError("invalid target language")
    _safe_constraints(catalog.get("constraints"))
    if (set(record.get("audiences", section_audiences)) - set(section_audiences)
            or set(record.get("contexts", section_contexts)) - set(section_contexts)):
        raise PublishError("record scope exceeds target catalog")
    if section_language != "multilingual" and record.get("language", section_language) != section_language:
        raise PublishError("record language differs from target catalog")
    rows = pack[rows_name]
    qkey = _normalized_question(record["question"])
    if any(row.get("id") == record["id"] for row in rows):
        raise PublishError("duplicate record id")
    if any(_normalized_question(str(row.get("question",""))) == qkey for row in rows):
        raise PublishError("duplicate canonical question")
    # Same source/question aliases with a different answer need human resolution,
    # not an automatic overwrite.
    aliases = {_normalized_question(x) for x in [record["question"], *record["aliases"]]}
    for row in rows:
        existing = {_normalized_question(x) for x in [str(row.get("question","")), *row.get("aliases", [])]}
        if aliases & existing and str(row.get("answer","")).strip() != record["answer"]:
            raise PublishError("possible contradiction; keep as candidate for manual resolution")
    rows.append(record)
    pack["pack_version"] = version
    pack_bytes = (json.dumps(pack, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    digest = hashlib.sha256(pack_bytes).hexdigest()
    target_entries[0]["sha256"] = digest
    manifest["knowledge_version"] = version
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return path, pack_bytes.decode(), manifest_bytes.decode(), pack_meta["sha"] + ":" + manifest_meta["sha"]


def _put(path: str, content: str, *, token: str, branch: str, sha: str, message: str) -> str:
    value = _api(
        f"/repos/{REPO}/contents/{quote(path)}", token=token, method="PUT",
        data={"message": message, "content": base64.b64encode(content.encode()).decode(), "branch": branch, "sha": sha},
    )
    return value["commit"]["sha"]


def _checks_state(sha: str, *, token: str) -> str:
    checks = _api(f"/repos/{REPO}/commits/{sha}/check-runs?per_page=100", token=token, accept="application/vnd.github+json")
    rows = checks.get("check_runs", [])
    required = [row for row in rows if row.get("name") == "validate"]
    if not required:
        return "pending"
    if any(row.get("status") == "completed" and row.get("conclusion") not in {"success", "neutral", "skipped"} for row in rows):
        return "failed"
    if any(row.get("status") != "completed" for row in rows):
        return "pending"
    return "green" if all(row.get("conclusion") == "success" for row in required) else "failed"


def wait_for_reviewed_checks(sha: str, *, token: str, base: str, base_sha: str, timeout_seconds: int = 1200,
                             interval_seconds: int = 20) -> None:
    """Wait for the PR's exact head; never approve a run against a moved base."""
    deadline = time.monotonic() + timeout_seconds
    while True:
        current_base = _api(f"/repos/{REPO}/git/ref/heads/{quote(base)}", token=token)["object"]["sha"]
        if current_base != base_sha:
            raise PublishError("base main moved; rebase and rerun exact-head checks")
        state = _checks_state(sha, token=token)
        if state == "failed":
            raise PublishError("PR opened, but exact-head checks failed")
        if state == "green":
            return
        if time.monotonic() >= deadline:
            raise PublishError("PR opened, but exact-head checks are not green before timeout")
        time.sleep(min(interval_seconds, max(0, deadline - time.monotonic())))


def publish(candidate: dict, *, token: str, base: str, branch: str, skip_ci: bool, merge_if_green: bool, report_path: Path | None = None) -> str:
    if os.getenv("BK_TRUSTED_PUBLISHER") != "1":
        raise PublishError("set BK_TRUSTED_PUBLISHER=1 only in isolated maintainer environment")
    if os.getenv("BOT_TOKEN") or os.getenv("IMPULS_BOT_TOKEN"):
        raise PublishError("refusing to run beside bot runtime credentials")
    if merge_if_green and skip_ci:
        raise PublishError("cannot auto-merge when CI was deliberately skipped")
    path, pack_text, manifest_text, shas = prepare_changes(candidate, token=token, base=base)
    pack_sha, manifest_sha = shas.split(":")
    base_ref = _api(f"/repos/{REPO}/git/ref/heads/{quote(base)}", token=token)
    base_sha = base_ref["object"]["sha"]
    _api(f"/repos/{REPO}/git/refs", token=token, method="POST", data={"ref":"refs/heads/"+branch,"sha":base_sha})
    suffix = " [skip ci]" if skip_ci else ""
    head = _put(path, pack_text, token=token, branch=branch, sha=pack_sha, message="knowledge: publish reviewed qa.v1 record"+suffix)
    # Fetch manifest SHA again from branch after the first commit; file content
    # is unchanged, but this avoids a stale API precondition.
    mm, _ = _contents("manifest.json", token=token, ref=branch)
    head = _put("manifest.json", manifest_text, token=token, branch=branch, sha=mm["sha"], message="manifest: pin reviewed knowledge"+suffix)
    pr = _api(f"/repos/{REPO}/pulls", token=token, method="POST", data={
        "title": f"Knowledge: {candidate['record']['id']}",
        "head": branch, "base": base, "draft": not merge_if_green,
        "body": "Reviewed qa.v1 publication candidate. Source and privacy were validated locally; exact-head checks remain authoritative.",
    })
    if merge_if_green:
        # Preserve the existing trusted --merge-if-green entry point, but use
        # one stronger completion gate with an exact-head workflow, append-only
        # digest checks, guarded merge and a separate post-main CI receipt.
        try:
            from scripts.complete_trusted_qa_pr import FinalizeError, finalize
        except ModuleNotFoundError:
            from complete_trusted_qa_pr import FinalizeError, finalize
        report = {"pr": pr["number"], "head_sha": head, "repository": REPO, "merged": False}
        failure = None
        try:
            finalize(number=pr["number"], expected_head=head, token=token, base=base,
                     merge=True, ready=False, timeout=1200, post_timeout=1200,
                     interval=15, report=report)
        except (FinalizeError, OSError, ValueError, KeyError, TypeError) as exc:
            failure = str(exc)
            report["reason"] = failure
            report["status"] = "merged_post_main_unconfirmed" if report.get("merged") else "blocked"
        finally:
            destination = report_path or Path("trusted_qa_publish_report.json")
            destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if failure:
            raise PublishError(f"PR {pr['html_url']} retained; trusted completion: {failure}")
    return pr["html_url"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--base", default="main")
    parser.add_argument("--branch", required=True)
    parser.add_argument("--skip-ci", action="store_true")
    parser.add_argument("--merge-if-green", action="store_true")
    parser.add_argument("--report", type=Path, default=Path("trusted_qa_publish_report.json"))
    args = parser.parse_args()
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required only in trusted publisher environment")
    candidate = json.loads(args.input.read_text(encoding="utf-8"))
    print(publish(candidate, token=token, base=args.base, branch=args.branch, skip_ci=args.skip_ci, merge_if_green=args.merge_if_green, report_path=args.report))


if __name__ == "__main__":
    main()
