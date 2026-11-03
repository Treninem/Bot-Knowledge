"""T28 synthetic social situations: exact SHA, scope, dedup and retrieval."""
from __future__ import annotations
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "talk_t28_"
EXPECTED = {"congratulations":6, "support":6, "humor":6, "profanity":6, "conversation":6, "creative":6}

def norm(value):
    return re.sub(r"[^\w]+", " ", value.casefold().replace("ё", "е")).strip()

def main():
    rel = "packs/ru/social_dialogues.json"
    raw = (ROOT / rel).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == next(x["sha256"] for x in manifest["packs"] if x["path"] == rel)
    assert len(raw) < 2 * 1024 * 1024
    rows = json.loads(raw)["cases"]
    selected = [r for r in rows if r["id"].startswith(PREFIX)]
    assert len(selected) == 36
    assert {r["id"] for r in selected} == {f"{PREFIX}{i:03d}" for i in range(1, 37)}
    assert Counter(r["kind"] for r in selected) == EXPECTED
    assert len({r["id"] for r in rows}) == len(rows)
    new_inputs = [norm(x["input"]) for x in selected]
    other_inputs = {norm(x["input"]) for x in rows if not x["id"].startswith(PREFIX)}
    assert len(set(new_inputs)) == 36 and set(new_inputs).isdisjoint(other_inputs)
    assert len({norm(r["response"]) for r in selected}) == 36
    index = KnowledgeSearch()
    for r in selected:
        assert r["audiences"] == ["all_ai_bots"] and r["context"] and r["avoid"]
        assert not re.search(r"(?:@\w+|\b\d{9,}\b|(?:access_token|api[_-]?key)\s*[:=])", str(r), re.I)
        assert any(hit[0] == r["id"] for hit in index.search(r["input"], audience="all_ai_bots", limit=20)), r["id"]
    print("T28_SOCIAL_OK accepted=36 sha256=%s" % hashlib.sha256(raw).hexdigest())

if __name__ == "__main__":
    main()
