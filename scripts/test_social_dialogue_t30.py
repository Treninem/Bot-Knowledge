"""T30: distinct synthetic social situations, manifest SHA, scope, privacy and lookup."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from scripts.search_knowledge import KnowledgeSearch

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "talk_t30_"
EXPECTED = {kind: 10 for kind in (
    "congratulations", "support", "humor", "profanity", "conversation", "creative"
)}


def normalize(text: str) -> str:
    return re.sub(r"[^\w]+", " ", text.casefold().replace("ё", "е")).strip()


def tokens(text: str) -> set[str]:
    return {token for token in normalize(text).split() if len(token) >= 4}


def jaccard(a: str, b: str) -> float:
    left, right = tokens(a), tokens(b)
    union = left | right
    return len(left & right) / len(union) if union else 0.0


def main() -> None:
    path = "packs/ru/social_dialogues.json"
    raw = (ROOT / path).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    stored = next(p["sha256"] for p in manifest["packs"] if p["path"] == path)
    assert hashlib.sha256(raw).hexdigest() == stored, "manifest hash mismatch"
    assert len(raw) < 2 * 1024 * 1024, "consumer pack exceeds 2 MiB"

    rows = json.loads(raw)["cases"]
    new = [r for r in rows if r["id"].startswith(PREFIX)]
    old = [r for r in rows if not r["id"].startswith(PREFIX)]
    assert len(new) == 60
    assert {r["id"] for r in new} == {f"{PREFIX}{i:03d}" for i in range(1, 61)}
    assert Counter(r["kind"] for r in new) == EXPECTED
    assert len({r["id"] for r in rows}) == len(rows)
    assert len({normalize(r["input"]) for r in rows}) == len(rows), "reused input"
    assert len({normalize(r["response"]) for r in new}) == len(new), "reused response"

    index = KnowledgeSearch()
    for row in new:
        assert row["audiences"] == ["all_ai_bots"]
        assert row["context"].strip() and row["avoid"].strip()
        assert len(row["response"].strip()) >= 20
        assert not re.search(
            r"(?:@\w+|\b\d{9,}\b|(?:access_token|api[_-]?key)\s*[:=])",
            str(row), re.IGNORECASE
        ), row["id"]
        assert all(jaccard(row["input"], previous["input"]) < .80 for previous in old), row["id"]
        results = index.search(row["input"], audience="all_ai_bots", limit=20)
        assert any(hit[0] == row["id"] for hit in results), row["id"]

    print(f"T30_SOCIAL_OK cases={len(new)} total={len(rows)} sha256={stored}")


if __name__ == "__main__":
    main()
