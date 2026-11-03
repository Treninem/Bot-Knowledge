"""T50: 48 new, context-guarded synthetic social replies and exact SHA."""
import hashlib, json, re
from collections import Counter
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/social_dialogues.json"
KINDS=("congratulations","support","humor","profanity","conversation","creative")
def main():
    raw=(ROOT/REL).read_bytes()
    data=json.loads(raw)
    manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(x["sha256"] for x in manifest["packs"] if x["path"]==REL)
    assert len(raw)<2*1024*1024
    rows=[x for x in data["cases"] if x["id"].startswith("talk_t50_")]
    assert len(rows)==48
    assert Counter(x["kind"] for x in rows)==dict.fromkeys(KINDS,8)
    assert len({x["id"] for x in data["cases"]})==len(data["cases"])
    for field in ("input","response"):
        values=[normalize_question(x[field]) for x in data["cases"]]
        assert len(set(values))==len(values),field
    index=KnowledgeSearch()
    for row in rows:
        assert row["audiences"]==["all_ai_bots"]
        assert all(row[k].strip() for k in ("context","input","response","avoid"))
        assert not re.search(r"(?i)https?://|@\\w+|\\b\\d{9,}\\b|(?:api[_-]?key|access[_-]?token)\\s*[:=]",str(row))
        hits=index.search(row["input"],audience="all_ai_bots",limit=20)
        assert any(x[0]==row["id"] for x in hits),(row["id"],hits)
    print("T50_SOCIAL_OK new=48 total="+str(len(data["cases"])))
if __name__=="__main__":main()
