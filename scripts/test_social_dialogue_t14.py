"""T14 safe natural conversation additions: deduplication, audience, search, hash."""
import json
import hashlib
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/social_dialogues.json"

def main():
    raw=(ROOT/REL).read_bytes()
    pack=json.loads(raw)
    manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    expected=next(v["sha256"] for v in manifest["packs"] if v["path"]==REL)
    assert hashlib.sha256(raw).hexdigest()==expected
    assert len(raw)<2*1024*1024
    rows=[v for v in pack["cases"] if v["id"].startswith("talk_t14_")]
    assert len(rows)==30
    assert len({v["id"] for v in rows})==len(rows)
    assert all(v["audiences"]==["all_ai_bots"] and v["kind"] in {"conversation","support","profanity","humor"} and v["context"] and v["avoid"] for v in rows)
    search=KnowledgeSearch()
    selected=[v for v in rows if len(v["input"].split())>=7]
    matched=0
    for v in selected:
        result=search.search(v["input"],audience="all_ai_bots",limit=20)
        assert any(x[0]==v["id"] for x in result),(v["id"],result)
        matched+=1
    print(f"SOCIAL_T14_OK rows={len(rows)} searches={matched}")
if __name__=="__main__":main()
