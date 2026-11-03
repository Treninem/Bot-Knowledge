"""T21 contextual social cases: exact SHA, privacy and offline retrieval."""
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
    return re.sub(r"[^\w]+", " ", s.casefold().replace("ё", "е")).strip()

def main() -> None:
    rel = "packs/ru/social_dialogues.json"
    raw = (ROOT / rel).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == next(p["sha256"] for p in manifest["packs"] if p["path"] == rel)
    assert len(raw) < 2 * 1024 * 1024
    cases = json.loads(raw)["cases"]
    selected = [r for r in cases if r["id"].startswith(PREFIX)]
    previous = [r for r in cases if not r["id"].startswith(PREFIX)]
    assert len(selected) == 48
    assert {r["id"] for r in selected} == {f"{PREFIX}{i:03d}" for i in range(1, 49)}
    assert Counter(r["kind"] for r in selected) == COUNTS
    assert len({r["id"] for r in cases}) == len(cases)
    new_inputs = [norm(r["input"]) for r in selected]
    assert len(set(new_inputs)) == len(selected), "duplicate in T21 inputs"
    assert not (set(new_inputs) & {norm(r["input"]) for r in previous}), "reused older input"
    assert len({norm(r["response"]) for r in selected}) == len(selected)
    index = KnowledgeSearch()
    for r in selected:
        assert r["audiences"] == ["all_ai_bots"] and r["context"] and r["avoid"]
        assert not re.search(r"(?:@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=])", str(r), re.I)
        assert any(hit[0] == r["id"] for hit in index.search(r["input"], audience="all_ai_bots", limit=20)), r["id"]
    print(f"T21_SOCIAL_OK cases={len(selected)} sha256={hashlib.sha256(raw).hexdigest()}")

if __name__ == "__main__":
    main()
