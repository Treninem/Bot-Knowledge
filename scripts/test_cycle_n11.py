"""N11: synthetic QA and English dialogue integrity, scope and indexed retrieval."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch

ROOT = Path(__file__).resolve().parents[1]
M = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))

def read_verified(rel):
    data = (ROOT / rel).read_bytes()
    assert hashlib.sha256(data).hexdigest() == next(x["sha256"] for x in M["packs"] if x["path"] == rel)
    return json.loads(data)

def main():
    q = read_verified("packs/ru/dialogue_help_qa.json")
    e = read_verified("packs/ru/english_dialogues.json")
    qa = [x for x in q["records"] if x["id"].startswith("dlg_n11_")]
    en = [x for x in e["cases"] if x["id"].startswith("en_n11_")]
    assert len(qa) == 30, len(qa)
    assert len(en) == 42, len(en)
    assert len(set(x["id"] for x in qa + en)) == len(qa + en)
    search = KnowledgeSearch()
    checks = 0
    for r in qa:
        assert r["audiences"] == ["all_ai_bots"]
        assert r["contexts"] == ["direct", "private", "group_addressed"]
        assert len(r["aliases"]) == 2 and len(r["variants"]) == 2
        assert not any(token in str(r).lower() for token in ["telegram_id", "chat_id", "user_id", "password:", "token:"])
        for term in [r["question"], *r["aliases"]]:
            hits = search.search(term, audience="all_ai_bots", limit=5)
            assert hits and hits[0][0] == r["id"], (r["id"], term, hits)
            checks += 1
    for r in en:
        assert r["language"] == "en" and r["audiences"] == ["all_ai_bots"]
        assert r["response"] and r["meaning_ru"] and r["avoid"]
        hits = search.search(r["input"], audience="all_ai_bots", limit=5)
        assert hits and hits[0][0] == r["id"], (r["id"], r["input"], hits)
        checks += 1
    print(f"N11_QA_EN_OK qa={len(qa)} en={len(en)} indexed_queries={checks}")

if __name__ == "__main__":
    main()
