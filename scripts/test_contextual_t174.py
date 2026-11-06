"""T174/T177: three supplemental pools, actual incremental counts and isolation.

No consumer activation, moderation actions, private messages or implicit approvals.
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECS = {
    "staging/ru/choice_t166_context_pool.json": (30, 9, 35, 1, 1680),
    "staging/ru/recovery_t168_context_pool.json": (24, 9, 33, 1, 1392),
    "staging/ru/boundaries_t167_context_pool.json": (31, 9, 36, 2, 1705),
}
SENSITIVE = re.compile(
    r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|"
    r"user_id|bearer\s+|https://t\.me/|"
    r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})"
)

def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join("".join(
        " " if unicodedata.category(c)[0] in {"P", "S"} else c for c in value
    ).split())


def main():
    manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
    registered = {v["path"] for v in manifest["packs"]}
    all_stage = []
    fresh = []
    identifiers = set()
    for path, (intents, base, stage_expected, new_each, remaining) in SPECS.items():
        assert path not in registered, path
        stage = json.loads((ROOT / path).read_text("utf-8"))
        checkpoint = stage["checkpoint"]
        assert checkpoint["base_main_sha"] == "309e5edd22f8ca4a6dcf59a4b2213a4c8696d36b"
        assert checkpoint["updated_in"] == ("T197" if "boundaries_" in path else "T193")
        assert checkpoint["latest_base_main_sha"] == ("0e9060cfcebdd735a9313c987a65854a39b28b80" if "boundaries_" in path else "4ae36975a4c209a3681b8f2f7e7fc1bd39ab8f8d")
        assert checkpoint["registered_count"] == intents * base
        assert checkpoint["added_candidates"] == intents * stage_expected
        assert checkpoint["latest_added"] == intents * new_each
        assert checkpoint["latest_rejected"] == 0
        assert checkpoint["remaining_total"] == remaining
        assert checkpoint["remaining_per_intent"] == 100 - base - stage_expected
        assert checkpoint["partial_intents"] == intents
        assert checkpoint["finished_100"] == 0
        assert len(stage["entries"]) == intents
        assert stage["audiences"] == ["all_ai_bots"]
        assert stage["constraints"] == {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
        for row in stage["entries"]:
            assert row["registered_reply_count"] == base
            assert row["staged_reply_count"] == stage_expected == len(row["replies"])
            new = [r for r in row["replies"] if ("_t197_" in r["id"] if "boundaries_" in path else "_t193_" in r["id"])]
            assert len(new) == new_each, row["intent_id"]
            assert len({r["context_note"] for r in new}) == new_each
            # Different wording alone is not a distinct context. Stop repeated
            # scenarios in one canonical intent, even when reply texts differ.
            context_notes = [norm(r["context_note"]) for r in row["replies"]]
            assert len(set(context_notes)) == len(context_notes), row["intent_id"]
            # Lexical near-duplicate guard complements, never replaces,
            # editorial semantic review of the synthetic replies.
            seen_tokens = []
            for r in row["replies"]:
                words = set(norm(r["text"]).split())
                for earlier in seen_tokens:
                    assert len(words & earlier) / len(words | earlier) < 0.78, row["intent_id"]
                seen_tokens.append(words)
            for r in row["replies"]:
                assert r["id"].startswith(row["intent_id"] + "_")
                assert r["id"] not in identifiers, r["id"]
                identifiers.add(r["id"])
                assert r["language"] == "ru" and r["style"] == "neutral"
                assert r["audiences"] == ["all_ai_bots"] and r["read_only"] is True
                assert r["context"] in {"direct", "private", "group_addressed"}
                assert r["context_note"].strip() and r["avoid"].strip()
                assert not SENSITIVE.search(r["text"])
                assert 0 < len(r["text"]) <= 1600
                all_stage.append(r["text"])
            fresh.extend(r["text"] for r in new)
    assert len(fresh) == 116 and len(all_stage) == 2958
    assert len({norm(t) for t in all_stage}) == len(all_stage)
    all_registered = set()
    for pack in manifest["packs"]:
        if not pack["path"].endswith("_qa.json"):
            continue
        obj = json.loads((ROOT / pack["path"]).read_text("utf-8"))
        for row in obj.get("records", []):
            all_registered.update(norm(t) for t in [row["answer"], *row.get("variants", [])])
    assert set(map(norm, all_stage)).isdisjoint(all_registered)
    print("T197 PASS: 62 new boundaries + 54 prior latest across 85 intents, 2958 staged unique; registered cross-pack exact dedup")


if __name__ == "__main__":
    main()
