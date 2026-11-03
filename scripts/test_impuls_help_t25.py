"""T25 natural ImPULS FAQ: hash, scope, full-pack dedup and local retrieval."""
import hashlib
import json
import re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "help_t25_"
COUNT = 22

def main():
    rel = "packs/ru/impuls_help_qa.json"
    raw = (ROOT / rel).read_bytes()
    man = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == next(x["sha256"] for x in man["packs"] if x["path"] == rel)
    assert len(raw) < 1024 * 1024
    rows = json.loads(raw)
    assert validate_qa_pack(rows) == len(rows["records"])
    selected = [r for r in rows["records"] if r["id"].startswith(PREFIX)]
    assert len(selected) == COUNT
    assert len({r["id"] for r in rows["records"]}) == len(rows["records"])
    keys = [normalize_question(x) for r in rows["records"] for x in [r["question"], *r.get("aliases", [])]]
    assert len(keys) == len(set(keys))
    index = KnowledgeSearch()
    for r in selected:
        assert r["audiences"] == ["impuls"]
        assert r["contexts"] == ["direct", "private", "group_addressed"]
        assert r["constraints"] == {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
        assert len(r["aliases"]) == len(r["variants"]) == 2
        assert not re.search(r"(?:@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=])", str([r["question"], r["aliases"], r["answer"], r["variants"]]), re.I)
        for phrase in [r["question"], *r["aliases"]]:
            assert any(hit[0] == r["id"] for hit in index.search(phrase, audience="impuls", limit=20)), (r["id"], phrase)
            assert all(hit[0] != r["id"] for hit in index.search(phrase, audience="all_ai_bots", limit=20))
    print("T25_IMPULS_OK questions=22 answers=66 aliases=44 sha256=%s" % hashlib.sha256(raw).hexdigest())

if __name__ == "__main__":
    main()
