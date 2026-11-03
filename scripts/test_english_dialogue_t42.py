"""T42: 28 distinct English conversational senses and safe local retrieval."""
import hashlib
import json
import re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch

ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/english_dialogues.json"
KINDS = ("conversation", "slang", "sarcasm", "rules", "deception", "support", "creative")


def norm(value):
    return " ".join(re.findall(r"[^\W_]+", value.casefold().replace("ё", "е")))


def main():
    raw = (ROOT / REL).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    pack = json.loads(raw)
    assert hashlib.sha256(raw).hexdigest() == next(
        item["sha256"] for item in manifest["packs"] if item["path"] == REL
    )
    assert len(raw) < 2 * 1024 * 1024
    rows = [x for x in pack["cases"] if x["id"].startswith("en_t42_")]
    assert len(rows) == 28
    assert {r["id"] for r in rows} == {f"en_t42_{i:03d}" for i in range(1, 29)}
    assert {kind: sum(x["kind"] == kind for x in rows) for kind in KINDS} == {
        kind: 4 for kind in KINDS
    }
    assert len({x["id"] for x in pack["cases"]}) == len(pack["cases"])
    old = [x for x in pack["cases"] if x not in rows]
    old_input = {norm(x["input"]) for x in old}
    old_response = {norm(x["response"]) for x in old}
    new_input = [norm(x["input"]) for x in rows]
    new_response = [norm(x["response"]) for x in rows]
    assert len(new_input) == len(set(new_input))
    assert len(new_response) == len(set(new_response))
    assert not (old_input & set(new_input))
    assert not (old_response & set(new_response))
    index = KnowledgeSearch()
    for row in rows:
        assert row["language"] == "en"
        assert row["audiences"] == ["all_ai_bots"]
        assert row["meaning_ru"] and row["avoid"]
        assert not re.search(r"@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=]", str(row), re.I)
        assert any(h[0] == row["id"] for h in index.search(
            row["input"], audience="all_ai_bots", limit=20
        )), row["id"]
    print(f"T42_ENGLISH_OK cases={len(rows)} bytes={len(raw)}")


if __name__ == "__main__":
    main()
