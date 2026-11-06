"""Opt-in incremental overlay for an already validated staged RU dialogue pool.

The parent remains immutable. Never uses message content to approve a reply,
never writes to users or bots, and fails closed on a moved parent/source.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import unicodedata
from scripts.staged_context_selector import StagedContextSelector, StagedSelection

DELTA = "staging/ru/spoken_pragmatics_t270_delta.json"
PARENT = "staging/ru/spoken_pragmatics_t251_context_pool.json"
SOURCE = "packs/ru/spoken_pragmatics_qa.json"
GUARDS = {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
SECRET = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")
CONTEXTS = {"direct", "private", "group_addressed"}

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P", "S"} else c for c in s).split())

def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def jaccard(a: str, b: str) -> float:
    aa, bb = set(norm(a).split()), set(norm(b).split())
    return len(aa & bb) / max(1, len(aa | bb))

class SpokenDeltaOverlay:
    """A deliberately explicit, read-only second layer. No automatic opt-in."""

    def __init__(self, root: Path, delta_path: str = DELTA):
        if delta_path != DELTA:
            raise ValueError("unreviewed delta path")
        root = Path(root).resolve(strict=True)
        self.parent = StagedContextSelector(root, PARENT)
        parent_raw = (root / PARENT).read_bytes()
        source_raw = (root / SOURCE).read_bytes()
        delta = json.loads((root / delta_path).read_text("utf-8"))
        source = json.loads(source_raw)
        old = json.loads(parent_raw)
        manifest = json.loads((root / "manifest.json").read_text("utf-8"))
        registered = {p["path"]: p["sha256"] for p in manifest["packs"]}
        if (delta.get("schema_version") != 1
            or delta.get("delta_type") != "supplemental_contextual_reply_delta"
            or delta.get("consumer_registered") is not False
            or delta.get("language") != "ru"
            or delta.get("audiences") != ["all_ai_bots"]
            or delta.get("constraints") != GUARDS
            or delta.get("source_pack") != SOURCE
            or delta.get("parent_stage") != PARENT
            or delta.get("source_pack_manifest_sha256") != registered[SOURCE]
            or hashlib.sha256(source_raw).hexdigest() != registered[SOURCE]
            or delta.get("source_pack_blob_sha") != blob_sha(source_raw)
            or delta.get("parent_stage_blob_sha") != blob_sha(parent_raw)
            or delta_path in registered):
            raise ValueError("delta/source/parent scope mismatch")
        rows = {row["id"]: row for row in source["records"]}
        oldrows = {row["intent_id"]: row for row in old["entries"]}
        if len(rows) != len(source["records"]) or len(oldrows) != len(rows):
            raise ValueError("invalid base inventory")
        known_ids, global_texts, prior_by_id = set(), set(), {}
        for row in source["records"]:
            for text in (row["answer"], *row["variants"]):
                global_texts.add(norm(text))
        for row in old["entries"]:
            prior_by_id[row["intent_id"]] = [x["text"] for x in row["replies"]]
            for reply in row["replies"]:
                known_ids.add(reply["id"])
                global_texts.add(norm(reply["text"]))
        new = {}
        new_count = 0
        for entry in delta.get("entries", []):
            ident = entry.get("intent_id")
            if (ident not in rows or ident in new or entry.get("question") != rows[ident]["question"]
                or entry.get("registered_reply_count") != 1 + len(rows[ident]["variants"])
                or entry.get("parent_staged_reply_count") != len(oldrows[ident]["replies"])
                or entry.get("delta_reply_count") != len(entry.get("replies", []))
                or not entry.get("replies")):
                raise ValueError("stale or malformed canonical intent")
            prior = [rows[ident]["answer"], *rows[ident]["variants"], *prior_by_id[ident]]
            selected = []
            notes = set()
            for reply in entry["replies"]:
                rid, text = reply.get("id"), reply.get("text")
                if (not isinstance(rid, str) or not rid.startswith(ident + "_t270_")
                    or not re.fullmatch(r"[A-Za-z0-9_-]{1,96}", rid)
                    or rid in known_ids or not isinstance(text, str) or not 1 <= len(text) <= 1600
                    or SECRET.search(text)
                    or reply.get("language") != "ru" or reply.get("style") != "neutral"
                    or reply.get("audiences") != ["all_ai_bots"] or reply.get("read_only") is not True
                    or reply.get("context") not in CONTEXTS
                    or not isinstance(reply.get("context_note"), str)
                    or not reply["context_note"].strip()
                    or not isinstance(reply.get("avoid"), str) or not reply["avoid"].strip()):
                    raise ValueError("invalid reply metadata or privacy")
                n = norm(text)
                note = norm(reply["context_note"])
                if not n or n in global_texts or note in notes:
                    raise ValueError("exact duplicate text or situation")
                if max((jaccard(text, other) for other in prior), default=0) >= .78:
                    raise ValueError("near-duplicate within canonical intent")
                notes.add(note)
                global_texts.add(n)
                known_ids.add(rid)
                prior.append(text)
                selected.append(reply)
            if len(selected) + len(prior_by_id[ident]) + 1 + len(rows[ident]["variants"]) > 100:
                raise ValueError("per-intent cap breached")
            new[ident] = tuple(selected)
            new_count += len(selected)
        cp = delta.get("checkpoint", {})
        expected = {
            "processed_intents": len(rows),
            "registered_count": sum(1 + len(x["variants"]) for x in rows.values()),
            "parent_staged_count": sum(len(x["replies"]) for x in old["entries"]),
            "added_in_current": new_count,
            "added_candidates": new_count,
            "total_staged_with_parent": new_count + sum(len(x["replies"]) for x in old["entries"]),
            "remaining_total": sum(100 - (1 + len(row["variants"])) - len(oldrows[ident]["replies"]) - len(new[ident]) for ident, row in rows.items()),
            "partial_intents": sum(1 for ident, row in rows.items() if 1 + len(row["variants"]) + len(oldrows[ident]["replies"]) + len(new[ident]) < 100),
            "finished_100": sum(1 for ident, row in rows.items() if 1 + len(row["variants"]) + len(oldrows[ident]["replies"]) + len(new[ident]) == 100),
        }
        if len(new) != len(rows) or any(cp.get(k) != v for k, v in expected.items()):
            raise ValueError("checkpoint and verified inventory differ")
        self._delta = new
        self.checkpoint = cp
        self.cache_identity = (manifest["knowledge_version"], blob_sha(parent_raw), blob_sha((root / delta_path).read_bytes()))

    def select(self, intent_id: str, *, approved_reply_ids: frozenset[str], audience: str,
               context: str, addressed: bool = False, local_permission: bool = False,
               recent_ids: tuple[str, ...] = ()) -> StagedSelection | None:
        if (not addressed or not local_permission or audience != "all_ai_bots"
            or context not in CONTEXTS or not isinstance(approved_reply_ids, frozenset)
            or not approved_reply_ids or not isinstance(recent_ids, tuple)):
            return None
        for reply in self._delta.get(intent_id, ()):
            if (reply["id"] in approved_reply_ids and reply["id"] not in recent_ids
                and reply["context"] == context):
                return StagedSelection(id=reply["id"], text=reply["text"], intent_id=intent_id,
                    context_note=reply["context_note"], stage_path=DELTA)
        return None
