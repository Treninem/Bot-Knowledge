"""T48 English: exact manifest SHA, duplicate-free inputs, privacy, seven kinds and search."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch

ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/english_dialogues.json"
KINDS = ("conversation", "slang", "sarcasm", "rules", "deception", "support", "creative")

def norm(text):
    return " ".join(re.findall(r"[^\W_]+", text.casefold()))

def main():
    raw = (ROOT / REL).read_bytes()
    pack = json.loads(raw)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == next(x["sha256"] for x in manifest["packs"] if x["path"] == REL)
    assert len(raw) < 2 * 1024 * 1024
    rows = [r for r in pack["cases"] if r["id"].startswith("en_t48_")]
    assert len(rows) == 56
    assert Counter(r["kind"] for r in rows) == dict.fromkeys(KINDS, 8)
    assert len({r["id"] for r in pack["cases"]}) == len(pack["cases"])
    for field in ("input", "response"):
        values = [norm(r[field]) for r in pack["cases"]]
        assert len(values) == len(set(values)), field
    search = KnowledgeSearch()
    for r in rows:
        assert r["language"] == "en" and r["audiences"] == ["all_ai_bots"]
        assert all(r.get(k, "").strip() for k in ("input", "response", "meaning_ru", "avoid"))
        assert not re.search(r"@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=]", str(r), re.I)
        assert any(x[0] == r["id"] for x in search.search(r["input"], audience="all_ai_bots", limit=20)), r["id"]
    print(f"T48_EN_OK rows={len(rows)} pack_bytes={len(raw)}")

if __name__ == "__main__":
    main()
