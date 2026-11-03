"""T37 bilingual English contexts: fixed SHA, original meaning and scoped search."""
import json,hashlib,re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
def norm(s):
    return " ".join(re.findall(r"[^\W_]+",s.casefold()))
def tok(s):
    return {x for x in norm(s).split() if len(x)>=3}
def sim(a,b):
    x,y=tok(a),tok(b)
    return len(x&y)/len(x|y) if x|y else 0.0
def main():
    rel="packs/ru/english_dialogues.json"
    raw=(ROOT/rel).read_bytes()
    manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(x["sha256"] for x in manifest["packs"] if x["path"]==rel)
    assert len(raw)<2*1024*1024
    allcases=json.loads(raw)["cases"]
    rows=[x for x in allcases if x["id"].startswith("en_t37_")]
    previous=[x for x in allcases if not x["id"].startswith("en_t37_")]
    assert len(rows)==42
    assert len({x["id"] for x in allcases})==len(allcases)
    assert len({norm(x["input"]) for x in allcases})==len(allcases)
    assert len({norm(x["response"]) for x in rows})==len(rows)
    assert {k:sum(x["kind"]==k for x in rows) for k in ["conversation","slang","sarcasm","rules","deception","support","creative"]}=={k:6 for k in ["conversation","slang","sarcasm","rules","deception","support","creative"]}
    search=KnowledgeSearch()
    for row in rows:
        assert row["language"]=="en" and row["audiences"]==["all_ai_bots"] and row["meaning_ru"] and row["avoid"]
        assert not re.search(r"@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=]",str(row),re.I)
        assert all(sim(row["input"],x["input"])<.70 for x in previous)
        assert any(hit[0]==row["id"] for hit in search.search(row["input"],audience="all_ai_bots",limit=25)),row["id"]
    print("T37_ENGLISH_OK",len(rows))
if __name__=="__main__":main()
