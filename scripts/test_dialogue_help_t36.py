"""T36 neutral clarification help in qa.v1: exact SHA, aliases, audience and indexing."""
import hashlib,json,re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import validate_qa_pack,normalize_question
ROOT=Path(__file__).resolve().parents[1]

def main():
    rel="packs/ru/dialogue_help_qa.json"
    payload=(ROOT/rel).read_bytes()
    manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(payload).hexdigest()==next(x["sha256"] for x in manifest["packs"] if x["path"]==rel)
    assert len(payload)<1024*1024
    pack=json.loads(payload)
    assert validate_qa_pack(pack)==len(pack["records"])
    rows=[x for x in pack["records"] if x["id"].startswith("dlg_t36_")]
    assert len(rows)==20
    assert len({x["id"] for x in rows})==len(rows)
    search=KnowledgeSearch()
    for row in rows:
        assert row["audiences"]==["all_ai_bots"]
        assert row["contexts"]==["direct","private","group_addressed"]
        assert len(row["aliases"])==2 and len(row["variants"])==2
        for phr in [row["question"],*row["aliases"]]:
            hits=search.search(phr,audience="all_ai_bots",limit=20)
            assert any(h[0]==row["id"] for h in hits),(row["id"],phr)
        assert not re.search(r"@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=]",str(row),re.I)
    print("T36_UNIVERSAL_QA_OK",len(rows),"aliases",len(rows)*2)

if __name__=="__main__":main()
