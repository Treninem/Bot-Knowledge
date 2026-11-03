"""T26: English contextual examples, exact pack hash, scope, privacy and retrieval."""
from __future__ import annotations
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "en_t26_"
KINDS = {"conversation": 5, "slang": 5, "sarcasm": 5, "rules": 5, "deception": 5, "support": 5, "creative": 5}

def norm(s: str) -> str:
    return re.sub(r"[^\w]+", " ", s.casefold()).strip()

def main() -> None:
    rel = "packs/ru/english_dialogues.json"
    raw = (ROOT / rel).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == next(p["sha256"] for p in manifest["packs"] if p["path"] == rel)
    assert len(raw) < 2 * 1024 * 1024
    cases = json.loads(raw)["cases"]
    selected = [r for r in cases if r["id"].startswith(PREFIX)]
    previous = [r for r in cases if not r["id"].startswith(PREFIX)]
    assert len(selected) == 35
    assert {r["id"] for r in selected} == {f"{PREFIX}{i:03d}" for i in range(1, 36)}
    assert Counter(r["kind"] for r in selected) == KINDS
    assert len({r["id"] for r in cases}) == len(cases)
    new_inputs = [norm(r["input"]) for r in selected]
    assert len(set(new_inputs)) == 35
    assert set(new_inputs).isdisjoint({norm(r["input"]) for r in previous})
    assert len({norm(r["response"]) for r in selected}) == 35
    index = KnowledgeSearch()
    for r in selected:
        assert r["language"] == "en" and r["audiences"] == ["all_ai_bots"]
        assert r["input"] and r["response"] and r["meaning_ru"] and r["avoid"]
        assert not re.search(r"(?:@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=])", str(r), re.I)
        assert any(hit[0] == r["id"] for hit in index.search(r["input"], audience="all_ai_bots", limit=20)), r["id"]
    print(f"T26_ENGLISH_OK cases={len(selected)} sha256={hashlib.sha256(raw).hexdigest()}")

if __name__ == "__main__":
    main()
