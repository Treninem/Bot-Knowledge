"""T57: original universal conversation precision QA, immutable source, and search."""
import hashlib
import json
import re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question, validate_qa_pack

ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/dialogue_help_qa.json"
PREFIX = "dlg_t57_"

def main():
    raw = (ROOT / REL).read_bytes()
    data = json.loads(raw)
    manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
    assert len(raw) < 1024 * 1024
    assert hashlib.sha256(raw).hexdigest() == next(
        e["sha256"] for e in manifest["packs"] if e["path"] == REL
    )
    assert validate_qa_pack(data) == len(data["records"])
    rows = [r for r in data["records"] if r["id"].startswith(PREFIX)]
    assert len(rows) == 32
    assert len(data["records"]) >= 468
    seen = set()
    for record in data["records"]:
        for term in (record["question"], *record["aliases"]):
            normalized = normalize_question(term)
            assert normalized not in seen, (record["id"], term)
            seen.add(normalized)
    search = KnowledgeSearch()
    checks = 0
    for record in rows:
        assert record["audiences"] == ["all_ai_bots"]
        assert record["contexts"] == ["direct", "private", "group_addressed"]
        assert record["language"] == "ru"
        assert record["source"].endswith("/docs/REQUIREMENTS_21.md")
        assert len(record["variants"]) == len(record["aliases"]) == 2
        assert all(x.strip() for x in [record["answer"], *record["variants"]])
        assert not any(k in record for k in ("action", "ban", "mute", "execute", "auto_apply"))
        assert not re.search(r"(?i)https?://|@\\w+|\\b\\d{10,}\\b", " ".join(
            [record["question"], *record["aliases"], record["answer"], *record["variants"]]
        ))
        for query in [record["question"], *record["aliases"]]:
            hits = search.search(query, audience="all_ai_bots", limit=20)
            assert any(hit[0] == record["id"] for hit in hits), (record["id"], query)
            checks += 1
    print(f"T57_UNIVERSAL_QA_OK rows={len(rows)} answers={len(rows)*3} queries={checks}")

if __name__ == "__main__":
    main()
