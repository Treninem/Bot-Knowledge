"""T85: RU conversation precision — manifest integrity, uniqueness, safety and retrieval."""
import hashlib
import json
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question, validate_qa_pack
from scripts.search_knowledge import KnowledgeSearch

ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/conversation_precision_qa.json"


def main():
    raw = (ROOT / REL).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
    expected = next(x["sha256"] for x in manifest["packs"] if x["path"] == REL)
    assert hashlib.sha256(raw).hexdigest() == expected
    assert len(raw) < 1024 * 1024
    pack = json.loads(raw)
    records = pack["records"]
    assert len(records) == 84 + 48 and validate_qa_pack(pack) == len(records)
    fresh = records[-48:]
    assert [r["id"] for r in fresh] == ["precision_t85_%03d" % n for n in range(1, 49)]
    queries, replies = set(), set()
    for info in manifest["packs"]:
        other = json.loads((ROOT / info["path"]).read_text("utf-8"))
        if other.get("catalog", {}).get("adapter") != "qa.v1":
            continue
        for record in other["records"]:
            for query in [record["question"], *record.get("aliases", [])]:
                normalized = normalize_question(query)
                assert normalized not in queries, ("duplicate_query", normalized)
                queries.add(normalized)
            if info["path"] == REL:
                for response in [record["answer"], *record.get("variants", [])]:
                    normalized = normalize_question(response)
                    assert normalized not in replies, ("duplicate_reply", normalized)
                    replies.add(normalized)
    index = KnowledgeSearch()
    for record in fresh:
        assert record["language"] == "ru" and record["audiences"] == ["all_ai_bots"]
        assert record["contexts"] == ["direct", "private", "group_addressed"]
        assert record["constraints"] == {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
        assert len(record["aliases"]) == 2 and 3 <= len(record["variants"]) <= 8
        assert not set(record).intersection({"execute", "action", "sanction", "mute", "ban", "auto_apply"})
        assert any(hit[0] == record["id"] for hit in index.search(record["question"], audience="all_ai_bots", limit=20)), record["id"]
    print("T85 PASS: 48 RU intents, 96 aliases, 432 replies after T114")

if __name__ == "__main__":
    main()
