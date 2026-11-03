"""T15 original conversational contexts: integrity, deduplication and safe retrieval."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/social_dialogues.json"

def normalize(value):
    import unicodedata
    return " ".join("".join(c if c.isalnum() else " " for c in unicodedata.normalize("NFKC",value).casefold().replace("ё","е")).split())

def main():
    raw=(ROOT/REL).read_bytes()
    manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    expected=next(row["sha256"] for row in manifest["packs"] if row["path"]==REL)
    assert hashlib.sha256(raw).hexdigest()==expected
    assert len(raw)<2*1024*1024
    pack=json.loads(raw)
    rows=[r for r in pack["cases"] if r["id"].startswith("talk_t15_")]
    assert len(rows)==36 and len(pack["cases"])==665
    assert len({r["id"] for r in rows})==36
    assert len({normalize(r["input"]) for r in rows})==36
    assert {k:sum(x["kind"]==k for x in rows) for k in {"congratulations","support","humor","profanity","conversation","creative"}}=={k:6 for k in {"congratulations","support","humor","profanity","conversation","creative"}}
    assert all(r["audiences"]==["all_ai_bots"] and r["context"] and r["avoid"] and r["response"] for r in rows)
    lookup=KnowledgeSearch()
    checked=0
    for r in rows:
        if len(r["input"].split())>=7:
            hits=lookup.search(r["input"],audience="all_ai_bots",limit=20)
            assert any(hit[0]==r["id"] for hit in hits),(r["id"],hits)
            checked+=1
    print(f"SOCIAL_T15_OK records={len(rows)} indexed_checks={checked}")

if __name__=="__main__":main()
