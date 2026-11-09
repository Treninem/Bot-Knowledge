"""Read-only scoped-repair candidate coverage across registered + immutable stages.

Only two named stage families are included. Other source packs/stage families are
NOT silently reinterpreted as these canonical intents. This script never writes.
"""
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "packs/ru/dialogue.json"
MANIFEST = ROOT / "manifest.json"
STAGING = ROOT / "staging/ru"
INTENTS = ("clarify_previous", "disagreement", "unknown_fact", "ambiguous")
PREFIXES = ("scoped_repair_t", "social_clarity_t")
TARGET = 100


def normalize(text):
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", text).lower().replace("ё", "е")))


def source_sha_is_valid():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected = next(x["sha256"] for x in manifest["packs"] if x["path"] == "packs/ru/dialogue.json")
    actual = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError("Registered dialogue source hash differs from manifest")
    return actual


def coverage_report():
    source_sha = source_sha_is_valid()
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    buckets = {intent: {"registered": [], "staged": [], "stages": {}, "ids": set()}
               for intent in INTENTS}

    for intent in INTENTS:
        for offset, text in enumerate(source.get("reactions", {}).get(intent, ())):
            buckets[intent]["registered"].append((f"registered:legacy:{intent}:{offset}", text))
        catalog = source.get("scoped_repair_reactions", {}).get("intents", {}).get(intent, {})
        for context_name, context_data in catalog.get("contexts", {}).items():
            for offset, reply in enumerate(context_data.get("replies", ())):
                ident = reply.get("id") or f"registered:scoped:{intent}:{context_name}:{offset}"
                buckets[intent]["registered"].append((ident, reply["text"]))

    for path in sorted(STAGING.glob("*.json")):
        if not path.name.startswith(PREFIXES) or not path.name.endswith("_context_pool.json"):
            continue
        stage = json.loads(path.read_text(encoding="utf-8"))
        if stage.get("source_pack") != "packs/ru/dialogue.json":
            continue
        if stage.get("source_pack_manifest_sha256") != source_sha:
            raise ValueError(f"Stage source SHA changed: {path.name}")
        if stage.get("consumer_registered") is not False:
            raise ValueError(f"Stage registration must be explicit: {path.name}")
        for entry in stage.get("entries", ()):
            intent = entry.get("intent_id")
            if intent not in buckets:
                continue
            records = [(reply["id"], reply["text"]) for reply in entry.get("replies", ())]
            if path.name in buckets[intent]["stages"]:
                raise ValueError(f"Duplicate intent entry within {path.name}: {intent}")
            buckets[intent]["stages"][path.name] = len(records)
            buckets[intent]["staged"].extend(records)

    output = {"source_pack_sha256": source_sha, "target_per_intent": TARGET,
              "scope": list(PREFIXES), "intents": {}}
    for intent, bucket in buckets.items():
        registered = bucket["registered"]
        staged = bucket["staged"]
        records = registered + staged
        keys = [identifier for identifier, _ in records]
        if len(keys) != len(set(keys)):
            raise ValueError(f"Duplicate candidate IDs in {intent}")
        normalized = [normalize(text) for _, text in records]
        if not all(normalized):
            raise ValueError(f"Empty response in {intent}")
        unique = len(set(normalized))
        total = len(records)
        output["intents"][intent] = {
            "registered": len(registered),
            "staged": len(staged),
            "candidate_total": total,
            "normalized_unique": unique,
            "normalized_duplicates": total - unique,
            "target": TARGET,
            "over_target": max(0, total - TARGET),
            "remaining": max(0, TARGET - total),
            "is_candidate_complete": unique >= TARGET,
            "stages": dict(sorted(bucket["stages"].items())),
        }
    output["total_registered"] = sum(x["registered"] for x in output["intents"].values())
    output["total_staged"] = sum(x["staged"] for x in output["intents"].values())
    output["total_candidates"] = sum(x["candidate_total"] for x in output["intents"].values())
    output["over_target_total"] = sum(x["over_target"] for x in output["intents"].values())
    return output


if __name__ == "__main__":
    print(json.dumps(coverage_report(), ensure_ascii=False, indent=2, sort_keys=True))
