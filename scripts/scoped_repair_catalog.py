"""Opt-in, source-pinned selection for context-specific conversational repairs.

Does not infer intent/context from an incoming message, act on the world, learn,
moderate, write private data, or issue sanctions. The consumer must first
confirm the intent and context and approve exact response IDs.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/dialogue.json"
INTENTS = frozenset({"clarify_previous", "disagreement", "unknown_fact", "ambiguous"})
AUDIENCE = "all_ai_bots"
SECRET = re.compile(
    r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+|"
    r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})"
)


def norm(value: str) -> str:
    return " ".join(re.findall(
        r"[\w]+", unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    ))


class ScopedRepairCatalog:
    def __init__(self, root: Path = ROOT):
        root = Path(root)
        manifest = json.loads((root / "manifest.json").read_text("utf-8"))
        matches = [p for p in manifest.get("packs", []) if p.get("path") == PACK]
        if (manifest.get("schema_version") != 1
                or manifest.get("language") != "ru" or len(matches) != 1):
            raise ValueError("untrusted manifest")
        raw = (root / PACK).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if matches[0].get("sha256") != digest:
            raise ValueError("dialogue SHA mismatch")
        pack = json.loads(raw)
        meta = pack.get("scoped_repair_reactions", {})
        required = {
            "schema_version": 1, "section": "общение", "language": "ru",
            "audiences": [AUDIENCE], "synthetic_examples_only": True,
            "automatic_sanctions_allowed": False, "personal_data_allowed": False,
            "requires_explicit_address": True, "requires_local_permission": True,
        }
        if any(meta.get(k) != v or type(meta.get(k)) is not type(v)
               for k, v in required.items()):
            raise ValueError("unsafe policy")
        if set(meta.get("intents", {})) != INTENTS:
            raise ValueError("wrong intent inventory")

        seen_ids, seen_texts = set(), {norm(x) for key in INTENTS
                                      for x in pack["reactions"][key]}
        choices = {}
        for intent, entry in meta["intents"].items():
            contexts = entry.get("contexts")
            if (not isinstance(entry.get("canonical_question"), str)
                    or not isinstance(contexts, dict) or len(contexts) != 8
                    or entry.get("existing_legacy_count") != len(pack["reactions"][intent])):
                raise ValueError("wrong context count or legacy inventory")
            choices[intent] = {}
            for context, spec in contexts.items():
                if not isinstance(context, str) or not re.fullmatch(r"[a-z][a-z_]*", context):
                    raise ValueError("unsafe context key")
                condition, replies = spec.get("condition"), spec.get("replies")
                if (not isinstance(condition, str) or not 50 <= len(condition) <= 240
                        or not isinstance(replies, list) or len(replies) != 2):
                    raise ValueError("unverified context condition")
                answers = []
                for i, reply in enumerate(replies, 1):
                    rid, text = reply.get("id"), reply.get("text")
                    if (not isinstance(rid, str) or rid != f"repair_{intent}_{context}_{i}"
                            or rid in seen_ids or not isinstance(text, str)
                            or not 30 <= len(text) <= 300 or norm(text) in seen_texts
                            or SECRET.search(text) or reply.get("style") != "neutral"
                            or reply.get("read_only") is not True):
                        raise ValueError("duplicate or unreviewed response")
                    seen_ids.add(rid)
                    seen_texts.add(norm(text))
                    answers.append((rid, text))
                choices[intent][context] = (condition, tuple(answers))
        if len(seen_ids) != 64:
            raise ValueError("wrong response count")
        self._choices = choices
        self.count = len(seen_ids)
        self.snapshot_key = (manifest["knowledge_version"], digest)

    def select(
        self, intent: str, *, context: str, approved_reply_ids: frozenset[str],
        addressed: bool = False, local_permission: bool = False,
        audience: str = AUDIENCE, language: str = "ru",
        sensitive: bool = False, silence_requested: bool = False,
        recent_ids: tuple[str, ...] = (),
    ) -> dict | None:
        if any(type(x) is not bool for x in
               (addressed, local_permission, sensitive, silence_requested)):
            return None
        if (not isinstance(approved_reply_ids, frozenset)
                or any(not isinstance(v, str) for v in approved_reply_ids)
                or not isinstance(recent_ids, (list, tuple))
                or len(recent_ids) > 128
                or any(not isinstance(v, str) for v in recent_ids)):
            return None
        if (not addressed or not local_permission or sensitive
                or silence_requested or audience != AUDIENCE or language != "ru"
                or intent not in self._choices
                or context not in self._choices[intent]):
            return None
        condition, replies = self._choices[intent][context]
        for rid, response in replies:
            if rid in approved_reply_ids and rid not in recent_ids:
                return {
                    "id": rid, "text": response, "intent": intent,
                    "context": context, "selection_condition": condition,
                    "source_pack": PACK, "read_only": True,
                    "snapshot_key": self.snapshot_key,
                }
        return None
