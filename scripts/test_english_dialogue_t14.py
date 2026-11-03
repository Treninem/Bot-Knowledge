"""T14 English social context: SHA, synthetic limits and retrieval check."""
import json,hashlib
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]

def main():
    rel="packs/ru/english_dialogues.json"
    raw=(ROOT/rel).read_bytes()
    manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    expected=next(x["sha256"] for x in manifest["packs"] if x["path"]==rel)
    assert hashlib.sha256(raw).hexdigest()==expected and len(raw)<2*1024*1024
    cases=json.loads(raw)["cases"]
    selected=[v for v in cases if v["id"].startswith("en_t14_")]
    assert len(selected)==32
    assert len({v["input"].casefold() for v in selected})==len(selected)
    assert len({v["response"].casefold() for v in selected})==len(selected)
    assert all(v["language"]=="en" and v["audiences"]==["all_ai_bots"] and v["meaning_ru"] and v["avoid"] for v in selected)
    index=KnowledgeSearch()
    checks=0
    for row in selected:
        hits=index.search(row["input"],audience="all_ai_bots",limit=20)
        assert any(h[0]==row["id"] for h in hits),(row["id"],hits)
        checks+=1
    print(f"ENGLISH_T14_OK cases={len(selected)} searches={checks}")
if __name__=="__main__":main()
