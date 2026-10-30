"""Deterministic data-contract tests. This does NOT evaluate an LLM or deploy bot behavior."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_AUDIENCES = {"all_ai_bots", "chat_moderators", "community_bots"}
ALLOWED_DECISIONS = {"answer", "clarify", "abstain", "human_review", "refuse_claim"}
TOPICS = {"context_links", "evidence_calibration", "tool_execution", "privacy_boundaries",
          "initiative_and_tone", "moderation_semantics", "permissions", "error_recovery",
          "multi_intent", "report_verifiability"}

def main() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    path = ROOT / "packs/ru/context_cases.json"
    payload = path.read_bytes()
    expected = next(p["sha256"] for p in manifest["packs"] if p["path"] == "packs/ru/context_cases.json")
    assert hashlib.sha256(payload).hexdigest() == expected, "checksum mismatch"
    data = json.loads(payload.decode("utf-8"))
    assert data["schema_version"] == 1 and data["language"] == "ru"
    policy = data["usage_policy"]
    assert policy == {
        "synthetic_examples_only": True,
        "personal_data_allowed": False,
        "automatic_sanctions_allowed": False,
        "runtime_activation_requires_consumer_tests": True,
        "local_policy_has_priority": True,
    }
    cases = data["cases"]
    assert len(cases) == 80
    assert set(data["decisions"]) == ALLOWED_DECISIONS
    assert Counter(x["category"] for x in cases) == {topic: 8 for topic in TOPICS}
    ids = set()
    messages = set()
    for case in cases:
        assert set(case) == {"id","category","audiences","context","input","decision","expected_behavior","forbidden_behavior"}
        assert case["id"] not in ids
        ids.add(case["id"])
        msg = " ".join(case["input"].lower().split())
        assert msg not in messages, case["id"]
        messages.add(msg)
        assert case["decision"] in ALLOWED_DECISIONS
        assert case["category"] in TOPICS
        assert case["audiences"] and set(case["audiences"]) <= ALLOWED_AUDIENCES
        if case["category"] == "moderation_semantics":
            assert case["audiences"] == ["chat_moderators"]
            assert case["decision"] == "human_review"
        if case["category"] == "permissions":
            assert "all_ai_bots" not in case["audiences"]
        for name in ("context","input","expected_behavior","forbidden_behavior"):
            assert isinstance(case[name], str) and 4 <= len(case[name]) <= 300
        assert len(case["id"]) <= 75 and case["id"].isascii()
        for forbidden in ("http://", "https://", "@", "token=", "password="):
            assert forbidden not in " ".join((case["context"],case["input"])), case["id"]
    assert any(c["decision"] == "abstain" for c in cases)
    assert any(c["decision"] == "refuse_claim" for c in cases)
    for i in range(1,11):
        for case in cases:
            assert case["expected_behavior"] != case["forbidden_behavior"]
        print(f"CONTEXT_CASES_PASS {i}/10 cases={len(cases)} unique={len(messages)}",flush=True)
    print("CONTEXT_CASES_10_ROUNDS_OK",flush=True)

if __name__ == "__main__":
    main()
