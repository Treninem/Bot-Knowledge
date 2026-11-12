"""Read-only cross-catalog coverage for four stable conversation intents.

Only delta records are added; checkpoint cumulative counts are NEVER added again.
No networking, cache writes, sanctions, or consumer registration.
"""
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTENTS = ("clarify_previous", "disagreement", "unknown_fact", "ambiguous")
STAGES = (
    "scoped_repair_t486_context_pool.json",
    "scoped_repair_t487_context_pool.json",
    "scoped_repair_t488_context_pool.json",
    "social_clarity_t493_context_pool.json",
    "social_clarity_t496_context_pool.json",
    "social_clarity_t497_context_pool.json",
    "social_clarity_t498_context_pool.json",
)
TARGET = 100

def normalized(value):
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", value).lower().replace("ё", "е")))

def calculate(root=ROOT):
    root = Path(root)
    pack_path = root / "packs/ru/dialogue.json"
    pack_bytes = pack_path.read_bytes()
    manifest = json.loads((root / "manifest.json").read_text("utf-8"))
    expected = next(item["sha256"] for item in manifest["packs"] if item["path"] == "packs/ru/dialogue.json")
    if hashlib.sha256(pack_bytes).hexdigest() != expected:
        raise ValueError("registered dialogue pack SHA-256 mismatch")
    pack = json.loads(pack_bytes)
    source = pack["scoped_repair_reactions"]["intents"]
    counters = {}
    texts = {}
    for intent in INTENTS:
        originals = list(pack["reactions"][intent])
        for context in source[intent]["contexts"].values():
            originals.extend(context["replies"])
        registered = len(originals)
        counters[intent] = {"intent_id": intent, "registered": registered, "staged": 0, "candidate_total": registered, "target": TARGET, "over_target": 0, "missing": 0}
        texts[intent] = set()
        for reply in originals:
            value = reply if isinstance(reply,str) else reply.get("text", reply.get("reply", ""))
            key = normalized(value)
            if not key or key in texts[intent]:
                raise ValueError(f"blank or repeated registered reply for {intent}")
            texts[intent].add(key)
    ids = set()
    for filename in STAGES:
        path = root / "staging/ru" / filename
        stage = json.loads(path.read_text("utf-8"))
        if stage.get("consumer_registered") is not False:
            raise ValueError(f"Unexpected consumer registration in {filename}")
        stage_count = 0
        for entry in stage["entries"]:
            intent = entry["intent_id"]
            if intent not in counters:
                raise ValueError(f"Untracked intent {intent} in {filename}")
            for reply in entry["replies"]:
                ident = reply["id"]
                norm = normalized(reply["text"])
                if ident in ids or not norm or norm in texts[intent]:
                    raise ValueError(f"Duplicate ID or text in {filename}: {ident}")
                ids.add(ident)
                texts[intent].add(norm)
                stage_count += 1
                counters[intent]["staged"] += 1
        if stage_count != stage["checkpoint"]["added_candidates"]:
            raise ValueError(f"Stage delta mismatch in {filename}")
    for item in counters.values():
        item["candidate_total"] = item["registered"] + item["staged"]
        item["over_target"] = max(0, item["candidate_total"] - TARGET)
        item["missing"] = max(0, TARGET - item["candidate_total"])
    return {"schema_version": 1, "registration": "registered_plus_unconsumed_staging", "registered": sum(r["registered"] for r in counters.values()), "staged": sum(r["staged"] for r in counters.values()), "candidate_total": sum(r["candidate_total"] for r in counters.values()), "newly_completed_intents_since_T488": 0, "intents": list(counters.values())}

if __name__ == "__main__":
    print(json.dumps(calculate(), ensure_ascii=False, sort_keys=True, indent=2))
