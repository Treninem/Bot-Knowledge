"""T27 practical ImPULS FAQ: integrity, privacy and source-scoped retrieval."""
import hashlib
import json
import re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question

ROOT = Path(__file__).resolve().parents[1]
COUNT = 30
PREFIX = "help_t27_"

def main():
    rel = "packs/ru/impuls_help_qa.json"
    raw = (ROOT / rel).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == next(e["sha256"] for e in manifest["packs"] if e["path"] == rel)
    assert len(raw) < 1024 * 1024
    pack = json.loads(raw)
    assert validate_qa_pack(pack) == len(pack["records"])
    records = [r for r in pack["records"] if r["id"].startswith(PREFIX)]
    assert len(records) == COUNT
    assert len({r["id"] for r in pack["records"]}) == len(pack["records"])
    normalized = [normalize_question(p) for r in pack["records"] for p in (r["question"], *r.get("aliases", []))]
    assert len(normalized) == len(set(normalized))
    index = KnowledgeSearch()
    for r in records:
        assert r["audiences"] == ["impuls"]
        assert r["contexts"] == ["direct", "private", "group_addressed"]
        assert r["constraints"] == {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
        assert r["language"] == "ru" and len(r["aliases"]) == 2 and len(r["variants"]) == 2
        assert all(isinstance(s, str) and s.strip() for s in [r["answer"], *r["variants"]])
        assert not re.search(r"(?:@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=])", str([r["question"], r["aliases"], r["answer"], r["variants"]]), re.I)
        for phrase in [r["question"], *r["aliases"]]:
            assert any(hit[0] == r["id"] for hit in index.search(phrase, audience="impuls", limit=20)), (r["id"], phrase)
            assert all(hit[0] != r["id"] for hit in index.search(phrase, audience="all_ai_bots", limit=20))
    print("T27_IMPULS_OK questions=30 answers=90 aliases=60 sha256=" + hashlib.sha256(raw).hexdigest())

if __name__ == "__main__":
    main()
