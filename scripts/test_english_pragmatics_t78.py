"""T78: English pragmatic QA package and cross-pack search integrity."""
import json
import hashlib
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/english_pragmatics_qa.json"

def main():
    raw=(ROOT/REL).read_bytes()
    m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(p["sha256"] for p in m["packs"] if p["path"]==REL)
    assert len(raw)<1024*1024
    rows=json.loads(raw)["records"][:32]
    assert len(json.loads(raw)["records"])>=32 and validate_qa_pack(json.loads(raw))==len(json.loads(raw)["records"])
    q=[normalize_question(x) for r in rows for x in (r["question"],*r["aliases"])]
    a=[normalize_question(x) for r in rows for x in (r["answer"],*r["variants"])]
    assert len(set(q))==96 and len(set(a))==96
    others=set()
    for p in m["packs"]:
        if p["path"]==REL: continue
        data=json.loads((ROOT/p["path"]).read_text("utf-8"))
        if data.get("catalog",{}).get("adapter")=="qa.v1":
            for r in data.get("records",[]): others.update(normalize_question(x) for x in (r["question"],*r.get("aliases",[])))
    assert not others.intersection(q)
    lookup=KnowledgeSearch()
    for r in rows:
        assert r["language"]=="en" and r["audiences"]==["all_ai_bots"]
        assert r["contexts"]==["direct","private","group_addressed"]
        assert r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True}
        assert not (set(r)&{"action","sanction","execute","ban","mute"})
        assert any(x[0]==r["id"] for x in lookup.search(r["question"],audience="all_ai_bots",limit=20)),r["id"]
    print("T78 PASS: 32 English questions, 64 aliases, 96 answers")

if __name__=="__main__": main()
