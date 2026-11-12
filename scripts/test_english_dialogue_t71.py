"""T71: original English cases; exact SHA, unique meaning, scoped local search."""
import hashlib
import json
import re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/english_dialogues.json"
PREFIX="en_t71_"
EXPECTED=62
def main():
    raw=(ROOT/REL).read_bytes()
    manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(x["sha256"] for x in manifest["packs"] if x["path"]==REL)
    assert len(raw)<2*1024*1024
    data=json.loads(raw)
    rows=data["cases"]
    new=[r for r in rows if r["id"].startswith(PREFIX)]
    assert len(new)==EXPECTED
    assert len(rows)>=968+EXPECTED
    assert len({r["id"] for r in rows})==len(rows)
    for field in ("input","response"):
        assert len({normalize_question(r[field]) for r in rows})==len(rows),field
    lookup=KnowledgeSearch()
    kinds={"context","conversation","support","slang","sarcasm","rules","deception","creative"}
    assert set(r["kind"] for r in new)==kinds
    for r in new:
        assert r["audiences"]==["all_ai_bots"] and r["language"]=="en"
        assert all(isinstance(r[k],str) and r[k].strip() for k in ("input","response","meaning_ru","avoid"))
        assert not re.search(r"https?://|@[A-Za-z0-9_]+|\\b\\d{10,}\\b|token\\s*[:=]|password\\s*[:=]",json.dumps(r,ensure_ascii=False),re.I)
        assert not any(key in r for key in ("action","sanction","auto_apply","execute","ban","mute"))
        hits=lookup.search(r["input"],audience="all_ai_bots",limit=20)
        assert any(hit[0]==r["id"] for hit in hits),r["id"]
    print("T71_ENGLISH_OK accepted=",len(new),"total=",len(rows))
if __name__=="__main__":
    main()
