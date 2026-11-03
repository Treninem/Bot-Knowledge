"""N13: original English dialogue contextual intent, SHA and indexed retrieval."""
import hashlib
import json
import re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=json.loads((ROOT/"manifest.json").read_text("utf-8"))

def main():
    rel="packs/ru/english_dialogues.json"
    raw=(ROOT/rel).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==next(e["sha256"] for e in MANIFEST["packs"] if e["path"]==rel)
    assert len(raw)<2*1024*1024
    records=json.loads(raw)["cases"]
    selected=[r for r in records if r["id"].startswith("en_n13_")]
    assert len(selected)==49,len(selected)
    assert len({r["id"] for r in records})==len(records)
    assert len({normalize_question(r["input"]) for r in records})==len(records)
    assert len({normalize_question(r["response"]) for r in records})==len(records)
    lookup=KnowledgeSearch()
    for r in selected:
        assert r["language"]=="en" and r["audiences"]==["all_ai_bots"]
        assert r["meaning_ru"] and r["avoid"]
        assert r["kind"] in {"conversation","slang","sarcasm","support","context","rules","deception","creative"}
        assert not re.search(r"(?i)https?://|@\\w+|\\b\\d{10,}\\b",json.dumps(r,ensure_ascii=False))
        hits=lookup.search(r["input"],audience="all_ai_bots",limit=20)
        assert any(x[0]==r["id"] for x in hits),(r["id"],r["input"])
    print(f"N13_EN_OK accepted={len(selected)} total={len(records)}")

if __name__=="__main__":
    main()
