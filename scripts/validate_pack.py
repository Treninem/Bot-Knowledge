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

    if errors:
        print("Bot-Knowledge validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Bot-Knowledge validation: OK ({manifest.get('knowledge_version')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
