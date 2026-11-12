"""T41 source-grounded ImPULS public help: 30 questions, 90 distinct responses."""
import hashlib
import json
import re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import validate_qa_pack

ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/impuls_help_qa.json"

def normalize(text):
    return " ".join(re.findall(r"[^\W_]+", text.casefold().replace("ё", "е")))

def main():
    data = (ROOT / REL).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    pack = json.loads(data)
    assert hashlib.sha256(data).hexdigest() == next(
        x["sha256"] for x in manifest["packs"] if x["path"] == REL
    )
    assert len(data) < 2 * 1024 * 1024
    assert validate_qa_pack(pack) == len(pack["records"])
    old = [r for r in pack["records"] if not r["id"].startswith("help_t41_")]
    rows = [r for r in pack["records"] if r["id"].startswith("help_t41_")]
    assert len(rows) == 30
    assert {r["id"] for r in rows} == {f"help_t41_{i:03d}" for i in range(1, 31)}
    assert len(pack["records"]) == len({r["id"] for r in pack["records"]})
    assert len(rows) * 3 == sum(1 + len(r["variants"]) for r in rows) == 90
    old_q = {normalize(v) for r in old for v in [r["question"], *r.get("aliases", [])]}
    old_a = {normalize(v) for r in old for v in [r["answer"], *r.get("variants", [])]}
    qs = [normalize(v) for r in rows for v in [r["question"], *r["aliases"]]]
    answers = [normalize(v) for r in rows for v in [r["answer"], *r["variants"]]]
    assert len(qs) == len(set(qs)) == 90
    assert len(answers) == len(set(answers)) == 90
    assert not old_q.intersection(qs)
    assert not old_a.intersection(answers)
    index = KnowledgeSearch()
    for r in rows:
        assert r["audiences"] == ["impuls"]
        assert r["contexts"] == ["direct", "private", "group_addressed"]
        assert r["language"] == "ru"
        assert r["constraints"] == {
            "read_only": True, "requires_direct_address": True, "no_personal_data": True
        }
        assert len(r["aliases"]) == 2 and len(r["variants"]) == 2
        assert not re.search(r"@\w+|\b\d{9,}\b|(?:access_token|api_key)\s*[:=]", str(r), re.I)
        for q in [r["question"], *r["aliases"]]:
            hits = index.search(q, audience="impuls", limit=20)
            assert any(hit[0] == r["id"] for hit in hits), (r["id"], q)
            assert all(hit[0] != r["id"] for hit in index.search(
                q, audience="all_ai_bots", limit=20
            )), r["id"]
    print(f"T41_IMPULS_HELP_OK records={len(rows)} searches={len(qs)} bytes={len(data)}")

if __name__ == "__main__":
    main()
