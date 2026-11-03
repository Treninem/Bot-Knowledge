"""T33: original social contexts, SHA, scope, privacy, dedup, retrieval."""
from collections import Counter
import hashlib,json,re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
PREFIX="talk_t33_"
EXPECTED={"congratulations":10,"support":10,"humor":10,"profanity":10,"conversation":10,"creative":10}
def norm(s):return re.sub(r"[^\w]+"," ",s.casefold().replace("ё","е")).strip()
def tok(s):return {x for x in norm(s).split() if len(x)>=4}
def jac(a,b):
    x,y=tok(a),tok(b)
    return len(x&y)/len(x|y) if x|y else 0.0
def main():
    rel="packs/ru/social_dialogues.json"
    raw=(ROOT/rel).read_bytes()
    m=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(x["sha256"] for x in m["packs"] if x["path"]==rel)
    assert len(raw)<2*1024*1024
    cases=json.loads(raw)["cases"]
    new=[x for x in cases if x["id"].startswith(PREFIX)]
    old=[x for x in cases if not x["id"].startswith(PREFIX)]
    assert len(new)==60
    assert {x["id"] for x in new}=={f"{PREFIX}{i:03d}" for i in range(1,61)}
    assert Counter(x["kind"] for x in new)==EXPECTED
    assert len({x["id"] for x in cases})==len(cases)
    assert len({norm(x["input"]) for x in cases})==len(cases)
    assert len({norm(x["response"]) for x in new})==len(new)
    idx=KnowledgeSearch()
    for x in new:
        assert x["audiences"]==["all_ai_bots"] and x["context"] and x["avoid"]
        assert not re.search(r"(?:@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=])",str(x),re.I)
        assert all(jac(x["input"],v["input"])<.78 for v in old),x["id"]
        assert any(hit[0]==x["id"] for hit in idx.search(x["input"],audience="all_ai_bots",limit=20)),x["id"]
    print(f"T33_SOCIAL_OK accepted={len(new)} total={len(cases)}")
if __name__=="__main__":main()
