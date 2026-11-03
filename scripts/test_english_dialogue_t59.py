"""T59: original English contexts, meanings, unique IDs, SHA, privacy and bounded lookup."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question

ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/english_dialogues.json"
KINDS = ("conversation", "support", "slang", "sarcasm", "context", "creative")
PREFIX = "en_t59_"

def main():
    raw = (ROOT / REL).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
    data = json.loads(raw)
    assert hashlib.sha256(raw).hexdigest() == next(x["sha256"] for x in manifest["packs"] if x["path"] == REL)
    assert len(raw) < 2 * 1024 * 1024
    rows = [r for r in data["cases"] if r["id"].startswith(PREFIX)]
    assert len(rows) == 42
    assert len(data["cases"]) >= 642
    assert Counter(r["kind"] for r in rows) == dict.fromkeys(KINDS, 7)
    assert len({r["id"] for r in data["cases"]}) == len(data["cases"])
    for field in ("input", "response"):
        terms = [normalize_question(r[field]) for r in data["cases"]]
        assert len(set(terms)) == len(terms), field
    lookup = KnowledgeSearch()
    for r in rows:
        assert r["audiences"] == ["all_ai_bots"]
        assert r["language"] == "en"
        assert all(r[field].strip() for field in ("input", "response", "meaning_ru", "avoid"))
        assert not re.search(r"(?i)https?://|@\w+|\b\d{10,}\b", json.dumps(r, ensure_ascii=False))
        assert not any(k in r for k in ("action", "auto_apply", "sanction", "ban", "mute"))
        hits = lookup.search(r["input"], audience="all_ai_bots", limit=20)
        assert any(hit[0] == r["id"] for hit in hits), (r["id"], r["input"])
    print(f"T59_ENGLISH_OK new={len(rows)} total={len(data['cases'])}")

if __name__ == "__main__":
    main()
