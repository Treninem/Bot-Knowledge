"""T54: 72 new privacy-safe contextual RU social conversations."""
from __future__ import annotations
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question

ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/social_dialogues.json"
KINDS = ("congratulations", "support", "humor", "profanity", "conversation", "creative")
PREFIX = "talk_t54_"


def main() -> None:
    raw = (ROOT / REL).read_bytes()
    data = json.loads(raw)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    pack = next(row for row in manifest["packs"] if row["path"] == REL)
    assert hashlib.sha256(raw).hexdigest() == pack["sha256"]
    assert len(raw) < 2 * 1024 * 1024
    cases = data["cases"]
    rows = [row for row in cases if row["id"].startswith(PREFIX)]
    assert len(rows) == 72
    assert len(cases) >= 1451
    assert Counter(row["kind"] for row in rows) == dict.fromkeys(KINDS, 12)
    assert len({row["id"] for row in cases}) == len(cases)
    for field in ("input", "response"):
        strings = [normalize_question(row[field]) for row in cases]
        assert len(strings) == len(set(strings)), f"duplicate {field}"
    search = KnowledgeSearch()
    for row in rows:
        assert row["audiences"] == ["all_ai_bots"]
        assert all(row[key].strip() for key in ("context", "input", "response", "avoid"))
        assert row["kind"] in KINDS
        assert not re.search(
            r"(?i)https?://|@\w+|\b\d{9,}\b|(?:api[_-]?key|access[_-]?token)\s*[:=]",
            json.dumps(row, ensure_ascii=False),
        )
        # A language response must not encode a live moderation sanction.
        assert not any(key in row for key in ("action", "auto_apply", "sanction", "ban", "mute"))
        hits = search.search(row["input"], audience="all_ai_bots", limit=100)
        assert any(hit[0] == row["id"] for hit in hits), row["id"]
    print(f"T54_SOCIAL_OK added={len(rows)} total={len(cases)}")


if __name__ == "__main__":
    main()
