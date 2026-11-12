"""T65: original general conversation/help QA, manifest SHA and scoped retrieval."""
import hashlib, json
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question, validate_qa_pack
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/dialogue_help_qa.json"
PREFIX="dlg_t65_"
COUNT=48

def main():
    raw=(ROOT/REL).read_bytes()
    manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    assert len(raw)<1024*1024
    assert hashlib.sha256(raw).hexdigest()==next(x["sha256"] for x in manifest["packs"] if x["path"]==REL)
    data=json.loads(raw)
    assert validate_qa_pack(data)==len(data["records"])
    added=[r for r in data["records"] if r["id"].startswith(PREFIX)]
    assert len(added)==COUNT
    seen=set()
    lookup=KnowledgeSearch()
    for r in data["records"]:
        for phrase in [r["question"],*r.get("aliases",[])]:
            key=normalize_question(phrase)
            assert key not in seen,(r["id"],phrase)
            seen.add(key)
    for r in added:
        assert r["audiences"]==["all_ai_bots"]
        assert r["contexts"]==["direct","private","group_addressed"]
        assert r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True}
        assert r["language"]=="ru" and len(r["variants"])==2 and len(r["aliases"])==2
        assert len(set([r["answer"],*r["variants"]]))==3
        assert r["source"]=="https://github.com/Treninem/Bot-Knowledge/blob/0e1123d161bc6e5230591c940428484064b32b4c/docs/REQUIREMENTS_21.md"
        assert not any(k in r for k in ("action","auto_apply","sanction","ban","mute","execute"))
        for phrase in [r["question"],*r["aliases"]]:
            matches=lookup.search(phrase,audience="all_ai_bots",limit=20)
            assert any(m[0]==r["id"] for m in matches),(r["id"],phrase)
    print(f"T65_OK records={len(added)} answers={3*len(added)} queries={3*len(added)}")
if __name__=="__main__":
    main()
