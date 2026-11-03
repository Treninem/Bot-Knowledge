"""T46: 48 synthetic contextual replies, exact manifest SHA, safe scopes and retrieval."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question

ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/social_dialogues.json"

def main():
    raw = (ROOT / REL).read_bytes()
    pack = json.loads(raw)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    sha = next(p["sha256"] for p in manifest["packs"] if p["path"] == REL)
    assert hashlib.sha256(raw).hexdigest() == sha
    assert len(raw) < 2 * 1024 * 1024
    rows = [x for x in pack["cases"] if x["id"].startswith("talk_t46_")]
    assert len(rows) == 48
    assert Counter(x["kind"] for x in rows) == dict.fromkeys(
        ("congratulations", "support", "humor", "profanity", "conversation", "creative"), 8
    )
    assert len({x["id"] for x in pack["cases"]}) == len(pack["cases"])
    for field in ("input", "response"):
        values = [normalize_question(x[field]) for x in pack["cases"]]
        assert len(values) == len(set(values)), field
    search = KnowledgeSearch()
    for x in rows:
        assert x["audiences"] == ["all_ai_bots"]
        assert all(x.get(k, "").strip() for k in ("context", "input", "response", "avoid"))
        assert not re.search(r"(?i)(?:api[_-]?key|access[_-]?token)\\s*[:=]|https?://|@\\w+|\\b\\d{9,}\\b", str(x))
        assert any(h[0] == x["id"] for h in search.search(
            x["input"], audience="all_ai_bots", limit=20
        )), x["id"]
    print(f"T46_SOCIAL_OK rows={len(rows)} pack_bytes={len(raw)} sha256={sha}")

if __name__ == "__main__":
    main()
