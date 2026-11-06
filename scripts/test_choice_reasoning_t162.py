"""T162/T169/T172/T174: choice QA and staged contextual continuation are scoped and unique."""
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
    assert validate_qa_pack(pack) == 30
    assert pack["catalog"]["audiences"] == ["all_ai_bots"]
    rows = pack["records"]
    assert len(rows) == 30 and len({r["id"] for r in rows}) == 30
    assert all(len(r["variants"]) == 8 for r in rows)
    assert all(r["audiences"] == ["all_ai_bots"] and
               set(r["contexts"]) == {"direct", "private", "group_addressed"}
               for r in rows)
    assert all(r["constraints"] == {"read_only": True,
                                      "requires_direct_address": True,
                                      "no_personal_data": True} for r in rows)
    answers = [s for r in rows for s in [r["answer"], *r["variants"]]]
    assert len(answers) == 270 and len({norm(s) for s in answers}) == 270
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

    # T166 supplemental pool is deliberately NOT consumer-registered.
    stage_path = "staging/ru/choice_t166_context_pool.json"
    staging = json.loads((ROOT / stage_path).read_text("utf-8"))
    assert staging["schema_version"] == 1
    assert staging["stage_type"] == "supplemental_contextual_reply_pool"
    assert staging["source_pack"] == PATH and staging["consumer_registered"] is False
    assert staging["source_pack_manifest_sha256"] == hashlib.sha256(data).hexdigest()
    git_blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    assert staging["source_pack_blob_sha"] == git_blob
    assert stage_path not in {m["path"] for m in manifest["packs"]}
    assert staging["constraints"] == {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
    assert staging["audiences"] == ["all_ai_bots"] and staging["language"] == "ru"
    progress = staging["checkpoint"]
    assert progress["base_main_sha"] == "309e5edd22f8ca4a6dcf59a4b2213a4c8696d36b"
    assert progress["added_candidates"] == 1110 and progress["registered_count"] == 270
    assert progress["latest_added"] == 60 and progress["latest_rejected"] == 0
    assert progress["finished_100"] == 0 and progress["partial_intents"] == 30
    assert progress["remaining_total"] == 1620 and progress["remaining_per_intent"] == 54
    assert len(staging["entries"]) == 30
    additional = []
    ids = set()
    for original, entry in zip(rows, staging["entries"]):
        assert entry["intent_id"] == original["id"] and entry["question"] == original["question"]
        assert entry["registered_reply_count"] == 9 and entry["staged_reply_count"] == 37
        assert len(entry["replies"]) == 37
        assert sum(r["id"].startswith(entry["intent_id"] + "_t166_") for r in entry["replies"]) == 3
        assert sum(r["id"].startswith(entry["intent_id"] + "_t169_") for r in entry["replies"]) == 3
        assert sum(r["id"].startswith(entry["intent_id"] + "_t172_") for r in entry["replies"]) == 3
        assert sum(r["id"].startswith(entry["intent_id"] + "_t174_") for r in entry["replies"]) == 2
        assert sum(r["id"].startswith(entry["intent_id"] + "_t175_") for r in entry["replies"]) == 1
        assert sum(r["id"].startswith(entry["intent_id"] + "_t176_") for r in entry["replies"]) == 2
        assert sum(r["id"].startswith(entry["intent_id"] + "_t177_") for r in entry["replies"]) == 1
        assert sum(r["id"].startswith(entry["intent_id"] + "_t178_") for r in entry["replies"]) == 2
        assert sum(r["id"].startswith(entry["intent_id"] + "_t179_") for r in entry["replies"]) == 2
        assert sum(r["id"].startswith(entry["intent_id"] + "_t180_") for r in entry["replies"]) == 1
        assert sum(r["id"].startswith(entry["intent_id"] + "_t181_") for r in entry["replies"]) == 1
        assert sum(r["id"].startswith(entry["intent_id"] + "_t182_") for r in entry["replies"]) == 1
        assert sum(r["id"].startswith(entry["intent_id"] + "_t183_") for r in entry["replies"]) == 2
        assert sum(r["id"].startswith(entry["intent_id"] + "_t184_") for r in entry["replies"]) == 2
        assert sum(r["id"].startswith(entry["intent_id"] + "_t185_") for r in entry["replies"]) == 2
        for r in entry["replies"]:
            assert r["id"] not in ids and (r["id"].startswith(entry["intent_id"] + "_t166_") or r["id"].startswith(entry["intent_id"] + "_t169_") or r["id"].startswith(entry["intent_id"] + "_t172_") or r["id"].startswith(entry["intent_id"] + "_t174_") or r["id"].startswith(entry["intent_id"] + "_t175_") or r["id"].startswith(entry["intent_id"] + "_t176_") or r["id"].startswith(entry["intent_id"] + "_t177_") or r["id"].startswith(entry["intent_id"] + "_t178_") or r["id"].startswith(entry["intent_id"] + "_t179_") or r["id"].startswith(entry["intent_id"] + "_t180_") or r["id"].startswith(entry["intent_id"] + "_t181_") or r["id"].startswith(entry["intent_id"] + "_t182_") or r["id"].startswith(entry["intent_id"] + "_t183_") or r["id"].startswith(entry["intent_id"] + "_t184_") or r["id"].startswith(entry["intent_id"] + "_t185_") or r["id"].startswith(entry["intent_id"] + "_t186_") or r["id"].startswith(entry["intent_id"] + "_t189_") or r["id"].startswith(entry["intent_id"] + "_t190_") or r["id"].startswith(entry["intent_id"] + "_t191_") or r["id"].startswith(entry["intent_id"] + "_t192_") or r["id"].startswith(entry["intent_id"] + "_t193_") or r["id"].startswith(entry["intent_id"] + "_t199_"))
            ids.add(r["id"])
            assert r["language"] == "ru" and r["style"] == "neutral"
            assert r["context"] in {"direct", "private", "group_addressed"}
            assert r["audiences"] == ["all_ai_bots"] and r["read_only"] is True
            assert r["context_note"].strip() and r["avoid"].strip()
            assert len(r["text"]) <= 1600
            assert not re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})",r["text"])
            additional.append(r["text"])
    assert len(additional) == 1110
    assert len({norm(s) for s in answers + additional}) == 1380
    stage_keys = {norm(s) for s in additional}
    for entry in manifest["packs"]:
        p = entry["path"]
        if p == PATH or not p.endswith("_qa.json"):
            continue
        other = json.loads((ROOT / p).read_text("utf-8"))
        for record in other.get("records", []):
            assert not stage_keys.intersection(
                norm(s) for s in [record["answer"], *record.get("variants", [])]), p
    print("T199 PASS: 30 choice intents, 270 registered + 1110 staged; source SHA, privacy, scope and uniqueness")

if __name__ == "__main__":
    main()
