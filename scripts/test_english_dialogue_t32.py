"""T32: distinct contextual English examples, privacy, pack SHA and local retrieval."""
from __future__ import annotations
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "en_t32_"
EXPECTED = {"conversation": 6, "slang": 4, "sarcasm": 6, "rules": 6, "deception": 6, "support": 6, "creative": 6}


def norm(text: str) -> str:
    return re.sub(r"[^\w]+", " ", text.casefold()).strip()


def tokens(text: str) -> set[str]:
    return {token for token in norm(text).split() if len(token) >= 4}


def similarity(a: str, b: str) -> float:
    x, y = tokens(a), tokens(b)
    union = x | y
    return len(x & y) / len(union) if union else 0.0


def main() -> None:
    path = "packs/ru/english_dialogues.json"
    raw = (ROOT / path).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    expected_sha = next(row["sha256"] for row in manifest["packs"] if row["path"] == path)
    assert hashlib.sha256(raw).hexdigest() == expected_sha
    assert len(raw) < 2 * 1024 * 1024

    data = json.loads(raw)
    rows = data["cases"]
    new = [row for row in rows if row["id"].startswith(PREFIX)]
    previous = [row for row in rows if not row["id"].startswith(PREFIX)]
    assert len(new) == 40
    assert {r["id"] for r in new} == {f"{PREFIX}{i:03d}" for i in range(1, 41)}
    assert Counter(r["kind"] for r in new) == EXPECTED
    assert len({r["id"] for r in rows}) == len(rows)
    assert len({norm(r["input"]) for r in rows}) == len(rows)
    assert len({norm(r["response"]) for r in new}) == len(new)
    index = KnowledgeSearch()
    for row in new:
        assert row["audiences"] == ["all_ai_bots"] and row["language"] == "en"
        assert row["input"].strip() and row["response"].strip()
        assert row["meaning_ru"].strip() and row["avoid"].strip()
        assert not re.search(
            r"(?:@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=])",
            str(row), re.IGNORECASE,
        )
        assert all(similarity(row["input"], older["input"]) < .78 for older in previous), row["id"]
        assert any(hit[0] == row["id"] for hit in index.search(row["input"], audience="all_ai_bots", limit=20)), row["id"]
    print(f"T32_ENGLISH_OK cases=40 total={len(rows)} sha256={expected_sha}")


if __name__ == "__main__":
    main()
