"""T67: scoped original synthetic RU situations, SHA and retrieval."""
from pathlib import Path
from collections import Counter
import hashlib, json, re
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/social_dialogues.json"
PREFIX="talk_t67_"
COUNT=60

def main():
    raw=(ROOT/REL).read_bytes()
    manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    assert len(raw)<2*1024*1024
    assert hashlib.sha256(raw).hexdigest()==next(r["sha256"] for r in manifest["packs"] if r["path"]==REL)
    cases=json.loads(raw)["cases"]
    assert len(cases)>=1702  # pinned T67 baseline; later verified editions may append cases
    assert len(set(r["id"] for r in cases))==len(cases)
    for key in ("input","response"):
        phrases=[normalize_question(r[key]) for r in cases]
        assert len(phrases)==len(set(phrases)),key
    added=[r for r in cases if r["id"].startswith(PREFIX)]
    assert len(added)==COUNT
    assert Counter(r["kind"] for r in added)=={'congratulations':10,'support':10,'humor':10,'profanity':10,'conversation':10,'creative':10}
    search=KnowledgeSearch()
    for r in added:
        assert r["audiences"]==["all_ai_bots"]
        assert all(r[k].strip() for k in ("context","input","response","avoid"))
        assert not re.search(r"(?i)https?://|@\w+|\b\d{10,}\b",json.dumps(r,ensure_ascii=False))
        assert not any(k in r for k in ("auto_apply","action","sanction","ban","mute"))
        matches=search.search(r["input"],audience="all_ai_bots",limit=20)
        assert any(hit[0]==r["id"] for hit in matches),r["id"]
    print(f"T67_SOCIAL_OK accepted={len(added)} total={len(cases)}")
if __name__=="__main__":main()
