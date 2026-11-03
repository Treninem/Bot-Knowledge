"""T58: 48 original RU contexts, deduplication, privacy, SHA and bounded local search."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question

ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/social_dialogues.json"
KINDS = ("congratulations", "support", "humor", "profanity", "conversation", "creative")
PREFIX = "talk_t58_"

def main():
    raw = (ROOT / REL).read_bytes()
    pack = json.loads(raw)
    manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
    expected = next(item["sha256"] for item in manifest["packs"] if item["path"] == REL)
    assert hashlib.sha256(raw).hexdigest() == expected
    assert len(raw) < 2 * 1024 * 1024
    cases = pack["cases"]
    rows = [r for r in cases if r["id"].startswith(PREFIX)]
    assert len(rows) == 48
    assert len(cases) >= 1499
    assert Counter(r["kind"] for r in rows) == dict.fromkeys(KINDS, 8)
    assert len(set(r["id"] for r in cases)) == len(cases)
    for field in ("input", "response"):
        normalized = [normalize_question(r[field]) for r in cases]
        assert len(set(normalized)) == len(normalized), field
    search = KnowledgeSearch()
    for row in rows:
        assert row["kind"] in KINDS
        assert row["audiences"] == ["all_ai_bots"]
        assert all(row[f].strip() for f in ("context", "input", "response", "avoid"))
        assert not any(k in row for k in ("action", "sanction", "auto_apply", "ban", "mute"))
        assert not re.search(r"(?i)https?://|@\w+|\b\d{10,}\b", json.dumps(row, ensure_ascii=False))
        hits = search.search(row["input"], audience="all_ai_bots", limit=20)
        assert any(hit[0] == row["id"] for hit in hits), row["id"]
    print(f"T58_SOCIAL_OK new={len(rows)} total={len(cases)}")

if __name__ == "__main__":
    main()
