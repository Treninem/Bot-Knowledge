"""T40: natural synthetic social dialogues, scope, exact SHA and indexed lookup."""
import hashlib
import json
import re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch

ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/social_dialogues.json"
KINDS = ("congratulations", "support", "humor", "profanity", "conversation", "creative")


def norm(value):
    return " ".join(re.findall(r"[^\W_]+", value.casefold().replace("ё", "е")))


def main():
    payload = (ROOT / REL).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    pack = json.loads(payload)
    assert manifest["knowledge_version"] >= "2026.11.03.119"
    assert hashlib.sha256(payload).hexdigest() == next(
        row["sha256"] for row in manifest["packs"] if row["path"] == REL
    )
    assert len(payload) < 2 * 1024 * 1024
    rows = [case for case in pack["cases"] if case["id"].startswith("talk_t40_")]
    assert len(rows) == 48
    assert {row["id"] for row in rows} == {
        f"talk_t40_{i:03d}" for i in range(1, 49)
    }
    assert {kind: sum(row["kind"] == kind for row in rows) for kind in KINDS} == {
        kind: 8 for kind in KINDS
    }
    assert len({case["id"] for case in pack["cases"]}) == len(pack["cases"])
    all_inputs = [norm(case["input"]) for case in pack["cases"]]
    assert len(all_inputs) == len(set(all_inputs))
    old_responses = {norm(case["response"]) for case in pack["cases"] if case not in rows}
    new_responses = [norm(case["response"]) for case in rows]
    assert len(new_responses) == len(set(new_responses))
    assert not (old_responses & set(new_responses))
    search = KnowledgeSearch()
    for row in rows:
        assert row["audiences"] == ["all_ai_bots"]
        assert all(row[key].strip() for key in ("context", "input", "response", "avoid"))
        assert not re.search(r"@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=]", str(row), re.I)
        assert any(hit[0] == row["id"] for hit in search.search(
            row["input"], audience="all_ai_bots", limit=20
        )), row["id"]
    print(f"T40_SOCIAL_OK count={len(rows)} bytes={len(payload)}")


if __name__ == "__main__":
    main()
