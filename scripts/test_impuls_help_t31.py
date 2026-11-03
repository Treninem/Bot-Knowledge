"""T31: source-grounded ImPULS help, exact manifest hash, privacy and bounded search."""
import hashlib
import json
import re
from pathlib import Path

from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "help_t31_"
COUNT = 24


def main() -> None:
    rel = "packs/ru/impuls_help_qa.json"
    raw = (ROOT / rel).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    expected = next(x["sha256"] for x in manifest["packs"] if x["path"] == rel)
    assert hashlib.sha256(raw).hexdigest() == expected
    assert len(raw) < 1024 * 1024, "qa.v1 one MiB limit"

    pack = json.loads(raw)
    assert validate_qa_pack(pack) == len(pack["records"])
    selected = [r for r in pack["records"] if r["id"].startswith(PREFIX)]
    assert len(selected) == COUNT
    assert {r["id"] for r in selected} == {f"{PREFIX}{i:03d}" for i in range(1, COUNT + 1)}
    assert len({r["id"] for r in pack["records"]}) == len(pack["records"])
    phrases = [
        normalize_question(p)
        for r in pack["records"]
        for p in (r["question"], *r["aliases"])
    ]
    assert len(set(phrases)) == len(phrases)

    search = KnowledgeSearch()
    for r in selected:
        assert r["audiences"] == ["impuls"]
        assert r["contexts"] == ["direct", "private", "group_addressed"]
        assert r["constraints"] == {
            "read_only": True, "requires_direct_address": True, "no_personal_data": True
        }
        assert r["language"] == "ru"
        assert len(r["aliases"]) == len(r["variants"]) == 2
        assert all(x.strip() for x in [r["answer"], *r["variants"]])
        assert not re.search(
            r"(?:@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=])",
            str([r["question"], r["aliases"], r["answer"], r["variants"]]),
            re.IGNORECASE,
        )
        for query in [r["question"], *r["aliases"]]:
            assert any(hit[0] == r["id"] for hit in search.search(query, audience="impuls", limit=20)), (r["id"], query)
            assert all(hit[0] != r["id"] for hit in search.search(query, audience="all_ai_bots", limit=20))
    print(f"T31_IMPULS_OK questions={COUNT} answers={COUNT * 3} aliases={COUNT * 2} sha256={expected}")


if __name__ == "__main__":
    main()
