"""Review-only, synthetic ImPULS FAQ checks: 10 distinct scenarios x 10 rounds."""
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

REL = "packs/ru/impuls_feature_faq_checks.json"
IDS = {
    "bot_help_pulse_journal_faq": "где найти журнал Пульсов",
    "bot_help_daily_word_chain_faq": "как найти ежедневную цепочку слов",
    "bot_help_selected_chat_access_faq": "почему после смены чата недоступны настройки",
}
POLICY = {
    "synthetic_examples_only": True,
    "user_data_allowed": False,
    "automatic_actions_allowed": False,
    "automatic_sanctions_allowed": False,
    "scope_filter_required": True,
    "consumer_feature_check_required": True,
    "publication_requires_review": True,
}


def normalized(text: str) -> str:
    return " ".join(re.findall(r"[a-zа-яё0-9]+", text.casefold().replace("ё", "е")))


def validate() -> tuple[dict, bytes]:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    registered = [entry for entry in manifest["packs"] if entry["path"] == REL]
    assert len(registered) == 1
    raw = (ROOT / REL).read_bytes()
    assert len(raw) < 12 * 1024
    assert hashlib.sha256(raw).hexdigest() == registered[0]["sha256"]
    pack = json.loads(raw)
    assert pack["schema_version"] == 1 and pack["language"] == "ru"
    assert pack["pack_version"] == manifest["knowledge_version"]
    assert pack["usage_policy"] == POLICY
    skills = pack["skills"]
    assert len(skills) == 3
    assert {x["id"] for x in skills} == set(IDS)
    existing = json.loads((ROOT / "packs/ru/skills.json").read_text(encoding="utf-8"))["skills"]
    old_ids = {x["id"] for x in existing}
    old_texts = {normalized(t) for x in existing for key in ("when", "examples")
                 for t in x.get(key, [])}
    assert not (set(IDS) & old_ids)
    new_texts = []
    for entry in skills:
        assert set(entry) == {"id", "kind", "when", "avoid", "examples", "audiences"}
        assert entry["kind"] == "bot_help" and entry["audiences"] == ["community_bots"]
        assert entry["when"] == [IDS[entry["id"]]]
        assert 1 <= len(entry["examples"]) <= 2
        assert 1 <= len(entry["avoid"]) <= 4
        for key in ("when", "avoid", "examples"):
            for value in entry[key]:
                assert 5 <= len(value) <= 300
                assert not re.search(r"https?://|@[A-Za-z0-9_]{4,32}\b|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?<!\d)\d{12,19}(?!\d)", value)
                if key != "avoid":
                    new_texts.append(normalized(value))
        assert not {"action", "auto_apply", "token", "sanction", "chat_id", "user_id"} & set(entry)
    assert len(new_texts) == len(set(new_texts))
    assert not old_texts.intersection(new_texts)
    return manifest, raw


def ten_rounds() -> None:
    index = KnowledgeSearch(ROOT)
    assert len(index.records) == 1182, len(index.records)  # 1179 baseline + exactly 3
    probes = [
        ("где найти журнал Пульсов", "community_bots", "bot_help_pulse_journal_faq", True),
        ("как найти ежедневную цепочку слов", "community_bots", "bot_help_daily_word_chain_faq", True),
        ("почему после смены чата недоступны настройки", "community_bots", "bot_help_selected_chat_access_faq", True),
        ("где найти журнал Пульсов", "all_ai_bots", "bot_help_pulse_journal_faq", False),
        ("как найти ежедневную цепочку слов", "all_ai_bots", "bot_help_daily_word_chain_faq", False),
        ("почему после смены чата недоступны настройки", "all_ai_bots", "bot_help_selected_chat_access_faq", False),
        ("где найти журнал Пульсов", "chat_moderators", "bot_help_pulse_journal_faq", False),
        ("как найти ежедневную цепочку слов", "chat_moderators", "bot_help_daily_word_chain_faq", False),
        ("почему после смены чата недоступны настройки", "chat_moderators", "bot_help_selected_chat_access_faq", False),
        ("Возможности зависят от роли в конкретном чате и прав Telegram", "community_bots", "bot_help_rights", True),
    ]
    for repetition in range(10):
        for n, (query, audience, expected, allowed) in enumerate(probes, 1):
            found = {r[0] for r in index.search(query, audience, 20)}
            assert (expected in found) is allowed, (repetition, n, audience, expected, found)
    print("IMPULS_FEATURE_FAQ_10X10_PASS")


def sha_cache_revalidation(raw: bytes) -> None:
    with tempfile.TemporaryDirectory(prefix="synthetic-feature-faq-") as tmp:
        root = Path(tmp)
        target = root / REL
        target.parent.mkdir(parents=True)
        target.write_bytes(raw)
        original_sha = hashlib.sha256(raw).hexdigest()
        manifest = {"schema_version": 1, "language": "ru", "knowledge_version": "snapshot-a",
                    "packs": [{"path": REL, "sha256": original_sha}]}
        (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        old = KnowledgeSearch(root)
        assert len(old.records) == 3
        new_pack = json.loads(raw)
        new_pack["skills"][0]["examples"][0] += " Эта подсказка синтетическая."
        updated = (json.dumps(new_pack, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        target.write_bytes(updated)
        try:
            KnowledgeSearch(root)
            raise AssertionError("modified bytes accepted with stale SHA")
        except ValueError as exc:
            assert "SHA mismatch" in str(exc)
        manifest["knowledge_version"] = "snapshot-b"
        manifest["packs"][0]["sha256"] = hashlib.sha256(updated).hexdigest()
        (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        current = KnowledgeSearch(root)
        assert current is not old and current.records[0]["preview"] != old.records[0]["preview"]
        assert len(current.records) == len(old.records) == 3
    print("IMPULS_FEATURE_FAQ_SHA_CACHE_REFRESH_PASS")


if __name__ == "__main__":
    _, raw = validate()
    ten_rounds()
    sha_cache_revalidation(raw)
    print("IMPULS_FEATURE_FAQ_VALIDATION_PASS")
