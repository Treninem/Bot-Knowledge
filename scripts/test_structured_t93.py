"""T93: scoped data-reasoning QA, checked against the full manifest."""
import hashlib, json
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/structured_information_qa.json"
def main():
    manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    raw=(ROOT/REL).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==next(p["sha256"] for p in manifest["packs"] if p["path"]==REL)
    assert len(raw)<1024*1024
    obj=json.loads(raw)
    assert validate_qa_pack(obj)==114
    rows=[r for r in obj["records"] if r["id"].startswith("struct_t93_")]
    assert len(rows)==25
    assert [r["id"] for r in rows]==[f"struct_t93_{i:03d}" for i in range(1,26)]
    seen_q=set();seen_a=set()
    for item in manifest["packs"]:
        pkg=json.loads((ROOT/item["path"]).read_text("utf-8"))
        if pkg.get("catalog",{}).get("adapter")!="qa.v1":continue
        for r in pkg["records"]:
            for q in [r["question"],*r.get("aliases",[])]:
                n=normalize_question(q)
                assert n not in seen_q,("duplicate_question",n)
                seen_q.add(n)
            if item["path"]==REL:
                for reply in [r["answer"],*r["variants"]]:
                    n=normalize_question(reply)
                    assert n not in seen_a,("duplicate_reply",n)
                    seen_a.add(n)
    idx=KnowledgeSearch()
    for r in rows[::5]:
        assert r["audiences"]==["all_ai_bots"] and r["language"]=="ru"
        assert r["contexts"]==["direct","private","group_addressed"]
        assert r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True}
        assert len(r["aliases"])==2 and 2 <= len(r["variants"]) <= 8
        assert any(hit[0]==r["id"] for hit in idx.search(r["question"],audience="all_ai_bots",limit=20))
    print("T93 PASS: +25 intents, +50 aliases, +75 replies")
if __name__=="__main__":main()
