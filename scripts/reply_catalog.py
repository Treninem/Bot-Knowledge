"""Read-only, explicitly scoped response catalogue.

No automatic intent routing, API calls, chat memory, moderation powers or chat
state. The consumer supplies a reviewed intent, verified local permission,
allowed audience, and a context-appropriate group. Missing context fails closed.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/reply_catalog.json"
AUDIENCES = frozenset({"all_ai_bots", "community_bots", "chat_moderators"})
POLICY = {
    "synthetic_only": True,
    "personal_data_allowed": False,
    "automatic_actions_allowed": False,
    "automatic_sanctions_allowed": False,
    "requires_explicit_address": True,
    "requires_local_permission": True,
}
HUMOR_INTENTS = frozenset({"tell_joke", "dark_humor"})


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join(re.findall(r"[^\W_]+", value, flags=re.UNICODE))


class ReplyCatalog:
    """Immutable SHA-checked catalogue of opt-in replies, without session state."""

    def __init__(self, root: Path = ROOT):
        root = Path(root)
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("schema_version") != 1 or manifest.get("language") != "ru":
            raise ValueError("Unsupported manifest")
        entries = [p for p in manifest.get("packs", ()) if p.get("path") == PACK]
        if len(entries) != 1:
            raise ValueError("Missing or duplicate reply catalogue manifest entry")
        raw = (root / PACK).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != entries[0].get("sha256"):
            raise ValueError("Reply catalogue SHA mismatch")
        pack = json.loads(raw)
        if (pack.get("schema_version") != 1 or pack.get("language") != "ru"
                or pack.get("usage_policy") != POLICY):
            raise ValueError("Invalid reply catalogue policy")
        records = pack.get("sets")
        if not isinstance(records, list) or not records:
            raise ValueError("Missing response sets")

        self._sets = {}
        seen_answers = set()
        for record in records:
            if not isinstance(record, dict):
                raise ValueError("Invalid response set")
            name = record.get("id")
            if (not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_]{2,63}", name)
                    or name in self._sets):
                raise ValueError("Duplicate or invalid response intent")
            if (not isinstance(record.get("question"), str)
                    or not 3 <= len(record["question"]) <= 160
                    or record.get("section") not in {
                        "общение", "правила", "помощь", "настройка", "навыки", "умение"
                    }):
                raise ValueError("Invalid question or section")
            audiences = record.get("audiences")
            if (not isinstance(audiences, list) or not audiences
                    or len(set(audiences)) != len(audiences)
                    or not set(audiences) <= AUDIENCES):
                raise ValueError("Unsafe audience")
            if "community_bots" in audiences and "all_ai_bots" in audiences:
                raise ValueError("Community help must not leak into general AI")
            groups = record.get("groups")
            if not isinstance(groups, list) or not groups:
                raise ValueError("Missing response groups")
            prepared = {}
            amount = 0
            for group in groups:
                if not isinstance(group, dict):
                    raise ValueError("Invalid response group")
                gid = group.get("id")
                if (not isinstance(gid, str) or not re.fullmatch(r"[a-z][a-z0-9_]{1,39}", gid)
                        or gid in prepared):
                    raise ValueError("Duplicate or invalid response group")
                if (not isinstance(group.get("when"), str) or len(group["when"]) < 8
                        or not isinstance(group.get("avoid"), str) or len(group["avoid"]) < 8):
                    raise ValueError("Missing context guard")
                replies = group.get("replies")
                if (not isinstance(replies, list) or not replies
                        or any(not isinstance(v, str) or not 12 <= len(v) <= 300
                               for v in replies)):
                    raise ValueError("Invalid reply")
                for reply in replies:
                    key = normalized(reply)
                    if key in seen_answers:
                        raise ValueError("Duplicate answer (normalized)")
                    seen_answers.add(key)
                prepared[gid] = tuple(replies)
                amount += len(replies)
            if amount > 100:
                raise ValueError("More than 100 replies per canonical question")
            default_group = record.get('default_group')
            if default_group is not None and default_group not in prepared:
                raise ValueError('Unknown default response group')
            self._sets[name] = (tuple(audiences), prepared, default_group)
        self.coverage = {name: sum(len(v) for v in groups.values())
                         for name, (_, groups, _) in self._sets.items()}
        self.snapshot_key = (manifest["knowledge_version"], digest)

    @staticmethod
    def _reject(reason: str) -> dict:
        return {"status": reason, "text": None}

    def reply(self, intent: str, *, addressed: bool = False,
              local_permission: bool = False, language: str = "ru",
              audience: str = "all_ai_bots", group: str | None = None,
              humor_allowed: bool = False, sensitive: bool = False,
              silence_requested: bool = False, recent: tuple[str, ...] = ()) -> dict:
        """Use a caller-validated intent/group; never inspect private messages."""
        flags = (addressed, local_permission, humor_allowed, sensitive, silence_requested)
        if any(type(flag) is not bool for flag in flags):
            raise ValueError("Context flags must be bool")
        if (not isinstance(recent, (tuple, list)) or len(recent) > 128
                or any(not isinstance(s, str) or len(s) > 1000 for s in recent)):
            raise ValueError("Bad recent history")
        if audience not in AUDIENCES:
            raise ValueError("Unknown audience")
        if not isinstance(intent, str):
            raise ValueError("Bad intent")
        if not addressed:
            return self._reject("not_addressed")
        if not local_permission:
            return self._reject("not_authorized")
        if silence_requested:
            return self._reject("silence_requested")
        if sensitive:
            return self._reject("sensitive_suppressed")
        if language != "ru":
            return self._reject("wrong_language")
        item = self._sets.get(intent)
        if item is None:
            return self._reject("unknown_intent")
        audiences, groups, default_group = item
        if audience not in audiences and "all_ai_bots" not in audiences:
            return self._reject("wrong_audience")
        if intent in HUMOR_INTENTS and not humor_allowed:
            return self._reject("humor_not_authorized")
        if group is None:
            if default_group is not None:
                group = default_group
            elif len(groups) == 1:
                group = next(iter(groups))
            else:
                return self._reject("group_required")
        if group not in groups:
            return self._reject("wrong_group")
        seen = {normalized(s) for s in recent}
        for index, answer in enumerate(groups[group], start=1):
            if normalized(answer) not in seen:
                return {
                    "status": "ok", "text": answer,
                    "source_id": f"{intent}:{group}:{index:03}",
                    "source_pack": PACK, "snapshot_key": self.snapshot_key,
                }
        return self._reject("repeat_suppressed")
