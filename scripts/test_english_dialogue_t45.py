"""T45 English original conversational situations; SHA, scope and indexed meaning."""
import hashlib, json, re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/english_dialogues.json"
KINDS=("conversation","slang","sarcasm","rules","deception","support","creative")
def norm(text):
    return " ".join(re.findall(r"[^\W_]+",text.casefold()))
def main():
    raw=(ROOT/REL).read_bytes()
    pack=json.loads(raw)
    manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(row["sha256"] for row in manifest["packs"] if row["path"]==REL)
    assert len(raw)<2*1024*1024
    rows=[r for r in pack["cases"] if r["id"].startswith("en_t45_")]
    assert {r["id"] for r in rows}=={f"en_t45_{i:03d}" for i in range(1,29)}
    assert all(sum(r["kind"]==k for r in rows)==4 for k in KINDS)
    old=[r for r in pack["cases"] if r not in rows]
    assert len({norm(r["input"]) for r in rows})==28
    assert len({norm(r["response"]) for r in rows})==28
    assert not ({norm(r["input"]) for r in old}&{norm(r["input"]) for r in rows})
    assert not ({norm(r["response"]) for r in old}&{norm(r["response"]) for r in rows})
    search=KnowledgeSearch()
    for r in rows:
        assert r["language"]=="en" and r["audiences"]==["all_ai_bots"]
        assert r["meaning_ru"] and r["avoid"]
        assert not re.search(r"@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=]",str(r),re.I)
        assert any(x[0]==r["id"] for x in search.search(r["input"],audience="all_ai_bots",limit=20)),r["id"]
    print(f"T45_ENGLISH_OK count={len(rows)} bytes={len(raw)}")
if __name__=="__main__":
    main()
