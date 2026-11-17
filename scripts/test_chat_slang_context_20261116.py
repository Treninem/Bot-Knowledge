#!/usr/bin/env python3
"""Read-only checks for synthetic Russian chat-slang examples (qa.v1)."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs/ru/chat_slang_context_qa.json"
DIGEST = "b3bf77b25272ac04d0ac1982bec7ca03b310cbffac4d0abe2280afc0dd130123"
IDS = {"bk_slang_life", "bk_slang_sorry", "bk_slang_imho", "bk_slang_cringe", "bk_slang_easy", "bk_slang_go", "bk_slang_thanks", "bk_slang_soon", "bk_slang_wow", "bk_slang_person", "bk_slang_rofl", "bk_slang_base"} 
SCOPES = ["direct", "private", "group_addressed"]
SOURCE_SHA = "47dda4a234ac33d332b90a26b4224ad4e0b9b9e3"

def check(ok, msg):
    if not ok:
        raise AssertionError(msg)

def norm(value):
    return " ".join(re.findall(r"\w+", value.casefold().replace("ё", "е")))

def main():
    raw = PACK.read_bytes()
    check(hashlib.sha256(raw).hexdigest() == DIGEST, "changed pack SHA")
    obj = json.loads(raw)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    refs = [x for x in manifest["packs"] if x["path"] == PACK.relative_to(ROOT).as_posix()]
    check(len(refs) == 1 and refs[0]["sha256"] == DIGEST, "manifest registration")
    check(tuple(map(int, manifest["knowledge_version"].split("."))) >= (2026, 11, 16, 12), "version regression")
    check(obj["pack_version"] == "2026.11.16.012", "source pack version")
    cat = obj["catalog"]
    check(cat["adapter"] == "qa.v1" and cat["audiences"] == ["all_ai_bots"], "audience")
    check(cat["contexts"] == SCOPES, "scope")
    check(cat["constraints"] == {"read_only": True, "requires_direct_address": True, "no_personal_data": True}, "constraints")
    records = obj["records"]
    check(len(records) == 12, "intent count")
    check({r["id"] for r in records} == IDS, "IDs changed")
    normalized = set()
    for r in records:
        check(r["language"] == "ru" and r["audiences"] == ["all_ai_bots"], "record language and audience")
        check(r["contexts"] == SCOPES and r["constraints"] == cat["constraints"], "record scope")
        check(SOURCE_SHA in r["source"] and r["source"].endswith("/docs/REQUIREMENTS_21.md"), "provenance")
        check(len(r["variants"]) == 8, "nine answer slots")
        for t in [r["answer"], *r["variants"]]:
            n = norm(t)
            check(len(n) >= 50, "content too short")
            check(n not in normalized, "duplicate phrase")
            normalized.add(n)
            check(not re.search(r"https?://|t\.me/|@[A-Za-z_]|\b\d{10,}\b", t), "personal detail")
    check(len(normalized) == 108, "total variants")
    for row in manifest["packs"]:
        other = ROOT / row["path"]
        if other == PACK or not other.exists():
            continue
        obj2 = json.loads(other.read_text(encoding="utf-8"))
        if not isinstance(obj2, dict) or not isinstance(obj2.get("records"), list):
            continue
        for r in obj2["records"]:
            if not isinstance(r, dict) or not isinstance(r.get("answer"), str):
                continue
            for t in [r["answer"], *(r.get("variants") or [])]:
                if isinstance(t, str):
                    check(norm(t) not in normalized, "cross-pack exact duplicate: " + row["path"])
    print("Chat-slang qa.v1: 12 intents, 108 contextual replies, SHA/scope/privacy/dedup OK")

if __name__ == "__main__":
    main()
