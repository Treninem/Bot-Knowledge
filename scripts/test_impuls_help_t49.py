"""T49: source-grounded, read-only ImPULS game help and indexed QA."""
import hashlib
import json
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question, validate_qa_pack
ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/impuls_help_qa.json"

def main():
    raw = (ROOT / REL).read_bytes()
    pack = json.loads(raw)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == next(row["sha256"] for row in manifest["packs"] if row["path"] == REL)
    assert len(raw) < 2 * 1024 * 1024
    assert validate_qa_pack(pack) == len(pack["records"])
    rows = [row for row in pack["records"] if row["id"].startswith("help_t49_")]
    assert len(rows) == 24
    assert len({row["id"] for row in rows}) == len(rows)
    normalized = set()
    for row in pack["records"]:
        for phrase in [row["question"], *row.get("aliases", [])]:
            key = normalize_question(phrase)
            assert key not in normalized, (row["id"], phrase)
            normalized.add(key)
    index = KnowledgeSearch()
    count = 0
    for row in rows:
        assert row["audiences"] == ["impuls"]
        assert row["contexts"] == ["direct", "private", "group_addressed"]
        assert row["constraints"] == {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
        assert len(row["aliases"]) == len(row["variants"]) == 2
        assert len({normalize_question(x) for x in [row["answer"], *row["variants"]]}) == 3
        for phrase in [row["question"], *row["aliases"]]:
            hits = index.search(phrase, audience="impuls", limit=5)
            assert hits and hits[0][0] == row["id"], (row["id"], phrase, hits)
            count += 1
            assert not any(x[0] == row["id"] for x in index.search(phrase, audience="all_ai_bots", limit=8))
    print("T49_IMPULS_GAME_HELP_OK questions=24 answers=72 searches="+str(count))

if __name__ == "__main__":
    main()
