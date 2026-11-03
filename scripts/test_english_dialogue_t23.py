"""T23: new bilingual English dialogue cases, scopes, hash and retrieval."""
from __future__ import annotations
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch

ROOT = Path(__file__).resolve().parents[1]
KINDS = {"conversation": 5, "support": 5, "slang": 5, "sarcasm": 5, "rules": 5, "deception": 5, "creative": 5}
PREFIX = "en_t23_"

def norm(s: str) -> str:
    return re.sub(r"[^\w]+", " ", s.casefold()).strip()

def main() -> None:
    relative = "packs/ru/english_dialogues.json"
    raw = (ROOT / relative).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == next(x["sha256"] for x in manifest["packs"] if x["path"] == relative)
    assert len(raw) < 2 * 1024 * 1024
    rows = json.loads(raw)["cases"]
    added = [r for r in rows if r["id"].startswith(PREFIX)]
    assert len(added) == 35
    assert {r["id"] for r in added} == {f"{PREFIX}{i:03d}" for i in range(1, 36)}
    assert Counter(r["kind"] for r in added) == KINDS
    assert len({r["id"] for r in rows}) == len(rows)
    assert len({norm(r["input"]) for r in rows}) == len(rows)
    assert len({norm(r["response"]) for r in added}) == len(added)
    index = KnowledgeSearch()
    for row in added:
        assert row["language"] == "en" and row["audiences"] == ["all_ai_bots"]
        assert row["response"] and row["meaning_ru"] and row["avoid"]
        assert not re.search(r"(?:@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=])", str(row), re.I)
        assert any(h[0] == row["id"] for h in index.search(row["input"], audience="all_ai_bots", limit=20)), row["id"]
    print(f"T23_ENGLISH_OK new={len(added)} sha256={hashlib.sha256(raw).hexdigest()}")

if __name__ == "__main__":
    main()
