"""T29 universal dialogue QA: full-pack duplicate, scope, SHA and retrieval."""
import hashlib
import json
import re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "dlg_t29_"
COUNT = 30

def main():
    rel = "packs/ru/dialogue_help_qa.json"
    raw = (ROOT / rel).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == next(x["sha256"] for x in manifest["packs"] if x["path"] == rel)
    assert len(raw) < 1024 * 1024
    data = json.loads(raw)
    assert validate_qa_pack(data) == len(data["records"])
    chosen = [r for r in data["records"] if r["id"].startswith(PREFIX)]
    assert len(chosen) == COUNT
    assert len({r["id"] for r in data["records"]}) == len(data["records"])
    qs = [normalize_question(p) for r in data["records"] for p in (r["question"], *r["aliases"])]
    assert len(qs) == len(set(qs))
    index = KnowledgeSearch()
    for r in chosen:
        assert r["audiences"] == ["all_ai_bots"]
        assert r["contexts"] == ["direct", "private", "group_addressed"]
        assert r["language"] == "ru" and len(r["aliases"]) == 2 and len(r["variants"]) == 2
        assert all(s.strip() for s in (r["answer"], *r["variants"]))
        assert not re.search(r"(?:@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=])", str(r), re.I)
        for query in [r["question"], *r["aliases"]]:
            assert any(hit[0] == r["id"] for hit in index.search(query, audience="all_ai_bots", limit=20)), (r["id"], query)
    print("T29_DIALOGUE_OK questions=30 answers=90 aliases=60 sha256=%s" % hashlib.sha256(raw).hexdigest())

if __name__ == "__main__":
    main()
