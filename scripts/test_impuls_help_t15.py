"""T15: natural ImPULS feature comparisons, exact-head data SHA and audience isolation."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question
ROOT=Path(__file__).resolve().parents[1]

def main():
    rel="packs/ru/impuls_help_qa.json"
    raw=(ROOT/rel).read_bytes()
    manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    expected=next(x["sha256"] for x in manifest["packs"] if x["path"]==rel)
    assert hashlib.sha256(raw).hexdigest()==expected
    assert len(raw)<2*1024*1024
    pack=json.loads(raw)
    assert validate_qa_pack(pack)==len(pack["records"])
    rows=[r for r in pack["records"] if r["id"].startswith("help_t15_")]
    assert len(rows)==29, len(rows)
    # T15 contributes 29 stable records; later independent batches may extend the pack.
    assert len(pack["records"])>=607, len(pack["records"])
    phrases=[q for r in rows for q in [r["question"], *r["aliases"]]]
    assert len(phrases)==87
    assert len(set(map(normalize_question, phrases)))==87
    search=KnowledgeSearch()
    for r in rows:
        assert r["audiences"]==["impuls"]
        assert r["contexts"]==["direct","private","group_addressed"]
        assert r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True}
        assert len(r["aliases"])==len(r["variants"])==2
        for phrase in [r["question"], *r["aliases"]]:
            hits=search.search(phrase,audience="impuls",limit=5)
            assert hits and hits[0][0]==r["id"], (r["id"],phrase,hits)
            hidden=search.search(phrase,audience="all_ai_bots",limit=10)
            assert all(hit[0]!=r["id"] for hit in hidden),(r["id"],phrase,hidden)
    print(f"IMPULS_HELP_T15_PASS records={len(rows)} answers={len(rows)*3} indexed_queries={len(phrases)}")

if __name__=="__main__":main()
