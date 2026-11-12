"""T56: universal QA on incomplete instructions, sources, permissions, and conversation scope."""
import hashlib
import json
import re
from pathlib import Path

from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question, validate_qa_pack

ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/dialogue_help_qa.json"
PREFIX = "dlg_t56_"


def main():
    raw = (ROOT / REL).read_bytes()
    pack = json.loads(raw)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == next(
        entry["sha256"] for entry in manifest["packs"] if entry["path"] == REL
    )
    assert len(raw) < 2 * 1024 * 1024
    assert validate_qa_pack(pack) == len(pack["records"])
    rows = [r for r in pack["records"] if r["id"].startswith(PREFIX)]
    assert len(rows) == 24
    assert len(pack["records"]) >= 436

    seen_ids = set()
    seen_inputs = set()
    for row in pack["records"]:
        assert row["id"] not in seen_ids
        seen_ids.add(row["id"])
        for phrase in [row["question"], *row.get("aliases", [])]:
            n = normalize_question(phrase)
            assert n not in seen_inputs, (row["id"], phrase)
            seen_inputs.add(n)

    search = KnowledgeSearch()
    total = 0
    for row in rows:
        assert row["audiences"] == ["all_ai_bots"]
        assert row["contexts"] == ["direct", "private", "group_addressed"]
        assert row["language"] == "ru"
        # T56_024 gained two verified input aliases; its two reply variants stay fixed.
        assert len(row["aliases"]) == (4 if row["id"] == "dlg_t56_024" else 2)
        assert len(row["variants"]) == 2
        assert row["source"].endswith("/docs/REQUIREMENTS_21.md")
        texts = [row["question"], *row["aliases"], row["answer"], *row["variants"]]
        assert all(t.strip() for t in texts)
        assert not re.search(r"(?i)https?://|@\w+|\b\d{9,}\b|(?:api[_-]?key|access[_-]?token)\s*[:=]", " ".join(texts))
        assert not any(k in row for k in ("action", "sanction", "ban", "mute", "auto_apply"))
        for phrase in [row["question"], *row["aliases"]]:
            hits = search.search(phrase, audience="all_ai_bots", limit=20)
            assert any(hit[0] == row["id"] for hit in hits), (row["id"], phrase)
            total += 1
    print(f"T56_UNIVERSAL_QA_OK new={len(rows)} answers={len(rows)*3} searches={total}")


if __name__ == "__main__":
    main()
