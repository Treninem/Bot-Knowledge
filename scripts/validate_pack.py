from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_KEYS = {
    "user_id", "chat_id", "telegram_id", "username", "phone", "email",
    "token", "cookie", "password", "secret", "first_name", "last_name",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def walk_keys(value, path="root"):
    if isinstance(value, dict):
        for key, item in value.items():
            yield path, str(key).lower()
            yield from walk_keys(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk_keys(item, f"{path}[{index}]")


def main() -> int:
    errors: list[str] = []
    manifest_path = ROOT / "manifest.json"
    manifest = read_json(manifest_path)

    if manifest.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if manifest.get("language") != "ru":
        errors.append("language must be ru")

    packs = manifest.get("packs")
    if not isinstance(packs, list) or not packs:
        errors.append("manifest.packs must be a non-empty list")
        packs = []

    for item in packs:
        if not isinstance(item, dict):
            errors.append("manifest pack entry must be an object")
            continue
        relative = str(item.get("path", ""))
        if not relative.startswith("packs/ru/") or ".." in Path(relative).parts:
            errors.append(f"unsafe pack path: {relative}")
            continue
        path = ROOT / relative
        if not path.exists():
            errors.append(f"missing pack: {relative}")
            continue
        payload = path.read_bytes()
        actual = hashlib.sha256(payload).hexdigest()
        expected = str(item.get("sha256", ""))
        if actual != expected:
            errors.append(f"sha256 mismatch: {relative}: expected {expected}, got {actual}")
        try:
            data = json.loads(payload.decode("utf-8"))
        except Exception as exc:
            errors.append(f"invalid JSON: {relative}: {exc}")
            continue
        for location, key in walk_keys(data):
            if key in FORBIDDEN_KEYS:
                errors.append(f"forbidden personal/secret key {key!r} in {relative} at {location}")

    intents_path = ROOT / "packs/ru/intents.json"
    if intents_path.exists():
        data = read_json(intents_path)
        intents = data.get("intents")
        if not isinstance(intents, list) or not intents:
            errors.append("intents.json must contain non-empty intents list")
        else:
            ids = []
            for item in intents:
                if not isinstance(item, dict):
                    errors.append("each intent must be an object")
                    continue
                intent_id = str(item.get("id", "")).strip()
                if not intent_id:
                    errors.append("intent without id")
                    continue
                ids.append(intent_id)
                examples = item.get("examples")
                if not isinstance(examples, list) or not examples:
                    errors.append(f"intent {intent_id} has no examples")
            if len(ids) != len(set(ids)):
                errors.append("duplicate intent ids")

    skills_path = ROOT / "packs/ru/skills.json"
    if skills_path.exists():
        payload = skills_path.read_bytes()
        if len(payload) > 128 * 1024:
            errors.append("skills pack exceeds 128 KiB")
        data = read_json(skills_path)
        policy = data.get("usage_policy", {})
        if (data.get("schema_version") != 1
                or data.get("language") != "ru"
                or not isinstance(policy, dict)
                or policy.get("user_data_allowed") is not False
                or policy.get("automatic_sanctions_allowed") is not False
                or policy.get("initiative_requires_local_authorization") is not True):
            errors.append("skills policy must forbid personal data, automatic sanctions and unauthorized initiative")
        skills = data.get("skills")
        if not isinstance(skills, list) or not skills:
            errors.append("skills pack must contain a nonempty list")
        else:
            seen = set()
            for skill in skills:
                if not isinstance(skill, dict):
                    errors.append("invalid skills entry")
                    continue
                skill_id = skill.get("id")
                if not isinstance(skill_id, str) or not skill_id.isascii() or not skill_id.replace("_", "").isalnum():
                    errors.append("invalid skill id")
                if skill_id in seen:
                    errors.append("duplicate skill id")
                seen.add(skill_id)
                if skill.get("kind") not in {"social", "bot_help", "moderation_language"}:
                    errors.append("unsupported skill kind")
                for field in ("when", "avoid", "examples"):
                    items = skill.get(field)
                    if not isinstance(items, list) or len(items) > 12 or any(
                        not isinstance(item, str) or not 1 <= len(item) <= 300 for item in items
                    ):
                        errors.append(f"invalid skill field {field}")
                if "action" in skill or "auto_apply" in skill:
                    errors.append("skill must not contain executable/action fields")
                audiences = skill.get("audiences")
                if (not isinstance(audiences, list) or not audiences
                        or len(audiences) > 5 or any(
                            item not in {"all_ai_bots", "chat_moderators", "community_bots"}
                            for item in audiences
                        )):
                    errors.append("invalid skill audience selection")
                if skill.get("kind") == "moderation_language" and "all_ai_bots" in (audiences or []):
                    errors.append("chat-specific moderation must not be treated as general AuroraFox knowledge")
                if skill.get("kind") == "bot_help" and "all_ai_bots" in (audiences or []):
                    errors.append("bot-specific help must not be treated as general AuroraFox knowledge")


    if errors:
        print("Bot-Knowledge validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Bot-Knowledge validation: OK ({manifest.get('knowledge_version')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
