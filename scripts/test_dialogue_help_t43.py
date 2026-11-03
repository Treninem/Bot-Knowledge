"""T43: natural language, scoped audience, no duplicate inputs and SHA-256."""
import hashlib
import json
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question, validate_qa_pack

ROOT = Path(__file__).resolve().parents[1]
def main():
    rel = "packs/ru/dialogue_help_qa.json"
    raw = (ROOT / rel).read_bytes()
    pack = json.loads(raw)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == next(x["sha256"] for x in manifest["packs"] if x["path"] == rel)
    assert validate_qa_pack(pack) == len(pack["records"])
    rows = [x for x in pack["records"] if x["id"].startswith("dlg_t43_")]
    assert len(rows) == 30, len(rows)
    assert len({x["id"] for x in rows}) == 30
    seen = set()
    search = KnowledgeSearch()
    checks = 0
    for row in rows:
        assert row["audiences"] == ["all_ai_bots"]
        assert row["contexts"] in (["direct", "private", "group_addressed"], ["group_addressed"])
        assert len(row["aliases"]) == len(row["variants"]) == 2
        assert all(v.strip() for v in [row["answer"], *row["variants"]])
        for phrase in [row["question"], *row["aliases"]]:
            key = normalize_question(phrase)
            assert key not in seen, (row["id"], phrase)
            seen.add(key)
            hits = search.search(phrase, audience="all_ai_bots", limit=5)
            assert hits and hits[0][0] == row["id"], (row["id"], phrase, hits)
            checks += 1
    print(f"T43_OK questions={len(rows)} original_answers={len(rows)*3} queries={checks}")

if __name__ == "__main__":
    main()
