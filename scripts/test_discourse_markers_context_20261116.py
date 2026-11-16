#!/usr/bin/env python3
"""QA for the 2026-11-16 contextual Russian discourse-marker pack."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = Path("packs/ru/discourse_markers_context_qa.json")
EXPECTED_SHA256 = "0737b244d7e0fcaa7bf89259a235c8a73c7af5e13f30d5e41bfd72fbbe7da1d0"
EXPECTED_INTENTS = {
    "listen", "youknow", "imagine", "shorter", "thatis", "bytheway",
    "frankly", "they_say", "sortof", "wellthere", "guesswhat", "actually",
    "holdon", "onemore", "inwhatway",
}


def check(condition: bool, message: str = "QA invariant failed") -> None:
    # Keep test checks active under python -O.
    if not condition:
        raise AssertionError(message)


def normalized(value: str) -> str:
    value = value.casefold().replace("ё", "е")
    return " ".join(re.findall(r"\w+", value, flags=re.UNICODE))


def phrases(record: dict) -> list[str]:
    return [record["answer"], *record.get("variants", [])]


def main() -> None:
    raw = (ROOT / PACK).read_bytes()
    check(hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256, "candidate pack changed")
    data = json.loads(raw)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    check(data["schema_version"] == 1 and data["pack_version"] == "2026.11.16.011", "QA invariant failed")
    check(manifest["knowledge_version"] == "2026.11.16.011", "QA invariant failed")
    entry = [x for x in manifest["packs"] if x["path"] == PACK.as_posix()]
    check(len(entry) == 1 and entry[0]["sha256"] == EXPECTED_SHA256, "QA invariant failed")
    check(data["language"] == "ru" and data["catalog"]["adapter"] == "qa.v1", "QA invariant failed")
    check(data["catalog"]["audiences"] == ["all_ai_bots"], "QA invariant failed")
    check(data["catalog"]["constraints"]["read_only"] is True, "QA invariant failed")
    records = data["records"]
    check(len(records) == 15, "QA invariant failed")
    check({r["id"].removeprefix("bk_discourse_marker_") for r in records} == EXPECTED_INTENTS, "QA invariant failed")
    current: set[str] = set()
    for r in records:
        check(len(r["variants"]) == 8, "QA invariant failed")
        check(r["language"] == "ru" and r["audiences"] == ["all_ai_bots"], "QA invariant failed")
        check(r["constraints"]["read_only"] is True, "QA invariant failed")
        check(r["constraints"]["requires_direct_address"] is True, "QA invariant failed")
        check(r["constraints"]["no_personal_data"] is True, "QA invariant failed")
        check(r["source"].endswith("/docs/REQUIREMENTS_21.md"), "QA invariant failed")
        for sentence in phrases(r):
            check(isinstance(sentence, str) and 20 <= len(sentence) <= 320, "QA invariant failed")
            key = normalized(sentence)
            check(key and key not in current, f"internal duplicate: {r['id']}")
            current.add(key)
    check(len(current) == 135, "QA invariant failed")
    # Cross-check against all existing registered response records, not just neighbours.
    others: dict[str, tuple[str, str]] = {}
    for item in manifest["packs"]:
        if item["path"] == PACK.as_posix():
            continue
        p = ROOT / item["path"]
        obj = json.loads(p.read_text(encoding="utf-8"))
        for r in obj.get("records", []):
            if not isinstance(r, dict) or not isinstance(r.get("answer"), str):
                continue
            for s in phrases(r):
                if isinstance(s, str):
                    others.setdefault(normalized(s), (item["path"], str(r.get("id"))))
    overlap = current.intersection(others)
    check(not overlap, f"cross-pack normalized duplicates: {[(s, others[s]) for s in sorted(overlap)[:10]]}")
    # Language data cannot silently become a command to issue sanctions.
    forbidden = re.compile(r"\b(?:забаню|забанить|замьючу|замутить|заблокирую|оштрафую)\b", re.I)
    check(not any(forbidden.search(s) for r in records for s in phrases(r)), "QA invariant failed")
    print(f"PASS: 15 intents, 135 unique replies, no cross-pack exact duplicates; SHA-256 {EXPECTED_SHA256}")


if __name__ == "__main__":
    main()
