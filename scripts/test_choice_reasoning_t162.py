"""T162: universal choice reasoning is SHA-checked, scoped, private, and searchable."""
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question

ROOT = Path(__file__).resolve().parents[1]
PATH = "packs/ru/choice_reasoning_qa.json"

def norm(s):
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join("".join(
        " " if unicodedata.category(c)[0] in ("P", "S") else c for c in s
    ).split())

def main():
    data = (ROOT / PATH).read_bytes()
    pack = json.loads(data)
    manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
    assert hashlib.sha256(data).hexdigest() == next(
        x["sha256"] for x in manifest["packs"] if x["path"] == PATH)
    assert validate_qa_pack(pack) == 14
    assert pack["catalog"]["audiences"] == ["all_ai_bots"]
    rows = pack["records"]
    assert len(rows) == 14 and len({r["id"] for r in rows}) == 14
    assert all(len(r["variants"]) == 5 for r in rows)
    assert all(r["audiences"] == ["all_ai_bots"] and
               set(r["contexts"]) == {"direct", "private", "group_addressed"}
               for r in rows)
    assert all(r["constraints"] == {"read_only": True,
                                      "requires_direct_address": True,
                                      "no_personal_data": True} for r in rows)
    answers = [s for r in rows for s in [r["answer"], *r["variants"]]]
    assert len(answers) == 84 and len({norm(s) for s in answers}) == 84
    assert not any(re.search(
        r"(?i)(ghp_|sk-|bot_token|chat_id|user_id|bearer\\s+)", s
    ) for s in answers)
    from scripts.search_knowledge import KnowledgeSearch
    index = KnowledgeSearch(ROOT)
    for r in rows:
        for context in ("direct", "private", "group_addressed"):
            hits = index.search(
                r["question"], audience="all_ai_bots", limit=20,
                context=context)
            assert any(h[0] == r["id"] and h[1] == PATH for h in hits), (r["id"], context)
    questions = {normalize_question(r["question"]) for r in rows}
    answer_keys = {norm(x) for x in answers}
    for entry in manifest["packs"]:
        p = entry["path"]
        if p == PATH or not p.endswith("_qa.json"):
            continue
        other = json.loads((ROOT / p).read_text("utf-8"))
        for r in other.get("records", []):
            assert not questions.intersection(
                normalize_question(s) for s in [r["question"], *r.get("aliases", [])]), p
            assert not answer_keys.intersection(
                norm(s) for s in [r["answer"], *r.get("variants", [])]), p
    print("T162 PASS: 14 original choice intents, 84 distinct replies, SHA and scoped search")

if __name__ == "__main__":
    main()
