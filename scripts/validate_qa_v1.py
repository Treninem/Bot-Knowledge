"""Validate declarative qa.v1 data locally; never fetch, execute or publish it.

The JSON Schema describes the canonical authoring shape. This stdlib validator
also checks safe field mappings, cross-field scopes, IDs, URLs, rendered limits
and obvious private-data markers that JSON Schema cannot express on its own.
Human review of provenance, privacy and factual meaning remains indispensable.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}\Z")
FIELD = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,63}\Z")
FIELDS = frozenset({"id", "question", "aliases", "answer", "variants", "source", "audiences", "contexts", "constraints", "language"})
CONTEXTS = frozenset({"direct", "private", "group_addressed"})
CONSTRAINTS = {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
FORBIDDEN = frozenset({
    "action", "actions", "auto_apply", "execute", "permissions", "command", "commands",
    "code", "template", "template_eval", "tool", "tools", "user_id", "chat_id", "telegram_id",
    "username", "phone", "email", "token", "cookie", "password", "secret", "first_name",
    "last_name", "raw_message", "raw_chat", "chat_history", "private_quote",
})
GITHUB_REV_SOURCE = re.compile(
    r"^/Treninem/Bot-Knowledge/blob/([0-9a-f]{40})/[A-Za-z0-9._/-]+$",
    re.IGNORECASE,
)
PRIVATE_MARKERS = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b|(?<!\w)@[A-Za-z0-9_]{4,}|"
    r"(?<!\d)\d{10,}(?!\d)|\b(?:token|password|secret|api[_-]?key|пароль|токен)\s*[:=]",
    re.IGNORECASE,
)


def _text(value, limit: int, required: bool = True) -> str:
    if (not isinstance(value, str) or len(value) > limit
            or any(ord(char) < 32 and char not in "\n\t" for char in value)):
        raise ValueError("invalid_text")
    if required and not value.strip():
        raise ValueError("empty_text")
    return value.strip()


def _strings(value, maximum: int, limit: int) -> tuple[str, ...]:
    if not isinstance(value, list) or len(value) > maximum:
        raise ValueError("invalid_list")
    return tuple(dict.fromkeys(_text(item, limit) for item in value))


def _url(value) -> str:
    if value is None or value == "":
        return ""
    value = _text(value, 500)
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or any(char in value for char in "<>\"'\\") or any(char.isspace() for char in value)):
        raise ValueError("invalid_source_url")
    # GitHub's immutable 40-hex revision segment is a public content
    # identifier, not a telephone number. Mask ONLY this exact segment on
    # the canonical public BK source URL before screening for private data.
    # Other long numbers in paths, query strings and arbitrary hosts remain
    # blocked. A decimal-only segment is deliberately not whitelisted.
    screened = value
    match = GITHUB_REV_SOURCE.fullmatch(parsed.path) if parsed.hostname.lower() == "github.com" else None
    if match and re.search(r"[a-f]", match.group(1), re.IGNORECASE):
        screened = value.replace("/blob/" + match.group(1) + "/", "/blob/REVISION/", 1)
    if PRIVATE_MARKERS.search(screened) or parsed.query or parsed.fragment:
        raise ValueError("source_must_be_public_without_personal_or_secret_query_data")
    return value


def _data(value, depth: int = 0, *, url_field: bool = False) -> None:
    if depth > 10:
        raise ValueError("nesting_limit")
    if isinstance(value, dict):
        if len(value) > 80 or any(not isinstance(key, str) or key.casefold() in FORBIDDEN for key in value):
            raise ValueError("private_or_executable_field")
        for key, child in value.items():
            _data(child, depth + 1, url_field=key in {"source", "$schema"})
    elif isinstance(value, list):
        if len(value) > 1000:
            raise ValueError("list_limit")
        for child in value:
            _data(child, depth + 1)
    elif isinstance(value, str):
        _text(value, 5000, required=False)
        if url_field:
            _url(value)
        elif PRIVATE_MARKERS.search(value):
            raise ValueError("potential_private_data_or_secret")
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non_finite_number")
    elif value is not None and not isinstance(value, (bool, int, float)):
        raise ValueError("unsupported_value")


def _constraints(value) -> None:
    if (not isinstance(value, dict) or set(value) != set(CONSTRAINTS)
            or any(value[key] is not expected for key, expected in CONSTRAINTS.items())):
        raise ValueError("unsupported_or_missing_constraints")


def validate_catalog_metadata(metadata: dict, *, adapter: str = "qa.v1") -> None:
    _data(metadata)
    if not isinstance(metadata, dict) or type(metadata.get("schema_version")) is not int or metadata["schema_version"] != 1:
        raise ValueError("unsupported_catalog_schema")
    if not ID.fullmatch(_text(metadata.get("id"), 96)):
        raise ValueError("invalid_section_id")
    for name, maximum in (("title", 120), ("description", 700), ("purpose", 80)):
        _text(metadata.get(name), maximum)
    if metadata.get("language") not in {"ru", "en", "multilingual"} or metadata.get("adapter") != adapter:
        raise ValueError("invalid_adapter_or_language")
    _strings(metadata.get("tags", []), 16, 64)
    _constraints(metadata.get("constraints"))
    audiences = _strings(metadata.get("audiences", ["all_ai_bots"]), 12, 64)
    contexts = _strings(metadata.get("contexts", ["direct"]), 3, 32)
    if not audiences or not contexts or set(contexts) - CONTEXTS:
        raise ValueError("invalid_section_scope")


def validate_qa_pack(pack: dict, metadata: dict | None = None) -> int:
    if not isinstance(pack, dict) or type(pack.get("schema_version")) is not int or pack["schema_version"] != 1:
        raise ValueError("unsupported_pack_schema")
    _data(pack)
    metadata = pack.get("catalog") if metadata is None else metadata
    validate_catalog_metadata(metadata)
    fields = metadata.get("fields", {})
    if (not isinstance(fields, dict) or set(fields) - FIELDS
            or any(not isinstance(value, str) or not FIELD.fullmatch(value) for value in fields.values())
            or len(set(fields.values())) != len(fields)):
        raise ValueError("unsafe_field_mapping")
    collection = metadata.get("records", "records")
    if not isinstance(collection, str) or not FIELD.fullmatch(collection):
        raise ValueError("unsafe_record_mapping")
    rows = pack.get(collection)
    if not isinstance(rows, list) or not 1 <= len(rows) <= 1000:
        raise ValueError("invalid_records")
    audiences = _strings(metadata.get("audiences", ["all_ai_bots"]), 12, 64)
    contexts = _strings(metadata.get("contexts", ["direct"]), 3, 32)
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("invalid_record")
        def field(name, default=None):
            return row.get(fields.get(name, name), default)
        identifier = _text(field("id"), 96)
        if not ID.fullmatch(identifier) or identifier in seen:
            raise ValueError("duplicate_or_invalid_record_id")
        seen.add(identifier)
        _text(field("question"), 500)
        _strings(field("aliases", []), 16, 500)
        answers = (_text(field("answer"), 1600),) + _strings(field("variants", []), 8, 1600)
        if any(len(escape(answer)) > 2000 for answer in answers):
            raise ValueError("escaped_answer_limit")
        if field("constraints") is not None:
            _constraints(field("constraints"))
        record_audiences = _strings(field("audiences", list(audiences)), 12, 64)
        record_contexts = _strings(field("contexts", list(contexts)), 3, 32)
        if (not record_audiences or not record_contexts or set(record_contexts) - set(contexts)
                or ("all_ai_bots" not in audiences and set(record_audiences) - set(audiences))):
            raise ValueError("record_scope_widening")
        language = field("language", metadata["language"])
        if language not in {"ru", "en", "multilingual"} or (metadata["language"] != "multilingual" and language != metadata["language"]):
            raise ValueError("record_language_mismatch")
        _url(field("source"))
    return len(rows)


def validate_qa_manifest(root: Path) -> list[str]:
    """Additional qa.v1 registration; all existing validators remain in force."""
    errors: list[str] = []
    try:
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        entries = manifest["packs"]
        seen_ids, seen_paths = set(), set()
        total = 0
        for entry in entries:
            relative = entry.get("path", "")
            if relative in seen_paths:
                raise ValueError("duplicate_manifest_path")
            seen_paths.add(relative)
            path = root / relative
            if not isinstance(relative, str) or not relative.startswith("packs/ru/") or ".." in Path(relative).parts:
                raise ValueError("unsafe_pack_path")
            if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
                raise ValueError("unsafe_pack_path")
            raw = path.read_bytes()
            pack = json.loads(raw)
            embedded, declared = pack.get("catalog"), entry.get("catalog")
            if embedded is not None and declared is not None and embedded != declared:
                raise ValueError("conflicting_catalog_metadata")
            metadata = declared if declared is not None else embedded
            if metadata is not None:
                _data(pack)
                _data(metadata)
            if isinstance(metadata, dict) and isinstance(metadata.get("id"), str):
                if metadata["id"] in seen_ids:
                    raise ValueError("duplicate_section_id")
                seen_ids.add(metadata["id"])
            if not isinstance(metadata, dict) or metadata.get("adapter") != "qa.v1":
                continue
            if len(raw) > 1024 * 1024 or hashlib.sha256(raw).hexdigest() != entry.get("sha256"):
                raise ValueError("qa_size_or_hash_mismatch")
            total += validate_qa_pack(pack, metadata)
            if total > 4096:
                raise ValueError("catalog_record_limit")
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, AttributeError) as exc:
        errors.append(f"qa.v1: {exc}")
    return errors


if __name__ == "__main__":
    problems = validate_qa_manifest(ROOT)
    if problems:
        raise SystemExit("\n".join(problems))
    print("qa.v1 manifest validation: OK")
