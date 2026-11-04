"""T92 English nuance: versioned SHA, intent/response uniqueness and indexed search."""
import json, hashlib
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/english_conversation_nuance_qa.json"
def main():
    manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    data=(ROOT/REL).read_bytes()
    assert hashlib.sha256(data).hexdigest()==next(p["sha256"] for p in manifest["packs"] if p["path"]==REL)
    assert len(data)<1024*1024
    rows=json.loads(data)["records"]
    assert len(rows)==87 and validate_qa_pack(json.loads(data))==87
    assert [r["id"] for r in rows[-25:]]==[f"en_nuance_t92_{n:03d}" for n in range(1,26)]
    seen_q=set();seen_a=set()
    for entry in manifest["packs"]:
        p=json.loads((ROOT/entry["path"]).read_text("utf-8"))
        if p.get("catalog",{}).get("adapter")!="qa.v1":continue
        for r in p["records"]:
            for q in [r["question"],*r.get("aliases",[])]:
                n=normalize_question(q)
                assert n not in seen_q,("duplicate_query",n)
                seen_q.add(n)
            if entry["path"]==REL:
                for a in [r["answer"],*r["variants"]]:
                    n=normalize_question(a);assert n not in seen_a,("duplicate_answer",n);seen_a.add(n)
    index=KnowledgeSearch()
    for r in rows[-25::5]:
        assert r["audiences"]==["all_ai_bots"] and r["language"]=="en"
        assert r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True}
        assert len(r["aliases"])==len(r["variants"])==2
        assert any(x[0]==r["id"] for x in index.search(r["question"],audience="all_ai_bots",limit=20)),r["id"]
    print("T92 PASS: 25 English pragmatic intents, 50 aliases, 75 context-bound replies")
if __name__=="__main__":main()
