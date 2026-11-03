"""T22 fact-scoped natural help: sources, alias retrieval, privacy and isolation."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "help_t22_"

def main() -> None:
    relative = "packs/ru/impuls_help_qa.json"
    raw = (ROOT / relative).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == next(x["sha256"] for x in manifest["packs"] if x["path"] == relative)
    assert len(raw) < 1024 * 1024
    pack = json.loads(raw)
    assert validate_qa_pack(pack) == len(pack["records"])
    new = [r for r in pack["records"] if r["id"].startswith(PREFIX)]
    assert len(new) == 24
    assert len({r["id"] for r in new}) == 24
    index = KnowledgeSearch()
    seen = set()
    for r in new:
        assert r["audiences"] == ["impuls"]
        assert r["contexts"] == ["direct", "private", "group_addressed"]
        assert r["constraints"] == {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
        assert len(r["aliases"]) == len(r["variants"]) == 2
        for field in ("question", "answer", "aliases", "variants"):
            assert not re.search(r"(?:@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=])", str(r[field]), re.I)
        for phrase in [r["question"], *r["aliases"]]:
            norm = normalize_question(phrase)
            assert norm not in seen
            seen.add(norm)
            hits = index.search(phrase, audience="impuls", limit=20)
            assert any(h[0] == r["id"] for h in hits), (r["id"], phrase)
            assert all(h[0] != r["id"] for h in index.search(phrase, audience="all_ai_bots", limit=20))
    print(f"T22_HELP_OK questions={len(new)} answers={len(new)*3} aliases={len(new)*2} sha256={hashlib.sha256(raw).hexdigest()}")

if __name__ == "__main__":
    main()
