"""N12: verify original universal QA and scoped social dialogue extensions."""
import hashlib
import json
import re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "manifest.json").read_text("utf-8"))

def verified(path):
    raw = (ROOT / path).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == next(
        e["sha256"] for e in MANIFEST["packs"] if e["path"] == path
    )
    return json.loads(raw)

def main():
    qa = verified("packs/ru/dialogue_help_qa.json")
    social = verified("packs/ru/social_dialogues.json")
    assert len((ROOT / "packs/ru/dialogue_help_qa.json").read_bytes()) < 1024 * 1024
    assert len((ROOT / "packs/ru/social_dialogues.json").read_bytes()) < 2 * 1024 * 1024
    assert validate_qa_pack(qa) == len(qa["records"])
    qrows = [r for r in qa["records"] if r["id"].startswith("dlg_n12_")]
    srows = [r for r in social["cases"] if r["id"].startswith("talk_n12_")]
    assert len(qrows) == 30
    assert len(srows) == 36
    assert len(set(r["id"] for r in qrows + srows)) == len(qrows + srows)
    assert len({normalize_question(r["input"]) for r in social["cases"]}) == len(social["cases"])
    assert len({normalize_question(r["response"]) for r in social["cases"]}) == len(social["cases"])
    search = KnowledgeSearch()
    checks = 0
    for r in qrows:
        assert r["audiences"] == ["all_ai_bots"] and r["language"] == "ru"
        assert len(r["aliases"]) == len(r["variants"]) == 2
        assert r["source"].startswith("https://github.com/Treninem/Bot-Knowledge/blob/1942da61d14e98fdb5dc0c95abd0470a0a4b1966/")
        for term in [r["question"], *r["aliases"]]:
            results = search.search(term, audience="all_ai_bots", limit=20)
            assert any(hit[0] == r["id"] for hit in results), (r["id"], term)
            checks += 1
    for r in srows:
        assert r["kind"] in {"conversation","congratulations","support","humor","profanity","creative"}
        assert r["audiences"] == ["all_ai_bots"] and r["context"] and r["avoid"]
        assert not re.search(r"(?i)https?://|@\\w+|\\b\\d{10,}\\b",str(r))
        results = search.search(r["input"], audience="all_ai_bots", limit=20)
        assert any(hit[0] == r["id"] for hit in results), (r["id"], r["input"])
        checks += 1
    print(f"N12_OK qa={len(qrows)} social={len(srows)} indexed_queries={checks}")

if __name__ == "__main__":
    main()
