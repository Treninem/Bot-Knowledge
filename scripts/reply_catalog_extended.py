"""Opt-in, SHA-pinned extensions of existing canonical reply questions.

This reference consumer does not route natural language or grant permissions.
The original ReplyCatalog is unchanged. New groups require an explicit group
and context_confirmed=True from a trusted caller; existing defaults survive.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from types import MappingProxyType

from reply_catalog import PACK, POLICY, ROOT, ReplyCatalog, normalized

PREFIX = "packs/ru/reply_extensions/"
PATH_PATTERN = re.compile(r"packs/ru/reply_extensions/([a-z][a-z0-9_]{2,63})\.json")
PACK_KEYS = {"schema_version", "language", "kind", "intent", "base_pack", "usage_policy", "groups"}
GROUP_KEYS = {"id", "when", "avoid", "replies"}
MAX_EXTENSION_BYTES = 128 * 1024


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def verified_extension(root: Path, relative: str, expected: str) -> tuple[dict, str]:
    path = root / relative
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Unsafe extension path")
    if path.stat().st_size > MAX_EXTENSION_BYTES:
        raise ValueError("Extension too large")
    raw = path.read_bytes()
    if len(raw) > MAX_EXTENSION_BYTES:
        raise ValueError("Extension too large")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected:
        raise ValueError("Extension SHA mismatch")
    data = json.loads(raw, object_pairs_hook=strict_object)
    if (not isinstance(data, dict) or set(data) != PACK_KEYS
            or type(data.get("schema_version")) is not int or data["schema_version"] != 1
            or data.get("language") != "ru"
            or data.get("kind") != "reply_catalog_extension"
            or data.get("base_pack") != PACK
            or data.get("usage_policy") != POLICY
            or any(type(v) is not bool for v in data["usage_policy"].values())):
        raise ValueError("Invalid extension policy or schema")
    return data, digest


class ReplyCatalogExtended(ReplyCatalog):
    """One immutable reference snapshot; private recent history stays with caller."""

    def __init__(self, root: Path = ROOT):
        root = Path(root)
        before = (root / "manifest.json").read_bytes()
        manifest = json.loads(before, object_pairs_hook=strict_object)
        version = manifest.get("knowledge_version")
        if not isinstance(version, str) or not version:
            raise ValueError("Invalid knowledge version")
        entries = manifest.get("packs")
        if not isinstance(entries, list) or any(not isinstance(p, dict) for p in entries):
            raise ValueError("Invalid manifest entries")
        paths = [p.get("path") for p in entries]
        if any(not isinstance(p, str) for p in paths) or len(set(paths)) != len(paths):
            raise ValueError("Duplicate or invalid manifest paths")
        super().__init__(root)
        self.base_snapshot_key = self.snapshot_key
        self.base_coverage = dict(self.coverage)
        base_raw = (root / PACK).read_bytes()
        if hashlib.sha256(base_raw).hexdigest() != self.base_snapshot_key[1]:
            raise ValueError("Base changed while loading")
        records = json.loads(base_raw)["sets"]
        self._legacy_defaults = {}
        for record in records:
            groups = self._sets[record["id"]][1]
            default = record.get("default_group")
            if default in groups:
                self._legacy_defaults[record["id"]] = default
            elif len(groups) == 1:
                self._legacy_defaults[record["id"]] = next(iter(groups))
        self._origins = {}
        self._guards = {}
        seen = {normalized(answer) for _, groups in self._sets.values()
                for replies in groups.values() for answer in replies}
        extension_entries = sorted((p for p in entries if p["path"].startswith(PREFIX)),
                                   key=lambda p: p["path"])
        if len(extension_entries) > 128:
            raise ValueError("Too many extension packs")
        snapshot = [(PACK, self.base_snapshot_key[1])]
        self.extension_coverage = {}
        for entry in extension_entries:
            relative = entry["path"]
            match = PATH_PATTERN.fullmatch(relative)
            if match is None:
                raise ValueError("Invalid extension path")
            data, digest = verified_extension(root, relative, entry.get("sha256"))
            name = data["intent"]
            if not isinstance(name, str) or name != match[1] or name not in self._sets:
                raise ValueError("Extension requires an existing matching intent")
            groups = data["groups"]
            if not isinstance(groups, list) or not 1 <= len(groups) <= 100:
                raise ValueError("Invalid extension groups")
            audiences, existing = self._sets[name]
            prepared = dict(existing)
            added = 0
            for group in groups:
                if not isinstance(group, dict) or set(group) != GROUP_KEYS:
                    raise ValueError("Invalid group schema")
                gid = group["id"]
                if (not isinstance(gid, str) or not re.fullmatch(r"[a-z][a-z0-9_]{1,39}", gid)
                        or gid in prepared):
                    raise ValueError("Duplicate or invalid extension group")
                if any(not isinstance(group[k], str) or not 8 <= len(group[k]) <= 600
                       for k in ("when", "avoid")):
                    raise ValueError("Invalid context guard")
                replies = group["replies"]
                if (not isinstance(replies, list) or not 1 <= len(replies) <= 100
                        or any(not isinstance(v, str) or not 12 <= len(v) <= 300
                               for v in replies)):
                    raise ValueError("Invalid extension replies")
                for answer in replies:
                    key = normalized(answer)
                    if not key or key in seen:
                        raise ValueError("Duplicate answer across base/extensions")
                    seen.add(key)
                prepared[gid] = tuple(replies)
                self._origins[name, gid] = relative
                self._guards[name, gid] = (group["when"], group["avoid"])
                added += len(replies)
            if sum(map(len, prepared.values())) > 100:
                raise ValueError("More than 100 replies per canonical question")
            self._sets[name] = (audiences, prepared)
            self.extension_coverage[name] = added
            snapshot.append((relative, digest))
        if (root / "manifest.json").read_bytes() != before:
            raise ValueError("Manifest changed while loading")
        if extension_entries:
            combined = hashlib.sha256(json.dumps(snapshot, separators=(",", ":")).encode()).hexdigest()
            self.snapshot_key = (version, combined)
        self.coverage = {name: sum(map(len, groups.values()))
                         for name, (_, groups) in self._sets.items()}
        self._sets = MappingProxyType({name: (aud, MappingProxyType(groups))
                                       for name, (aud, groups) in self._sets.items()})
        self.extension_sources = tuple(snapshot[1:])

    def conditions(self, intent: str, group: str) -> dict | None:
        """Read the original guards before independently confirming caller context."""
        if not isinstance(intent, str) or not isinstance(group, str):
            raise ValueError("Bad intent or group")
        guard = self._guards.get((intent, group))
        return None if guard is None else {"when": guard[0], "avoid": guard[1]}

    def reply(self, intent: str, *, group: str | None = None,
              context_confirmed: bool = False, **kwargs) -> dict:
        if type(context_confirmed) is not bool:
            raise ValueError("Context confirmation must be bool")
        if not isinstance(intent, str) or (group is not None and not isinstance(group, str)):
            raise ValueError("Bad intent or group")
        if group is None:
            group = self._legacy_defaults.get(intent)
        result = super().reply(intent, group=group, **kwargs)
        origin = self._origins.get((intent, group))
        if result["status"] == "ok" and origin is not None:
            if not context_confirmed:
                return self._reject("context_confirmation_required")
            result = dict(result, source_pack=origin, conditions=self.conditions(intent, group))
        return result
