"""T14 natural ImPULS help questions: integrity, lookup, and strict audience isolation."""
import hashlib
import json
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question
ROOT=Path(__file__).resolve().parents[1]

def main():
    rel="packs/ru/impuls_help_qa.json"
    content=(ROOT/rel).read_bytes()
    manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    expected=next(x["sha256"] for x in manifest["packs"] if x["path"]==rel)
    assert hashlib.sha256(content).hexdigest()==expected
    assert len(content)<2*1024*1024
    pack=json.loads(content)
    assert validate_qa_pack(pack)==len(pack["records"])
    records=[r for r in pack["records"] if r["id"].startswith("help_t14_")]
    assert len(records)==41
    assert all(r["audiences"]==["impuls"] and r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True} for r in records)
    queries=[q for r in records for q in [r["question"],*r["aliases"]]]
    assert len(set(map(normalize_question,queries)))==123
    search=KnowledgeSearch()
    checked=0
    for record in records:
        for query in [record["question"],*record["aliases"]]:
            hits=search.search(query,audience="impuls",limit=5)
            assert hits and hits[0][0]==record["id"],(record["id"],query,hits)
            hidden=search.search(query,audience="all_ai_bots",limit=10)
            assert all(x[0]!=record["id"] for x in hidden),(record["id"],query)
            checked+=1
    print(f"IMPULS_HELP_T14_PASS records={len(records)} searches={checked}")
if __name__=="__main__":main()
