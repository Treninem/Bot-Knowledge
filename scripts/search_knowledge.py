"""Offline SHA-verified retrieval over portable, approved packs.

This code is a local reference implementation. It does not connect to GitHub,
learn autonomously, make moderation decisions or grant administrative powers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIENCES = {"all_ai_bots", "chat_moderators", "community_bots"}
WORDS = re.compile(r"[a-zа-яё0-9]+", re.IGNORECASE)

def exact_phrase(text: str) -> str:
    return " ".join(WORDS.findall(text.casefold().replace("ё", "е")))
STOP = {"это", "мне", "для", "что", "как", "или", "with", "the", "and", "you", "are"}

def tokens(text: str) -> set[str]:
    words = set()
    for raw in WORDS.findall(text.casefold().replace("ё", "е")):
        if len(raw) < 3 or raw in STOP:
            continue
        words.add(raw)
        if len(raw) >= 7:
            words.add(raw[:5] + "~")
    return words

def searchable_text(item: dict) -> str:
    fields = ("id", "topic", "category", "kind", "domain", "classification",
              "context", "input", "message", "local_rule", "reason",
              "response", "meaning_ru", "when", "avoid", "examples",
              "expected_behavior", "forbidden_behavior", "expression", "source", "semantic_guard")
    values = []
    for key in fields:
        value = item.get(key)
        if isinstance(value, str):
            values.append(value)
        elif isinstance(value, list):
            values.extend(x for x in value if isinstance(x, str))
    for reading in item.get("readings", ()):
        if isinstance(reading, dict):
            for name in ("context", "meaning", "suggested_response"):
                if isinstance(reading.get(name), str):
                    values.append(reading[name])
            values.extend(c for c in reading.get("cues", ()) if isinstance(c, str))
    # Do not index deliberately incorrect counterexamples as approved text.
    variants = item.get("variants", {})
    if isinstance(variants, dict):
        values.extend(v for v in variants.values() if isinstance(v, str))
    return " ".join(values)

class KnowledgeSearch:
    def __init__(self, root: Path = ROOT):
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        self.records: list[dict] = []
        self.inverted: dict[str, set[int]] = defaultdict(set)
        self.exact: dict[str, set[int]] = defaultdict(set)
        for info in manifest["packs"]:
            rel = info["path"]
            if not rel.startswith("packs/ru/") or ".." in Path(rel).parts:
                raise ValueError("Unsafe pack path")
            payload = (root / rel).read_bytes()
            if hashlib.sha256(payload).hexdigest() != info["sha256"]:
                raise ValueError("SHA mismatch: " + rel)
            pack = json.loads(payload.decode("utf-8"))
            for key in ("skills", "cases", "intents", "pairs", "triggers", "paraphrases"):
                for item in pack.get(key, []):
                    if not isinstance(item, dict):
                        continue
                    audiences = item.get("audiences", ["all_ai_bots"])
                    if not isinstance(audiences, list) or not set(audiences) <= AUDIENCES:
                        raise ValueError("Bad audience: " + rel)
                    contents = searchable_text(item)
                    record = {
                        "id": item.get("id", ""),
                        "pack": rel,
                        "audiences": audiences,
                        "topic": item.get("target_case_id", item.get("topic", item.get("kind", item.get("category", "")))),
                        "expression": item.get("expression") or item.get("source") or (item.get("input", "") if "target_case_id" in item or "expected_ids" in item else ""),
                        "preview": (item.get("expression") or item.get("response") or item.get("reason")
                                    or item.get("source") or item.get("input") or item.get("message")
                                    or (item.get("examples") or [""])[0])[:220],
                    }
                    index = len(self.records)
                    self.records.append(record)
                    if isinstance(record["expression"], str) and record["expression"].strip():
                        self.exact[exact_phrase(record["expression"])].add(index)
                    for term in tokens(contents):
                        self.inverted[term].add(index)

    @lru_cache(maxsize=512)
    def search(self, query: str, audience: str = "all_ai_bots", limit: int = 5) -> tuple[tuple, ...]:
        if audience not in AUDIENCES:
            raise ValueError("Unknown audience")
        if not 1 <= limit <= 20:
            raise ValueError("Invalid limit")
        terms = tokens(query)
        if not terms:
            return ()
        allowed = {"all_ai_bots", audience}
        scores: dict[int, int] = defaultdict(int)
        for term in terms:
            for i in self.inverted.get(term, ()):
                if allowed.intersection(self.records[i]["audiences"]):
                    scores[i] += 1
        # Rank an exact phrase above loose token overlap, after audience filtering.
        for i in self.exact.get(exact_phrase(query), ()):
            if allowed.intersection(self.records[i]["audiences"]):
                scores[i] += max(10, 3 * len(terms))
        ranked = sorted(scores, key=lambda i: (-scores[i], self.records[i]["id"]))
        return tuple((self.records[i]["id"], self.records[i]["pack"],
                      self.records[i]["topic"], self.records[i]["preview"])
                     for i in ranked[:limit])

def main() -> None:
    parser = argparse.ArgumentParser(description="Search local approved knowledge without network calls")
    parser.add_argument("--query", required=True)
    parser.add_argument("--audience", choices=sorted(AUDIENCES), default="all_ai_bots")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    started = time.perf_counter()
    index = KnowledgeSearch()
    result = index.search(args.query, args.audience, args.limit)
    elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
    print(json.dumps({"query": args.query, "audience": args.audience,
                      "loaded_records": len(index.records),
                      "load_and_first_query_ms": elapsed_ms,
                      "results": [{"id": x[0], "pack": x[1], "topic": x[2], "preview": x[3]}
                                  for x in result]}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
