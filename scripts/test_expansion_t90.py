"""T90: additive QA coverage with immutable source, read-only audience and scoped search."""
import hashlib
import json
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question, validate_qa_pack
from scripts.search_knowledge import KnowledgeSearch

ROOT = Path(__file__).resolve().parents[1]
NEW = {"packs/ru/conversation_followthrough_qa.json": ("follow_t90_", 57, 25),
       "packs/ru/structured_information_qa.json": ("struct_t90_", 64, 25)}
EXPECTED_SCOPE = {"read_only": True, "requires_direct_address": True, "no_personal_data": True}

def main():
    manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
    lookup = {entry["path"]: entry["sha256"] for entry in manifest["packs"]}
    index = KnowledgeSearch()
    queries, answers = set(), set()
    all_ids = set()
    for path in lookup:
        file = ROOT / path
        raw = file.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == lookup[path], path
        data = json.loads(raw)
        if data.get("catalog", {}).get("adapter") != "qa.v1":
            continue
        for record in data["records"]:
            assert record["id"] not in all_ids, record["id"]
            all_ids.add(record["id"])
            for q in [record["question"], *record.get("aliases", [])]:
                v = normalize_question(q)
                assert v not in queries, ("duplicate_query", path, v)
                queries.add(v)
            if path in NEW:
                for a in [record["answer"], *record["variants"]]:
                    v = normalize_question(a)
                    assert v not in answers, ("duplicate_answer", path, v)
                    answers.add(v)
        if path not in NEW:
            continue
        prefix, existing, added = NEW[path]
        assert len(raw) < 1024 * 1024
        assert validate_qa_pack(data) >= existing + added
        fresh = [r for r in data["records"] if r["id"].startswith(prefix)]
        assert len(fresh) == added
        assert [r["id"] for r in fresh] == [f"{prefix}{i:03d}" for i in range(1, added + 1)]
        for r in fresh:
            assert r["language"] == "ru"
            assert r["audiences"] == ["all_ai_bots"]
            assert r["contexts"] == ["direct", "private", "group_addressed"]
            assert r["constraints"] == EXPECTED_SCOPE
            assert len(r["aliases"]) == 2 and len(r["variants"]) == 2
            assert not {"action", "execute", "sanction", "auto_apply", "ban", "mute"} & set(r)
        for r in fresh[:5] + fresh[-5:]:
            assert any(hit[0] == r["id"] for hit in index.search(r["question"], audience="all_ai_bots", limit=20)), r["id"]
    print("T90 PASS: 50 canonical questions, 100 aliases, 150 context-scoped replies")

if __name__ == "__main__":
    main()
