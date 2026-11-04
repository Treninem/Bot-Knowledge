"""T77: 42 original qa.v1 records, SHA, scope, duplicates and local lookup."""
import hashlib
import json
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question, validate_qa_pack
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/conversation_precision_qa.json"

def main():
    raw=(ROOT/REL).read_bytes()
    assert len(raw)<1024*1024
    manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(p["sha256"] for p in manifest["packs"] if p["path"]==REL)
    pack=json.loads(raw); rows=pack["records"][:42]
    assert len(pack["records"])>=42 and validate_qa_pack(pack)==len(pack["records"])
    assert len({r["id"] for r in rows})==42
    assert len({normalize_question(q) for r in rows for q in (r["question"],*r["aliases"])})==126
    assert len({normalize_question(a) for r in rows for a in (r["answer"],*r["variants"])})==126
    seen=set()
    for p in manifest["packs"]:
        if p["path"]==REL: continue
        other=json.loads((ROOT/p["path"]).read_text("utf-8"))
        if other.get("catalog",{}).get("adapter")=="qa.v1":
            for r in other.get("records",[]):
                seen.update(normalize_question(q) for q in (r["question"],*r.get("aliases",[])))
    assert not seen.intersection(normalize_question(q) for r in rows for q in (r["question"],*r["aliases"]))
    idx=KnowledgeSearch()
    for r in rows:
        assert r["audiences"]==["all_ai_bots"] and r["contexts"]==["direct","private","group_addressed"]
        assert r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True}
        assert r["language"]=="ru" and len(r["aliases"])==2 and len(r["variants"])==2
        assert not (set(r)&{"action","sanction","auto_apply","execute","ban","mute"})
        hits=idx.search(r["question"],audience="all_ai_bots",limit=20)
        assert any(h[0]==r["id"] for h in hits),r["id"]
    print("T77 PASS: 42 original questions, 84 aliases, 126 responses")

if __name__=="__main__": main()
