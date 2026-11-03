"""Contract tests only: synthetic moderation cases do not issue sanctions or evaluate a live model."""
from collections import Counter
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/moderation_cases.json"
def normalize(value):
    return re.sub(r"[^a-zа-я0-9]+", " ", value.casefold().replace("ё", "е")).strip()

def main():
    raw = (ROOT / REL).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    expected_sha = next(p["sha256"] for p in manifest["packs"] if p["path"] == REL)
    assert hashlib.sha256(raw).hexdigest() == expected_sha
    assert len(raw) < 2 * 1024 * 1024
    data = json.loads(raw)
    assert data["schema_version"] == 1 and data["language"] == "ru"
    policy = data["usage_policy"]
    assert policy == {
        "no_auto_sanctions": True, "required_local_rule": True,
        "required_role_verification": True, "private_chat_memory_prohibited": True,
        "manual_review_on_uncertainty": True,
    }
    cases = data["cases"]
    new = [x for x in cases if x["id"].startswith("mod_t70_")]
    assert len(cases) == 126 and len(new) == 63
    assert len({x["id"] for x in cases}) == 126
    assert len({normalize(x["message"]) for x in cases}) == 126
    assert Counter(x["classification"] for x in new) == {
        "candidate_violation": 21, "allow": 21, "review": 21,
    }
    assert len({x["topic"] for x in new}) == 21
    assert Counter(x["topic"] for x in new) == {x["topic"]:3 for x in new}
    for case in cases:
        assert case["audiences"] == ["chat_moderators"]
        assert case["classification"] in ("candidate_violation", "allow", "review")
        assert case["local_rule"] and case["reason"] and case["required_checks"]
        assert not {"sanction", "action", "auto_apply", "execute"} & case.keys()
        for field in ("message", "reason", "local_rule"):
            assert isinstance(case[field], str) and case[field].strip()
        assert not re.search(r"https?://|@[a-z0-9_]+|token=|password=", case["message"], flags=re.I)
    print("T70_MODERATION_PASS count=126 new=63 topics=21 classes=42/42/42")

if __name__ == "__main__":
    main()
