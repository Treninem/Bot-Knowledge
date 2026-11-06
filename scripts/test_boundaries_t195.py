"""T195: 31 contextual boundary intents, 93 new reviewed synthetic suggestions.

Staged only: no consumer activation, sanctions, secrets or implicit actions.
"""
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector

ROOT = Path(__file__).resolve().parents[1]
STAGE = "staging/ru/boundaries_t167_context_pool.json"
SRC = "packs/ru/response_boundaries_qa.json"
SECRET = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|bearer\s+|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")

def norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold().replace("ё", "е")
    return " ".join("".join(
        " " if unicodedata.category(ch)[0] in ("P", "S") else ch
        for ch in text
    ).split())

def main():
    manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
    source = (ROOT / SRC).read_bytes()
    expected = next(p["sha256"] for p in manifest["packs"] if p["path"] == SRC)
    assert hashlib.sha256(source).hexdigest() == expected
    registered = json.loads(source)["records"]
    data = json.loads((ROOT / STAGE).read_text("utf-8"))
    assert STAGE not in {p["path"] for p in manifest["packs"]}
    assert data["source_pack"] == SRC and data["consumer_registered"] is False
    assert data["source_pack_manifest_sha256"] == expected
    assert data["source_pack_blob_sha"] == hashlib.sha1(
        b"blob " + str(len(source)).encode() + b"\0" + source).hexdigest()
    assert data["constraints"] == {
        "read_only": True, "requires_direct_address": True, "no_personal_data": True
    }
    checkpoint = data["checkpoint"]
    assert checkpoint["updated_in"] == "T203"
    assert checkpoint["latest_base_main_sha"] == "4e1f7b38e86bf0d9e6e7ed273b2bb8848185d1c4"
    assert checkpoint["registered_count"] == 279
    assert checkpoint["added_candidates"] == 1271
    assert checkpoint["latest_added"] == 62 and checkpoint["latest_rejected"] == 0
    assert checkpoint["partial_intents"] == 31 and checkpoint["finished_100"] == 0
    assert checkpoint["per_intent_total"] == 50
    assert checkpoint["remaining_per_intent"] == 50
    assert checkpoint["remaining_total"] == 1550
    assert len(data["entries"]) == len(registered) == 31

    ids, texts, newest = set(), set(), []
    selector = StagedContextSelector(ROOT, STAGE)
    for original, entry in zip(registered, data["entries"]):
        assert original["id"] == entry["intent_id"]
        assert original["question"] == entry["question"]
        assert entry["registered_reply_count"] == 9
        assert entry["staged_reply_count"] == len(entry["replies"]) == 41
        fresh = [r for r in entry["replies"] if "_t195_" in r["id"]]
        assert len(fresh) == 3
        assert {r["id"] for r in fresh} == {
            entry["intent_id"] + "_t195_01",
            entry["intent_id"] + "_t195_02",
            entry["intent_id"] + "_t195_03",
        }
        note_keys = set()
        tokens = []
        for r in entry["replies"]:
            assert r["id"].startswith(entry["intent_id"] + "_")
            assert r["id"] not in ids
            ids.add(r["id"])
            assert r["language"] == "ru" and r["style"] == "neutral"
            assert r["audiences"] == ["all_ai_bots"] and r["read_only"] is True
            assert r["context"] in {"direct", "private", "group_addressed"}
            assert r["context_note"].strip() and r["avoid"].strip()
            assert not SECRET.search(r["text"])
            n = norm(r["text"])
            assert 0 < len(r["text"]) <= 1600 and n not in texts
            texts.add(n)
            note = norm(r["context_note"])
            assert note and note not in note_keys
            note_keys.add(note)
            t = set(n.split())
            for old in tokens:
                assert len(t & old) / len(t | old) < 0.78
            tokens.append(t)
        for r in fresh:
            approved = frozenset({r["id"]})
            params = dict(intent_id=entry["intent_id"], approved_reply_ids=approved,
                          audience="all_ai_bots", context=r["context"],
                          addressed=True, local_permission=True)
            result = selector.select(**params)
            assert result is not None and result.text == r["text"]
            assert selector.select(**{**params, "approved_reply_ids": frozenset()}) is None
            assert selector.select(**{**params, "addressed": False}) is None
            assert selector.select(**{**params, "local_permission": False}) is None
            assert selector.select(**{**params, "audience": "community_bots"}) is None
            for other_ctx in {"direct", "private", "group_addressed"} - {r["context"]}:
                assert selector.select(**{**params, "context": other_ctx}) is None
            newest.append(norm(r["text"]))
    assert len(newest) == 93 and len(texts) == 1271

    # No exact normalized copy from registered QA packages (not just the source pack).
    for entry in manifest["packs"]:
        if not entry["path"].endswith("_qa.json"):
            continue
        other = json.loads((ROOT / entry["path"]).read_text("utf-8"))
        for record in other.get("records", []):
            for reply in [record["answer"], *record.get("variants", [])]:
                assert norm(reply) not in newest
    print("T195 PASS: 31 intents, +93 T195 staged, 1271 cumulative unique; scope, opt-in and registered QA isolation")

if __name__ == "__main__":
    main()
