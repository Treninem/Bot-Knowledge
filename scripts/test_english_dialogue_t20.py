"""T20 English conversation, source-safe rule nuance and local retrieval."""
from __future__ import annotations
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch

ROOT = Path(__file__).resolve().parents[1]
KINDS = {"conversation": 5, "support": 5, "slang": 5, "sarcasm": 4, "rules": 4, "deception": 4, "creative": 5}
EXPECTED_IDS = {f"en_t20_{i:03d}" for i in range(1, 33)}

def normalize(value: str) -> str:
    return re.sub(r"[^\w]+", " ", value.casefold()).strip()

def main():
    path = "packs/ru/english_dialogues.json"
    raw = (ROOT / path).read_bytes()
    manifest = json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    entry = next(p for p in manifest["packs"] if p["path"] == path)
    assert hashlib.sha256(raw).hexdigest() == entry["sha256"], "T20 hash"
    assert len(raw) < 2*1024*1024, "T20 pack limit"
    rows = json.loads(raw)["cases"]
    added = [x for x in rows if x["id"].startswith("en_t20_")]
    assert {x["id"] for x in added} == EXPECTED_IDS
    assert Counter(x["kind"] for x in added) == KINDS
    assert len({x["id"] for x in rows}) == len(rows), "T20 ID duplicate"
    assert len({normalize(x["input"]) for x in rows}) == len(rows), "T20 input duplicate"
    assert len({normalize(x["response"]) for x in added}) == len(added), "T20 repeated response"
    search = KnowledgeSearch()
    for x in added:
        assert x["language"] == "en" and x["audiences"] == ["all_ai_bots"]
        assert x["response"] and x["meaning_ru"] and x["avoid"]
        assert not re.search(r"(?:@\w+|\b\d{9,}\b|access_token|api[_-]?key)", str(x), re.I), "T20 private marker"
        results = search.search(x["input"], audience="all_ai_bots", limit=20)
        assert any(h[0] == x["id"] for h in results), "T20 retrieval " + x["id"]
    print(f"ENGLISH_T20_OK added={len(added)} size={len(raw)} sha256={entry['sha256']}")

if __name__ == "__main__":
    main()
