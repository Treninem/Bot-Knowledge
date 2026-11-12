"""T91: ImPULS user help without executable permissions or unverified live claims."""
import hashlib
import json
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question
from scripts.search_knowledge import KnowledgeSearch

ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/impuls_ai_modes_help_qa.json"
def main():
    manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    expected=next(x["sha256"] for x in manifest["packs"] if x["path"]==REL)
    raw=(ROOT/REL).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==expected
    assert len(raw)<1024*1024
    data=json.loads(raw)
    assert len(data["records"])==25 and validate_qa_pack(data)==25
    assert data["catalog"]["audiences"]==["impuls"]
    assert data["catalog"]["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True}
    assert [r["id"] for r in data["records"]]==[f"impuls_t91_{i:03d}" for i in range(1,26)]
    qs=set(); ans=set()
    for entry in manifest["packs"]:
        f=ROOT/entry["path"]
        content=json.loads(f.read_text("utf-8"))
        if content.get("catalog",{}).get("adapter")!="qa.v1":continue
        for r in content["records"]:
            for q in [r["question"],*r.get("aliases",[])]:
                v=normalize_question(q); assert v not in qs,("duplicate_q",v);qs.add(v)
            if entry["path"]==REL:
                assert len(r["aliases"])==len(r["variants"])==2
                assert r["audiences"]==["impuls"] and r["language"]=="ru"
                assert r["contexts"]==["direct","private","group_addressed"]
                assert r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True}
                assert not set(r)&{"action","execute","sanction","ban","mute","auto_apply"}
                for a in [r["answer"],*r["variants"]]:
                    v=normalize_question(a);assert v not in ans,("duplicate_a",v);ans.add(v)
    search=KnowledgeSearch()
    for r in data["records"][::4]:
        hits=search.search(r["question"],audience="impuls",limit=20)
        assert any(h[0]==r["id"] for h in hits),r["id"]
        assert not any(h[0]==r["id"] for h in search.search(r["question"],audience="all_ai_bots",limit=20))
    print("T91 PASS: 25 original ImPULS intents; 50 aliases; 75 context-limited replies")
if __name__=="__main__":main()
