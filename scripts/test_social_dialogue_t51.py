"""T51: 72 contextual original social cases, manifest integrity and local retrieval."""
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
def main():
    raw = (ROOT / REL).read_bytes()
    data = json.loads(raw)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    expected = next(p["sha256"] for p in manifest["packs"] if p["path"] == REL)
    assert hashlib.sha256(raw).hexdigest() == expected
    assert len(raw) < 2 * 1024 * 1024
    rows = [x for x in data["cases"] if x["id"].startswith("talk_t51_")]
    assert len(rows) == 72 and len(data["cases"]) >= 1379
    assert Counter(x["kind"] for x in rows) == dict.fromkeys(KINDS, 12)
    assert len({x["id"] for x in data["cases"]}) == len(data["cases"])
    for field in ("input", "response"):
        normalized = [normalize_question(x[field]) for x in data["cases"]]
        assert len(normalized) == len(set(normalized)), field
    search = KnowledgeSearch()
    for x in rows:
        assert x["audiences"] == ["all_ai_bots"]
        assert all(x[k].strip() for k in ("context", "input", "response", "avoid"))
        assert not re.search(r"(?i)https?://|@\\w+|\\b\\d{9,}\\b|(?:api[_-]?key|access[_-]?token)\\s*[:=]", str(x))
        assert any(hit[0] == x["id"] for hit in search.search(x["input"], audience="all_ai_bots", limit=20)), x["id"]
    print(f"T51_SOCIAL_OK new={len(rows)} total={len(data['cases'])}")
if __name__ == "__main__":
    main()
