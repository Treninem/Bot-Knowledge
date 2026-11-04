"""T74: 41 distinct original RU QA, exact SHA, scope, retrieval, regressions."""
import hashlib
import json
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question, validate_qa_pack
from scripts.search_knowledge import KnowledgeSearch
ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/dialogue_help_qa.json"
PREFIX = "dlg_t74_"
EXPECTED = 41
def main():
    payload = (ROOT / REL).read_bytes()
    assert len(payload) < 1024 * 1024
    manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
    assert hashlib.sha256(payload).hexdigest() == next(x["sha256"] for x in manifest["packs"] if x["path"] == REL)
    pack = json.loads(payload)
    assert validate_qa_pack(pack) == len(pack["records"])
    assert len(pack["records"]) == 749 + EXPECTED
    rows = [r for r in pack["records"] if r["id"].startswith(PREFIX)]
    assert len(rows) == EXPECTED
    assert len(set(r["id"] for r in pack["records"])) == len(pack["records"])
    all_queries = [normalize_question(v) for r in pack["records"] for v in (r["question"], *r["aliases"])]
    assert len(all_queries) == len(set(all_queries))
    answers = [normalize_question(v) for r in rows for v in (r["answer"], *r["variants"])]
    assert len(answers) == len(set(answers))
    search = KnowledgeSearch()
    for r in rows:
        assert len(r["aliases"]) == 2 and len(r["variants"]) == 2
        assert r["audiences"] == ["all_ai_bots"] and r["contexts"] == ["direct","private","group_addressed"]
        assert r["constraints"] == {"read_only":True,"requires_direct_address":True,"no_personal_data":True}
        assert r["language"] == "ru" and "REQUIREMENTS_21.md" in r["source"]
        assert not set(r) & {"action","sanction","auto_apply","execute","ban","mute"}
        hits = search.search(r["question"],audience="all_ai_bots",limit=30)
        assert any(hit[0] == r["id"] for hit in hits),r["id"]
    print(f"T74 QA PASS: {EXPECTED} records, {EXPECTED*3} answers")
if __name__ == "__main__":
    main()
