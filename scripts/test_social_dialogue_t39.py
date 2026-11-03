"""T39: original social responses with verified manifest, audiences and retrieval."""
import hashlib,json,re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
def normalize(s):
    return " ".join(re.findall(r"[^\W_]+",s.casefold().replace("ё","е")))
def main():
    rel="packs/ru/social_dialogues.json"
    raw=(ROOT/rel).read_bytes()
    pack=json.loads(raw)
    manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(x["sha256"] for x in manifest["packs"] if x["path"]==rel)
    assert len(raw)<2*1024*1024
    all_cases=pack["cases"]
    rows=[x for x in all_cases if x["id"].startswith("talk_t39_")]
    assert len(rows)==36
    assert {x["id"] for x in rows}=={f"talk_t39_{n:03d}" for n in range(1,37)}
    assert {k:sum(x["kind"]==k for x in rows) for k in ["congratulations","support","humor","profanity","conversation","creative"]}=={k:6 for k in ["congratulations","support","humor","profanity","conversation","creative"]}
    assert len({x["id"] for x in all_cases})==len(all_cases)
    assert len({normalize(x["input"]) for x in all_cases})==len(all_cases)
    assert len({normalize(x["response"]) for x in rows})==len(rows)
    lookup=KnowledgeSearch()
    for x in rows:
        assert x["audiences"]==["all_ai_bots"]
        assert x["context"] and x["avoid"]
        assert not re.search(r"@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=]",str(x),re.I)
        assert any(h[0]==x["id"] for h in lookup.search(x["input"],audience="all_ai_bots",limit=20)),x["id"]
    print("T39_SOCIAL_OK",len(rows))
if __name__=="__main__":main()
