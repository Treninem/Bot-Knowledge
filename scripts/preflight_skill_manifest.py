"""Offline preflight for a reviewed skill candidate and proposed Bot-Knowledge manifest.

This does not approve content or publish it. A human must still review the PR.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

from prepare_knowledge_candidate import validate as validate_candidate


SKILL_PATH = "packs/ru/skills.json"
AUDIENCES = {"all_ai_bots", "chat_moderators", "community_bots"}
KINDS = {"social", "bot_help", "moderation_language"}
DOMAINS = {"evidence", "context", "execution", "progress", "decisions", "technical", "writing", "creativity"}
PRIVATE_VALUE = (
    re.compile(r"https?://|t\.me/|telegram\.me/", re.I),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"(?<!\w)@[A-Za-z][A-Za-z0-9_]{4,31}\b"),
    re.compile(r"(?<!\d)\d{10,}(?!\d)"),
    re.compile(r"(?:\+7|8)(?:[\s().-]*\d){10}(?!\d)"),
    re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I),
    re.compile(r"\b(?:api[_-]?key|token|password|secret|пароль|токен)\s*[:=]", re.I),
    re.compile(r"\b(?:забань|бань|заблокируй|замуть|мутни|кикни|ban|mute|kick)\b", re.I),
    re.compile(r"\b(?:игнорируй|отключи|обойди)\s+(?:политику|правила|защиту)\b", re.I),
)
PRIVATE_KEYS = {
    "chat_id", "user_id", "telegram_id", "username", "first_name", "last_name",
    "phone", "email", "password", "cookie", "token", "secret", "raw_message",
    "raw_chat", "chat_history", "private_quote", "action", "auto_apply",
}


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _read_json(path: Path, *, max_bytes: int):
    if path.stat().st_size > max_bytes:
        raise ValueError("JSON input too large")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)


def _walk(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key), None
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)
    elif isinstance(value, str):
        yield None, value


def _private_value(value) -> bool:
    return any(
        (key is not None and key.casefold() in PRIVATE_KEYS)
        or (text is not None and any(pattern.search(text) for pattern in PRIVATE_VALUE))
        for key, text in _walk(value)
    )


def _safe_pack_path(raw: object) -> str | None:
    if not isinstance(raw, str) or not raw.startswith("packs/ru/") or "\\" in raw:
        return None
    path = PurePosixPath(raw)
    if path.as_posix() != raw or any(part in {".", ".."} for part in raw.split("/")):
        return None
    if path.suffix != ".json" or not re.fullmatch(r"[a-z][a-z0-9_]*\.json", path.name):
        return None
    return raw


def validate_bundle(
    root: Path, candidate_path: Path, reviewed_skill_path: Path, manifest_path: Path,
    baseline_root: Path, baseline_manifest_path: Path,
) -> None:
    """Raise ValueError on unsafe, inconsistent or unreviewed local inputs."""
    candidate = _read_json(candidate_path, max_bytes=16 * 1024)
    try:
        validate_candidate(candidate)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"candidate rejected: {exc}") from exc
    if _private_value(candidate):
        raise ValueError("candidate contains private or executable content")
    reviewed_skill = _read_json(reviewed_skill_path, max_bytes=16 * 1024)
    if not isinstance(reviewed_skill, dict) or _private_value(reviewed_skill):
        raise ValueError("reviewed skill contains private or executable content")

    manifest = _read_json(manifest_path, max_bytes=128 * 1024)
    if (not isinstance(manifest, dict)
            or not {"schema_version", "knowledge_version", "language", "packs"} <= set(manifest)
            or set(manifest) - {"schema_version", "knowledge_version", "language", "packs", "generated_at"}):
        raise ValueError("manifest shape invalid")
    if (type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1
            or manifest["language"] != "ru"
            or not isinstance(manifest["knowledge_version"], str)
            or not re.fullmatch(r"[0-9]{4}\.[0-9]{1,2}\.[0-9]{1,2}\.[0-9]+", manifest["knowledge_version"])):
        raise ValueError("manifest version or language invalid")
    if "generated_at" in manifest and (not isinstance(manifest["generated_at"], str)
            or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", manifest["generated_at"]) is None):
        raise ValueError("manifest timestamp invalid")
    entries = manifest["packs"]
    if not isinstance(entries, list) or not entries or len(entries) > 64:
        raise ValueError("manifest pack list invalid")
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            raise ValueError("manifest entry shape invalid")
        relative = _safe_pack_path(entry["path"])
        if relative is None or relative in seen:
            raise ValueError("unsafe or duplicate pack path")
        seen.add(relative)
        expected = entry["sha256"]
        if not isinstance(expected, str) or re.fullmatch(r"[0-9a-f]{64}", expected) is None:
            raise ValueError("manifest SHA invalid")
        path = root / relative
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError("pack path unavailable or outside root")
        limit = 128 * 1024 if relative == SKILL_PATH else 1024 * 1024
        if path.stat().st_size > limit:
            raise ValueError("pack too large")
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != expected:
            raise ValueError("manifest SHA mismatch")
        try:
            data = json.loads(payload.decode("utf-8"), object_pairs_hook=_unique_pairs)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("pack JSON invalid") from exc
        if relative == SKILL_PATH and _private_value(data):
            raise ValueError("pack contains private or executable content")

    if SKILL_PATH not in seen:
        raise ValueError("skills pack absent from manifest")
    baseline = _read_json(baseline_manifest_path, max_bytes=128 * 1024)
    if (not isinstance(baseline, dict) or not isinstance(baseline.get("packs"), list)
            or not isinstance(baseline.get("knowledge_version"), str)
            or baseline.get("schema_version") != 1 or baseline.get("language") != "ru"
            or re.fullmatch(r"[0-9]{4}\.[0-9]{1,2}\.[0-9]{1,2}\.[0-9]+", baseline["knowledge_version"]) is None
            or tuple(map(int, manifest["knowledge_version"].split(".")))
            <= tuple(map(int, baseline["knowledge_version"].split(".")))):
        raise ValueError("baseline invalid or knowledge version not increased")
    baseline_entries: dict[str, str] = {}
    for entry in baseline["packs"]:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            raise ValueError("baseline manifest entry invalid")
        relative = _safe_pack_path(entry["path"])
        expected = entry["sha256"]
        if (relative is None or relative in baseline_entries or not isinstance(expected, str)
                or re.fullmatch(r"[0-9a-f]{64}", expected) is None):
            raise ValueError("baseline manifest path or SHA invalid")
        baseline_entries[relative] = expected
        base_path = baseline_root / relative
        if (base_path.is_symlink() or not base_path.is_file()
                or not base_path.resolve().is_relative_to(baseline_root.resolve())
                or base_path.stat().st_size > (128 * 1024 if relative == SKILL_PATH else 1024 * 1024)
                or hashlib.sha256(base_path.read_bytes()).hexdigest() != expected):
            raise ValueError("baseline pack missing or SHA mismatch")
    proposed_entries = {entry["path"]: entry["sha256"] for entry in entries}
    if set(proposed_entries) != set(baseline_entries) or any(
        proposed_entries[path] != sha for path, sha in baseline_entries.items() if path != SKILL_PATH
    ):
        raise ValueError("unrelated pack or manifest entry changed")
    if SKILL_PATH not in baseline_entries or proposed_entries[SKILL_PATH] == baseline_entries[SKILL_PATH]:
        raise ValueError("skills pack unchanged or absent in baseline")
    baseline_skills = _read_json(baseline_root / SKILL_PATH, max_bytes=128 * 1024)
    baseline_rows = baseline_skills.get("skills") if isinstance(baseline_skills, dict) else None
    if not isinstance(baseline_rows, list) or not isinstance(skills := _read_json(root / SKILL_PATH, max_bytes=128 * 1024), dict):
        raise ValueError("baseline or proposed skills shape invalid")
    if (set(skills) != set(baseline_skills) or any(
            key != "skills" and skills[key] != baseline_skills[key] for key in baseline_skills
    ) or not isinstance(skills.get("skills"), list)
            or skills["skills"][:-1] != baseline_rows
            or len(skills["skills"]) != len(baseline_rows) + 1
            or not isinstance(skills["skills"][-1], dict)
            or skills["skills"][-1].get("id") != candidate["candidate_id"]):
        raise ValueError("existing skills changed or candidate was not appended once")
    policy = skills.get("usage_policy") if isinstance(skills, dict) else None
    if (not isinstance(skills, dict) or skills.get("schema_version") != 1 or skills.get("language") != "ru"
            or not isinstance(policy, dict) or policy.get("user_data_allowed") is not False
            or policy.get("automatic_sanctions_allowed") is not False
            or policy.get("initiative_requires_local_authorization") is not True
            or policy.get("scope_filter_required") is not True
            or policy.get("shared_between_bots") is not True):
        raise ValueError("skills policy invalid")
    rows = skills.get("skills")
    if not isinstance(rows, list) or not rows or len(rows) > 256:
        raise ValueError("skills list invalid")
    ids: set[str] = set()
    matching = []
    for skill in rows:
        if (not isinstance(skill, dict)
                or not {"id", "kind", "when", "avoid", "examples", "audiences"} <= set(skill)
                or set(skill) - {"id", "kind", "when", "avoid", "examples", "audiences"} - {"domain"}):
            raise ValueError("skill shape invalid")
        if "domain" in skill and (not isinstance(skill["domain"], str) or skill["domain"] not in DOMAINS):
            raise ValueError("skill domain invalid")
        skill_id = skill["id"]
        if (not isinstance(skill_id, str) or re.fullmatch(r"[a-z][a-z0-9_]{2,70}", skill_id) is None
                or skill_id in ids or not isinstance(skill["kind"], str) or skill["kind"] not in KINDS):
            raise ValueError("skill identity invalid")
        ids.add(skill_id)
        for field in ("when", "avoid", "examples"):
            values = skill[field]
            if (not isinstance(values, list) or len(values) > 12
                    or any(not isinstance(v, str) or not 1 <= len(v) <= 300 for v in values)):
                raise ValueError(f"skill {field} invalid")
        audience = skill["audiences"]
        if (not isinstance(audience, list) or not audience or len(audience) > 5
                or any(not isinstance(v, str) or v not in AUDIENCES for v in audience)):
            raise ValueError("skill audience invalid")
        if skill["kind"] in {"bot_help", "moderation_language"} and "all_ai_bots" in audience:
            raise ValueError("chat-specific skill cannot target all bots")
        if skill_id == candidate["candidate_id"]:
            matching.append(skill)
    if len(matching) != 1:
        raise ValueError("candidate skill absent or ambiguous")
    proposed = matching[0]
    if not proposed["when"] or not proposed["avoid"] or not proposed["examples"]:
        raise ValueError("proposed skill lacks context or example")
    if (proposed["when"] != candidate["when"] or proposed["avoid"] != candidate["avoid"]
            or proposed["audiences"] != candidate["audiences"]):
        raise ValueError("candidate and proposed skill differ")
    if proposed != reviewed_skill:
        raise ValueError("proposed skill differs from exact reviewed skill")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True, help="local draft pack root")
    parser.add_argument("--baseline-root", type=Path, required=True, help="trusted published pack root")
    parser.add_argument("--candidate", type=Path, required=True, help="reviewed abstract candidate JSON")
    parser.add_argument("--reviewed-skill", type=Path, required=True, help="exact skill JSON reviewed for publication")
    parser.add_argument("--manifest", type=Path, required=True, help="draft manifest JSON")
    parser.add_argument("--baseline-manifest", type=Path, required=True, help="trusted published manifest JSON")
    args = parser.parse_args()
    try:
        validate_bundle(args.root, args.candidate, args.reviewed_skill, args.manifest,
                        args.baseline_root, args.baseline_manifest)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"PREFLIGHT_REJECTED: {exc}")
        return 1
    print("PREFLIGHT_OK; manual privacy review and PR still required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
