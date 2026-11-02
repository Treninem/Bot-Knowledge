"""Offline, no-network safety tests for trusted reviewed qa.v1 completion."""
from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

try:
    from scripts import complete_trusted_qa_pr as finalizer
except ModuleNotFoundError:
    import complete_trusted_qa_pr as finalizer


HEAD = "a" * 40
BASE = "b" * 40


def pr(draft=False):
    return {
        "number": 123, "state": "open", "draft": draft, "node_id": "PR_123",
        "head": {"sha": HEAD, "ref": "trusted/qa-123", "repo": {"full_name": finalizer.REPO}},
        "base": {"ref": "main", "sha": BASE},
        "body": "Reviewed qa.v1 publication candidate. Source and privacy were validated locally.",
        "mergeable": True,
    }


def run(path, name, *, head=HEAD, conclusion="success", status="completed", event="pull_request"):
    return {"id": 99, "path": path, "name": name, "head_sha": head,
            "head_branch": "trusted/qa-123", "event": event,
            "status": status, "conclusion": conclusion, "created_at": "2026-11-02T00:00:00Z"}


class GuardTests(unittest.TestCase):
    def test_guard_accepts_pinned_publisher_pr(self):
        self.assertEqual(finalizer.guard_pr(pr(), number=123, expected_head=HEAD, base="main"), BASE)

    def test_legacy_or_other_pr_refused(self):
        for mutation in (
            lambda p: p["head"].update(sha="c" * 40),
            lambda p: p["head"]["repo"].update(full_name="someone/other"),
            lambda p: p.update(body="Some unrelated PR"),
            lambda p: p["base"].update(ref="develop"),
            lambda p: p.update(state="closed"),
        ):
            value = pr()
            mutation(value)
            with self.subTest(value=value), self.assertRaises(finalizer.FinalizeError):
                finalizer.guard_pr(value, number=123, expected_head=HEAD, base="main")

    def test_exact_head_run_cannot_be_replaced_by_merge_ref(self):
        merge_run = run(*finalizer.EXACT, head="c" * 40)
        self.assertIsNone(finalizer.choose_run([merge_run], HEAD, "trusted/qa-123", finalizer.EXACT))
        good = run(*finalizer.EXACT)
        self.assertEqual(finalizer.choose_run([merge_run, good], HEAD, "trusted/qa-123", finalizer.EXACT), good)

    def test_wrong_branch_or_workflow_refused(self):
        fake = run(".github/workflows/other.yml", "Trusted qa.v1 publisher exact-head")
        self.assertIsNone(finalizer.choose_run([fake], HEAD, "trusted/qa-123", finalizer.EXACT))

    def test_unfinished_ci_times_out_not_green(self):
        with patch.object(finalizer, "request", return_value={"workflow_runs": [run(*finalizer.EXACT)]}):
            with self.assertRaisesRegex(finalizer.FinalizeError, "not completed"):
                finalizer.wait_ci(HEAD, "trusted/qa-123", token="fixture", timeout=0, interval=1)

    def test_failed_ci_does_not_fall_back_to_old_success(self):
        failure = run(*finalizer.EXACT, conclusion="failure")
        failure["id"] = 101
        prior = run(*finalizer.EXACT)
        prior["id"] = 100
        quality = run(*finalizer.QUALITY)
        with patch.object(finalizer, "request", return_value={"workflow_runs": [prior, quality, failure]}):
            with self.assertRaisesRegex(finalizer.FinalizeError, "failed"):
                finalizer.wait_ci(HEAD, "trusted/qa-123", token="fixture", timeout=0, interval=1)

    def test_both_exact_and_quality_required(self):
        a, b = run(*finalizer.EXACT), run(*finalizer.QUALITY)
        with patch.object(finalizer, "request", return_value={"workflow_runs": [a, b]}):
            result = finalizer.wait_ci(HEAD, "trusted/qa-123", token="fixture", timeout=0, interval=1)
        self.assertEqual(result["exact_head"]["conclusion"], "success")
        self.assertEqual(result["quality"]["conclusion"], "success")

    def test_append_only_manifest_integrity_and_cache_version(self):
        import hashlib
        import json
        pack_path = "packs/ru/knowledge_format.json"
        old_pack = {"schema_version": 1, "pack_version": "2026.11.02.1",
                    "catalog": {"adapter": "qa.v1", "records": "records"},
                    "records": [{"id": "existing", "question": "First?", "answer": "First."}]}
        new_pack = copy.deepcopy(old_pack)
        new_pack["pack_version"] = "2026.11.02.2"
        new_pack["records"].append({"id": "next", "question": "Next?", "answer": "Next.",
                                    "source": "https://github.com/Treninem/Bot-Knowledge"})
        raw = (json.dumps(new_pack, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        digest = hashlib.sha256(raw).hexdigest()
        before = {"schema_version": 1, "knowledge_version": "2026.11.02.1",
                  "packs": [{"path": pack_path, "sha256": "old-digest"},
                            {"path": "packs/ru/intents.json", "sha256": "unchanged"}]}
        after = copy.deepcopy(before)
        after["knowledge_version"] = "2026.11.02.2"
        after["packs"][0]["sha256"] = digest
        contents = {
            ("manifest.json", BASE): (before, b""),
            ("manifest.json", HEAD): (after, b""),
            (pack_path, BASE): (old_pack, b""),
            (pack_path, HEAD): (new_pack, raw),
        }
        file_rows = [{"filename": "manifest.json", "status": "modified"},
                     {"filename": pack_path, "status": "modified"}]
        def fake_content(path, *, token, ref):
            return contents[path, ref]
        with patch.object(finalizer, "request", return_value=file_rows):
            with patch.object(finalizer, "content", side_effect=fake_content):
                with patch.object(finalizer, "validate_qa_pack", return_value=2):
                    good = finalizer.verify_append_only(123, token="fixture", base_sha=BASE, head_sha=HEAD)
                    self.assertEqual(good["pack_sha256"], digest)
                    self.assertEqual(good["added_records"], 1)
                    after["knowledge_version"] = before["knowledge_version"]
                    with self.assertRaisesRegex(finalizer.FinalizeError, "knowledge_version"):
                        finalizer.verify_append_only(123, token="fixture", base_sha=BASE, head_sha=HEAD)
                    after["knowledge_version"] = "2026.11.02.2"
                    after["packs"][0]["sha256"] = "0" * 64
                    with self.assertRaisesRegex(finalizer.FinalizeError, "SHA-256"):
                        finalizer.verify_append_only(123, token="fixture", base_sha=BASE, head_sha=HEAD)
                    after["packs"][0]["sha256"] = digest
                    new_pack["catalog"]["audiences"] = ["all_ai_bots"]
                    with self.assertRaisesRegex(finalizer.FinalizeError, "catalog permissions"):
                        finalizer.verify_append_only(123, token="fixture", base_sha=BASE, head_sha=HEAD)

    def test_post_main_push_status_must_match_exact_merge_sha(self):
        post = run(*finalizer.QUALITY, head=HEAD, event="push")
        post["head_branch"] = "main"
        merge_ref = run(*finalizer.QUALITY, head="b" * 40, event="push")
        with patch.object(finalizer, "request", return_value={"workflow_runs": [merge_ref, post]}):
            result = finalizer.wait_ci(HEAD, "main", token="fixture", timeout=0,
                                       interval=1, post_main=True)
        self.assertEqual(result["post_main_quality"]["head_sha"], HEAD)

    def test_untrusted_environment_and_bot_credentials_refused(self):
        with patch.dict("os.environ", {"BK_TRUSTED_PUBLISHER": "1", "IMPULS_BOT_TOKEN": "local-bot"}, clear=True):
            with self.assertRaises(finalizer.FinalizeError):
                finalizer.trusted_environment("fixture")
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(finalizer.FinalizeError):
                finalizer.trusted_environment("fixture")

    def test_no_merge_when_main_moves(self):
        calls = []
        main_lookups = 0
        def fetch(path, **kwargs):
            nonlocal main_lookups
            calls.append(path)
            if path.endswith("/pulls/123"):
                return pr()
            if path.endswith("/git/ref/heads/main"):
                main_lookups += 1
                return {"object": {"sha": BASE if main_lookups == 1 else "c" * 40}}
            raise AssertionError("unexpected network operation: " + path)
        with patch.dict("os.environ", {"BK_TRUSTED_PUBLISHER": "1"}, clear=True):
            with patch.object(finalizer, "request", side_effect=fetch):
                with patch.object(finalizer, "verify_append_only", return_value={"path": "packs/ru/knowledge_format.json"}):
                    with patch.object(finalizer, "wait_ci", return_value={"exact_head": {"conclusion": "success"}}):
                        with self.assertRaisesRegex(finalizer.FinalizeError, "main advanced"):
                            finalizer.finalize(number=123, expected_head=HEAD, token="fixture", base="main", merge=True,
                                               ready=False, timeout=0, post_timeout=0, interval=1, report={})
        self.assertFalse(any("/merge" in path for path in calls))


if __name__ == "__main__":
    unittest.main()
