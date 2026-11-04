"""T84 original English pragmatic cases: manifest, QA, privacy, retrieval."""
from pathlib import Path
import hashlib
import json
from scripts.validate_qa_v1 import normalize_question, validate_qa_pack
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/english_pragmatics_qa.json"
def main():
    raw=(ROOT/REL).read_bytes()
    manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(p["sha256"] for p in manifest["packs"] if p["path"]==REL)
    assert len(raw)<1024*1024
    pack=json.loads(raw); rows=pack["records"]
    assert len(rows)==32+35 and validate_qa_pack(pack)==len(rows)
    assert [x["id"] for x in rows[32:]]==["en_precision_t84_%03d"%i for i in range(1,36)]
    queries=set();answers=set()
    for p in manifest["packs"]:
        data=json.loads((ROOT/p["path"]).read_text("utf-8"))
        if data.get("catalog",{}).get("adapter")!="qa.v1":continue
        for r in data["records"]:
            for q in [r["question"],*r.get("aliases",[])]:
                n=normalize_question(q)
                assert n not in queries,("duplicate_query",n)
                queries.add(n)
            if p["path"]==REL:
                for ans in [r["answer"],*r.get("variants",[])]:
                    n=normalize_question(ans)
                    assert n not in answers,("duplicate_answer",n)
                    answers.add(n)
    idx=KnowledgeSearch()
    for r in rows[32:]:
        assert r["language"]=="en" and r["audiences"]==["all_ai_bots"]
        assert r["contexts"]==["direct","private","group_addressed"]
        assert r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True}
        assert len(r["aliases"])==2 and len(r["variants"])==2
        assert not(set(r)&{"execute","action","sanction","auto_apply","ban","mute"})
        assert any(hit[0]==r["id"] for hit in idx.search(r["question"],audience="all_ai_bots",limit=20)),r["id"]
    print("T84 PASS: 35 new English meanings, 70 aliases and 105 answers")
if __name__=="__main__":main()
