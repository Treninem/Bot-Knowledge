"""T21 context-specific social examples, SHA, privacy and local indexed retrieval."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from collections import Counter
from scripts.search_knowledge import KnowledgeSearch

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "talk_t21_"
COUNTS = {"congratulations": 8, "support": 8, "humor": 8, "profanity": 8, "conversation": 8, "creative": 8}

def norm(s: str) -> str:
    return re.sub(r"[^\\w]+", " ", s.casefold().replace("ё", "е")).strip()

def main() -> None:
    rel = "packs/ru/social_dialogues.json"
    raw = (ROOT / rel).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == next(x["sha256"] for x in manifest["packs"] if x["path"] == rel)
    assert len(raw) < 2 * 1024 * 1024
    cases = json.loads(raw)["cases"]
    added = [c for c in cases if c["id"].startswith(PREFIX)]
    assert len(added) == 48
    assert {x["id"] for x in added} == {f"{PREFIX}{i:03d}" for i in range(1, 49)}
    assert Counter(x["kind"] for x in added) == COUNTS
    assert len({x["id"] for x in cases}) == len(cases)
    assert len({norm(x["input"]) for x in cases}) == len(cases)
    assert len({norm(x["response"]) for x in added}) == len(added)
    index = KnowledgeSearch()
    for row in added:
        assert row["audiences"] == ["all_ai_bots"] and row["context"] and row["avoid"]
        assert not re.search(r"(?:@\\w+|\\b\\d{9,}\\b|(?:api[_-]?key|access_token)\\s*[:=])", str(row), re.I)
        assert any(hit[0] == row["id"] for hit in index.search(row["input"], audience="all_ai_bots", limit=20)), row["id"]
    print(f"T21_SOCIAL_OK cases={len(added)} sha256={hashlib.sha256(raw).hexdigest()}")

if __name__ == "__main__":
    main()
