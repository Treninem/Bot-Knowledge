"""New social dialogue scenes must be retrievable without changing old data."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from search_knowledge import KnowledgeSearch

def main() -> None:
    raw=(ROOT/"packs/ru/social_dialogues.json").read_bytes()
    p=json.loads(raw)
    manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    expected=next(e["sha256"] for e in manifest["packs"] if e["path"]=="packs/ru/social_dialogues.json")
    assert hashlib.sha256(raw).hexdigest()==expected
    added=[r for r in p["cases"] if r["id"].startswith("talk_t7_")]
    assert len(added)==48
    assert {r["kind"] for r in added}=={"congratulations","support","humor","profanity","conversation","creative"}
    assert all(sum(r["kind"]==k for r in added)==8 for k in {r["kind"] for r in added})
    ids={r["id"] for r in added}
    assert len(ids)==48
    search=KnowledgeSearch()
    for r in added:
        assert r["context"] and r["avoid"] and r["audiences"]==["all_ai_bots"]
        hits=search.search(r["input"],"all_ai_bots",limit=20)
        # A specialized semantic rule may outrank a valid general dialogue case.
        # Require actual indexed retrieval without altering existing ranking.
        assert r["id"] in {item[0] for item in hits},(r["id"],hits)
    newer=[r for r in p["cases"] if r["id"].startswith("talk_t8_")]
    assert len(newer)==36, len(newer)
    assert len({r["id"] for r in newer})==len(newer)
    assert {r["kind"] for r in newer}=={"congratulations","support","humor","profanity","conversation","creative"}
    for r in newer:
        assert r["context"] and r["avoid"] and r["audiences"]==["all_ai_bots"]
        hits=search.search(r["input"],"all_ai_bots",limit=20)
        assert r["id"] in {item[0] for item in hits},(r["id"],hits)
    print("SOCIAL_CONTEXT_T8_SEARCH_OK 36/36")
    print("SOCIAL_CONTEXT_T7_SEARCH_OK 48/48")

    recent=[r for r in p["cases"] if r["id"].startswith("talk_t10_")]
    assert len(recent)==36, len(recent)
    assert len({r["id"] for r in recent})==len(recent)
    assert {r["kind"] for r in recent}=={"congratulations","support","humor","profanity","conversation","creative"}
    for r in recent:
        assert r["context"] and r["avoid"] and r["audiences"]==["all_ai_bots"]
        hits=search.search(r["input"],"all_ai_bots",limit=20)
        assert r["id"] in {x[0] for x in hits},(r["id"],hits)
    print("SOCIAL_CONTEXT_T10_SEARCH_OK 36/36")

if __name__=="__main__":
    main()
