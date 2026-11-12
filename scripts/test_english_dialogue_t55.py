"""T55: original English pragmatic dialogue cases, privacy, SHA, and local retrieval."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question

ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/english_dialogues.json"
PREFIX = "en_t55_"
KINDS = ("conversation", "slang", "sarcasm", "support", "rules", "creative")


def main():
    raw = (ROOT / REL).read_bytes()
    data = json.loads(raw)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == next(
        item["sha256"] for item in manifest["packs"] if item["path"] == REL
    )
    assert len(raw) < 2 * 1024 * 1024
    rows = [row for row in data["cases"] if row["id"].startswith(PREFIX)]
    assert len(rows) == 42 and len(data["cases"]) >= 600
    assert Counter(row["kind"] for row in rows) == dict.fromkeys(KINDS, 7)
    assert len({row["id"] for row in data["cases"]}) == len(data["cases"])
    for field in ("input", "response"):
        vals = [normalize_question(row[field]) for row in data["cases"]]
        assert len(vals) == len(set(vals)), field
    lookup = KnowledgeSearch()
    for row in rows:
        assert row["language"] == "en"
        assert row["audiences"] == ["all_ai_bots"]
        assert all(row[f].strip() for f in ("input", "response", "meaning_ru", "avoid"))
        assert not re.search(
            r"(?i)https?://|@\w+|\b\d{9,}\b|(?:api[_-]?key|access[_-]?token)\s*[:=]",
            json.dumps(row, ensure_ascii=False),
        ), row["id"]
        assert not any(k in row for k in ("action", "sanction", "auto_apply", "ban", "mute"))
        hits = lookup.search(row["input"], audience="all_ai_bots", limit=20)
        assert any(hit[0] == row["id"] for hit in hits), row["id"]
    print(f"T55_ENGLISH_OK added={len(rows)} total={len(data['cases'])}")


if __name__ == "__main__":
    main()
