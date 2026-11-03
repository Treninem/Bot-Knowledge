"""N11 social-context expansion: exact hash, synthetic scope and local retrieval."""
import hashlib
import json
import re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question

ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/social_dialogues.json"
def main():
    raw=(ROOT/REL).read_bytes()
    m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    assert len(raw)<2*1024*1024
    assert hashlib.sha256(raw).hexdigest()==next(x["sha256"] for x in m["packs"] if x["path"]==REL)
    all_rows=json.loads(raw)["cases"]
    accepted=[x for x in all_rows if x["id"].startswith("talk_n11_")]
    assert len(accepted)==48
    assert len(all_rows)==1547
    assert len({x["id"] for x in all_rows})==len(all_rows)
    assert len({normalize_question(x["input"]) for x in all_rows})==len(all_rows)
    assert len({normalize_question(x["response"]) for x in all_rows})==len(all_rows)
    lookup=KnowledgeSearch()
    for x in accepted:
        assert x["audiences"]==["all_ai_bots"]
        assert x["kind"] in ("congratulations","support","humor","profanity","conversation","creative")
        assert all(x[k].strip() for k in ("context","input","response","avoid"))
        assert not re.search(r"(?i)https?://|@\w+|\b\d{10,}\b", json.dumps(x,ensure_ascii=False))
        hits=lookup.search(x["input"],audience="all_ai_bots",limit=20)
        assert any(hit[0]==x["id"] for hit in hits),x["id"]
    print("N11_SOCIAL_OK accepted="+str(len(accepted)))
if __name__=="__main__":
    main()
