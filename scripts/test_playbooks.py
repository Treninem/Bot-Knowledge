"""Ten deterministic offline rounds checking skill package boundaries and audiences.

This is *structural* coverage, not a claim of model understanding or live
moderation accuracy. Synthetic chats only, no third-party API calls.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIENCES = {"all_ai_bots", "chat_moderators", "community_bots"}
EXPECTED_TESTS = [
    ("celebrate_birthday", "all_ai_bots"),
    ("support_grief", "all_ai_bots"),
    ("deescalate", "all_ai_bots"),
    ("no_answer_mourning", "all_ai_bots"),
    ("no_answer_personal_chat", "all_ai_bots"),
    ("moderation_typo_safe", "chat_moderators"),
    ("moderation_masked_profanity", "chat_moderators"),
    ("moderation_profanity_allowed", "chat_moderators"),
    ("moderation_fake_payment", "chat_moderators"),
    ("bot_help_games", "community_bots"),
    ("bot_help_privacy", "community_bots"),
]

def read_pack(name: str) -> dict:
    payload = (ROOT / "packs/ru" / name).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    expected = next(row["sha256"] for row in manifest["packs"]
                    if row["path"] == "packs/ru/" + name)
    assert hashlib.sha256(payload).hexdigest() == expected, name
    return json.loads(payload)


def main() -> None:
    skills = read_pack("skills.json")
    styles = read_pack("styles.json")
    by_id = {row["id"]: row for row in skills["skills"]}
    assert len(by_id) == len(skills["skills"])
    assert len(by_id) >= 100
    assert len(styles["styles"]) >= 12
    assert skills["usage_policy"]["user_data_allowed"] is False
    assert skills["usage_policy"]["automatic_sanctions_allowed"] is False
    assert skills["usage_policy"]["scope_filter_required"] is True
    sample_count = sum(len(x["examples"]) for x in by_id.values())
    assert sample_count >= 300

    # Public repo content must not include visible identifiers in templates.
    private_markers = [
        re.compile(r"(?<!\\w)@[A-Za-z0-9_]{4,32}\\b"),
        re.compile(r"(?<!\\d)\\d{12,19}(?!\\d)"),
        re.compile(r"(?i)\\bhttps?://\\S+"),
        re.compile(r"(?i)\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}\\b"),
    ]
    for skill in by_id.values():
        assert set(skill["audiences"]) <= AUDIENCES
        assert skill["audiences"], skill["id"]
        assert skill["kind"] in {"social", "moderation_language", "bot_help"}
        assert all(len(x) <= 300 for x in skill["examples"])
        for sample in skill["examples"]:
            assert not any(p.search(sample) for p in private_markers), skill["id"]

    # Filter by audience before applying local safety and chat policy.
    for i in range(1, 11):
        for skill_id, audience in EXPECTED_TESTS:
            item = by_id[skill_id]
            assert audience in item["audiences"]
            # AuroraFox imports only portable conversation skills, not chat sanctions.
            if audience != "all_ai_bots":
                assert "all_ai_bots" not in item["audiences"]
            if item["kind"] == "moderation_language":
                assert "automatic_sanctions_allowed" not in item
                assert "action" not in item and "auto_apply" not in item
        assert by_id["choose_silence"]["examples"] == []
        print(f"PLAYBOOK_TEST_PASS {i}/10 skills={len(by_id)} samples={sample_count}", flush=True)
    print("PLAYBOOK_10_ROUNDS_OK", flush=True)


if __name__ == "__main__":
    main()
