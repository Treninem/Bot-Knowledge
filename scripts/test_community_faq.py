"""Ten offline synthetic, audience-scoped FAQ regression scenarios; no bot side effects."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from search_knowledge import KnowledgeSearch

REL = "packs/ru/community_faq_checks.json"
EXPECTED = {
    "bot_help_antispam_settings_faq": "как настроить антиспам в чате",
    "bot_help_family_game_faq": "как работает семейная игра",
    "bot_help_free_raffle_faq": "как участвовать в бесплатном розыгрыше",
}


def read_checked_pack() -> tuple[dict, dict]:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    matches = [p for p in manifest["packs"] if p["path"] == REL]
    assert len(matches) == 1, "FAQ pack must appear once in manifest"
    raw = (ROOT / REL).read_bytes()
    assert len(raw) < 12 * 1024
    assert hashlib.sha256(raw).hexdigest() == matches[0]["sha256"], "FAQ SHA mismatch"
    return manifest, json.loads(raw)


def inspect_pack() -> None:
    manifest, pack = read_checked_pack()
    assert manifest["knowledge_version"] == pack["pack_version"]
    assert pack["schema_version"] == 1 and pack["language"] == "ru"
    policy = pack["usage_policy"]
    required_policy = {
        "synthetic_examples_only": True,
        "user_data_allowed": False,
        "automatic_actions_allowed": False,
        "automatic_sanctions_allowed": False,
        "scope_filter_required": True,
        "consumer_feature_check_required": True,
        "publication_requires_review": True,
    }
    assert policy == required_policy
    original = json.loads((ROOT / "packs/ru/skills.json").read_text(encoding="utf-8"))["skills"]
    old_ids = {s["id"] for s in original}
    old_examples = {" ".join(p.casefold().split()) for s in original for p in s["examples"]}
    assert {"bot_help_chat_settings", "bot_help_rules", "bot_help_reports", "respond_to_thanks"} <= old_ids
    skills = pack["skills"]
    assert len(skills) == 3
    assert {s["id"] for s in skills} == set(EXPECTED)
    assert not old_ids.intersection(EXPECTED)
    all_examples = []
    for item in skills:
        assert item["kind"] == "bot_help"
        assert item["audiences"] == ["community_bots"]
        assert item["when"] == [EXPECTED[item["id"]]]
        assert len(item["avoid"]) == 3 and len(item["examples"]) == 1
        assert all(4 <= len(v) <= 180 for k in ("when", "avoid", "examples") for v in item[k])
        assert not {"action", "auto_apply", "command", "api_call", "sanction"}.intersection(item)
        all_examples.extend(item["examples"])
    normalized = [" ".join(v.casefold().split()) for v in all_examples]
    assert len(set(normalized)) == len(normalized)
    assert not old_examples.intersection(normalized)
    for message in [*all_examples, *(s for item in skills for field in ("when", "avoid") for s in item[field])]:
        assert not re.search(r"(?i)https?://|@[a-z0-9_]{4,32}\b|\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", message)
        assert not re.search(r"(?<!\d)\d{12,19}(?!\d)", message)
    assert "права" in skills[0]["examples"][0]
    assert "добровольные" in skills[1]["examples"][0]
    assert "Если" in skills[2]["examples"][0]


def ten_scoped_rounds() -> None:
    index = KnowledgeSearch(ROOT)
    assert len(index.records) == 1182, len(index.records)  # 1179 baseline + 3 review-only FAQ cases
    # Each probe is a distinct permission/use-case; retrieval is NOT authorization.
    probes = [
        ("как настроить антиспам в чате", "community_bots", "bot_help_antispam_settings_faq", True),
        ("как работает семейная игра", "community_bots", "bot_help_family_game_faq", True),
        ("как участвовать в бесплатном розыгрыше", "community_bots", "bot_help_free_raffle_faq", True),
        ("как настроить антиспам в чате", "all_ai_bots", "bot_help_antispam_settings_faq", False),
        ("как работает семейная игра", "all_ai_bots", "bot_help_family_game_faq", False),
        ("как участвовать в бесплатном розыгрыше", "all_ai_bots", "bot_help_free_raffle_faq", False),
        ("как настроить антиспам в чате", "chat_moderators", "bot_help_antispam_settings_faq", False),
        ("как работает семейная игра", "chat_moderators", "bot_help_family_game_faq", False),
        ("как участвовать в бесплатном розыгрыше", "chat_moderators", "bot_help_free_raffle_faq", False),
        ("Правила этого чата задаёт его администрация", "community_bots", "bot_help_rules", True),
    ]
    for n, (query, audience, skill_id, should_find) in enumerate(probes, 1):
        matches = {result[0] for result in index.search(query, audience, limit=20)}
        assert (skill_id in matches) is should_find, (n, audience, skill_id, matches)
        print(f"COMMUNITY_FAQ_ROUND_PASS {n}/10 audience={audience}")


def sha_and_version_invalidation() -> None:
    raw = (ROOT / REL).read_bytes()
    with tempfile.TemporaryDirectory(prefix="synthetic-faq-") as scratch:
        root = Path(scratch)
        target = root / REL
        target.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / REL, target)
        minimal_manifest = {"schema_version": 1, "language": "ru", "knowledge_version": "v1", "packs": [{"path": REL, "sha256": hashlib.sha256(raw).hexdigest()}]}
        (root / "manifest.json").write_text(json.dumps(minimal_manifest), encoding="utf-8")
        before = KnowledgeSearch(root)
        assert "bot_help_family_game_faq" in {x[0] for x in before.search(EXPECTED["bot_help_family_game_faq"], "community_bots", 20)}
        altered = json.loads(raw)
        altered["skills"][1]["examples"][0] += " Доступность зависит от чата."
        replacement = (json.dumps(altered, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        target.write_bytes(replacement)
        try:
            KnowledgeSearch(root)
        except ValueError as exc:
            assert "SHA mismatch" in str(exc)
        else:
            raise AssertionError("tampering should invalidate the snapshot")
        minimal_manifest["packs"][0]["sha256"] = hashlib.sha256(replacement).hexdigest()
        minimal_manifest["knowledge_version"] = "v2"
        (root / "manifest.json").write_text(json.dumps(minimal_manifest), encoding="utf-8")
        after = KnowledgeSearch(root)
        assert after.records[1]["preview"] != before.records[1]["preview"]
        assert before.records[1]["preview"] not in ("", after.records[1]["preview"])
        print("COMMUNITY_FAQ_SHA_CACHE_INVALIDATION_PASS")


def main() -> None:
    inspect_pack()
    ten_scoped_rounds()
    sha_and_version_invalidation()
    print("COMMUNITY_FAQ_SYNTHETIC_TESTS_PASS")


if __name__ == "__main__":
    main()
