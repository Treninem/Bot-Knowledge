"""T72: 28 independent universal QA cases; three context-appropriate replies each."""
import hashlib
import json
import re
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question, validate_qa_pack
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/dialogue_help_qa.json"
PREFIX="dlg_t72_"
EXPECTED=28
def main():
    raw=(ROOT/REL).read_bytes()
    assert len(raw)<1024*1024
    manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(x["sha256"] for x in manifest["packs"] if x["path"]==REL)
    pack=json.loads(raw)
    records=pack["records"]
    assert len(records)>=749
    assert validate_qa_pack(pack)==len(records)
    current=[r for r in records if r["id"].startswith(PREFIX)]
    assert len(current)==EXPECTED
    assert len(set(r["id"] for r in records))==len(records)
    names=[normalize_question(x) for r in records for x in [r["question"],*r["aliases"]]]
    assert len(names)==len(set(names))
    search=KnowledgeSearch()
    for r in current:
        assert r["audiences"]==["all_ai_bots"]
        assert r["contexts"]==["direct","private","group_addressed"]
        assert r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True}
        assert r["language"]=="ru" and len(r["aliases"])==2 and len(r["variants"])==2
        assert len(set(map(normalize_question,[r["answer"],*r["variants"]])))==3
        assert "REQUIREMENTS_21.md" in r["source"]
        assert not re.search(r"(?i)@[a-z0-9_]+|\\b\\d{10,}\\b|(?:token|password|secret)\\s*[:=]",json.dumps({k:v for k,v in r.items() if k!="source"},ensure_ascii=False))
        assert not any(k in r for k in ("sanction","action","auto_apply","execute","ban","mute"))
        for phrase in [r["question"],*r["aliases"]]:
            hits=search.search(phrase,audience="all_ai_bots",limit=20)
            assert any(h[0]==r["id"] for h in hits),(r["id"],phrase)
    print(f"T72_QA_OK records=28 answers=84 base=721 total={len(records)}")
if __name__=="__main__":
    main()
