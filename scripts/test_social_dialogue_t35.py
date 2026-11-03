"""T35 synthetic social dialogues: duplicate, context, index, privacy, immutable SHA."""
import hashlib
import json
import re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "talk_t35_"
EXPECTED = {"congratulations":8, "support":8, "humor":8, "profanity":8, "conversation":8, "creative":8}

def norm(s):
    return " ".join(re.findall(r"[^\W_]+", s.casefold().replace("ё", "е"), re.U))

def tok(s):
    return {x for x in norm(s).split() if len(x) >= 4}

def jac(a,b):
    x,y=tok(a),tok(b)
    return len(x&y)/len(x|y) if x|y else 0.0

def test_new_social_contexts():
    rel="packs/ru/social_dialogues.json"
    raw=(ROOT/rel).read_bytes()
    meta=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(x["sha256"] for x in meta["packs"] if x["path"]==rel)
    assert len(raw)<2*1024*1024
    all_cases=json.loads(raw)["cases"]
    current=[x for x in all_cases if x["id"].startswith(PREFIX)]
    previous=[x for x in all_cases if not x["id"].startswith(PREFIX)]
    assert len(current)==48
    assert {x["id"] for x in current}=={f"{PREFIX}{i:03d}" for i in range(1,49)}
    assert {k:sum(x["kind"]==k for x in current) for k in EXPECTED}==EXPECTED
    assert len({x["id"] for x in all_cases})==len(all_cases)
    assert len({norm(x["input"]) for x in all_cases})==len(all_cases)
    assert len({norm(x["response"]) for x in current})==len(current)
    idx=KnowledgeSearch()
    for item in current:
        assert item["audiences"]==["all_ai_bots"] and item["context"] and item["avoid"]
        assert not re.search(r"@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=]",str(item),re.I)
        assert all(jac(item["input"],x["input"])<.58 for x in previous)
        assert any(hit[0]==item["id"] for hit in idx.search(item["input"],audience="all_ai_bots",limit=20)),item["id"]

if __name__=="__main__":
    test_new_social_contexts()
    print("T35_SOCIAL_OK accepted=48 contexts=6")
