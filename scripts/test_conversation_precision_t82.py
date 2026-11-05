"""T82: original RU conversation QAs, normalized dedup, SHA and indexed access."""
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
    rows = pack["records"]
    assert len(rows) >= 42 + 42 and validate_qa_pack(pack) == len(rows)
    new = rows[42:84]
    assert [r["id"] for r in new] == ["precision_t82_%03d" % n for n in range(1, 43)]
    seen = set()
    answers = set()
    for info in manifest["packs"]:
        other = json.loads((ROOT / info["path"]).read_text("utf-8"))
        if other.get("catalog", {}).get("adapter") != "qa.v1":
            continue
        for r in other.get("records", []):
            for q in [r["question"], *r.get("aliases", [])]:
                n = normalize_question(q)
                assert n not in seen, ("duplicate_query", n)
                seen.add(n)
            if info["path"] == REL:
                for a in [r["answer"], *r.get("variants", [])]:
                    n = normalize_question(a)
                    assert n not in answers, ("duplicate_response", n)
                    answers.add(n)
    index = KnowledgeSearch()
    for r in new:
        assert r["audiences"] == ["all_ai_bots"]
        assert r["contexts"] == ["direct", "private", "group_addressed"]
        assert r["constraints"] == {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
        assert r["language"] == "ru" and len(r["aliases"]) == 2 and 3 <= len(r["variants"]) <= 8
        assert not (set(r) & {"execute", "action", "sanction", "mute", "ban", "auto_apply"})
        assert any(hit[0] == r["id"] for hit in index.search(r["question"], audience="all_ai_bots", limit=20)), r["id"]
    print("T82 PASS: 42 new intents, 84 aliases, 378 responses after T114")

if __name__ == "__main__":
    main()
