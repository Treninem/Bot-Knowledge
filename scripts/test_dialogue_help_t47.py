"""T47: scoped natural conversation QA, schema, SHA and indexed search."""
import hashlib
import json
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question, validate_qa_pack

ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/dialogue_help_qa.json"

def main():
    raw = (ROOT / REL).read_bytes()
    pack = json.loads(raw)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == next(x["sha256"] for x in manifest["packs"] if x["path"] == REL)
    assert len(raw) < 2 * 1024 * 1024
    assert validate_qa_pack(pack) == len(pack["records"])
    rows = [x for x in pack["records"] if x["id"].startswith("dlg_t47_")]
    assert len(rows) == 24
    seen = set()
    for r in pack["records"]:
        for text in [r["question"], *r.get("aliases", [])]:
            n = normalize_question(text)
            assert n not in seen, (r["id"], text)
            seen.add(n)
    search = KnowledgeSearch()
    checked = 0
    for r in rows:
        assert r["audiences"] == ["all_ai_bots"]
        assert r["contexts"] == ["direct", "private", "group_addressed"]
        assert len(r["aliases"]) == len(r["variants"]) == 2
        assert all(x.strip() for x in [r["answer"], *r["variants"]])
        for phrase in [r["question"], *r["aliases"]]:
            hits = search.search(phrase, audience="all_ai_bots", limit=5)
            assert hits and hits[0][0] == r["id"], (r["id"], phrase, hits)
            checked += 1
    print(f"T47_QA_OK questions={len(rows)} answers={len(rows)*3} searches={checked}")

if __name__ == "__main__":
    main()
