"""T19 synthetic social examples: privacy, SHA, uniqueness, context and search."""
from __future__ import annotations
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "talk_t19_"
KIND_COUNTS = {
    "conversation": 10,
    "support": 10,
    "humor": 10,
    "profanity": 10,
    "congratulations": 10,
    "creative": 10,
}
EXPECTED_IDS = {f"{PREFIX}{i:03d}" for i in range(1, 61)}

def norm(value: str) -> str:
    return re.sub(r"[^\\w]+", " ", value.casefold().replace("ё", "е")).strip()

def tokens(value: str) -> set[str]:
    return {x for x in norm(value).split() if len(x) >= 4}

def jaccard(left: str, right: str) -> float:
    a, b = tokens(left), tokens(right)
    return len(a & b) / len(a | b) if a | b else 0.0

def main() -> None:
    rel = "packs/ru/social_dialogues.json"
    raw = (ROOT / rel).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    entry = next(p for p in manifest["packs"] if p["path"] == rel)
    assert hashlib.sha256(raw).hexdigest() == entry["sha256"], "T19 pack sha mismatch"
    assert len(raw) < 2 * 1024 * 1024, "T19 size limit"
    rows = json.loads(raw)["cases"]
    chosen = [r for r in rows if r["id"].startswith(PREFIX)]
    assert {r["id"] for r in chosen} == EXPECTED_IDS, "T19 id set"
    assert Counter(r["kind"] for r in chosen) == KIND_COUNTS, "T19 kind coverage"
    assert len({r["id"] for r in rows}) == len(rows), "T19 repeated id"
    all_inputs = [norm(r["input"]) for r in rows]
    assert len(set(all_inputs)) == len(all_inputs), "T19 repeated normalized input"
    selected_responses = [norm(r["response"]) for r in chosen]
    assert len(set(selected_responses)) == len(selected_responses), "T19 repeated response"
    past = [r for r in rows if not r["id"].startswith(PREFIX)]
    search = KnowledgeSearch()
    for r in chosen:
        assert r["context"] and r["avoid"] and r["response"]
        assert r["audiences"] == ["all_ai_bots"]
        assert not re.search(r"(?:@\\w+|\\b\\d{9,}\\b|(?:api[_-]?key|access_token)\\s*[:=])", str(r), re.I), "T19 private marker"
        assert all(jaccard(r["input"], old["input"]) < .80 for old in past), "T19 close input"
        hits = search.search(r["input"], audience="all_ai_bots", limit=30)
        assert any(hit[0] == r["id"] for hit in hits), "T19 retrieval " + r["id"]
    print(f"T19_SOCIAL_OK accepted={len(chosen)} bytes={len(raw)} SHA256={entry['sha256']}")

if __name__ == "__main__":
    main()
