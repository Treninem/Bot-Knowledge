"""Regression checks for scoped, non-intrusive greeting response variety."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIALOGUE = "packs/ru/dialogue.json"
BASE_ANSWERS = (
    "Привет. Я на связи. Что нужно разобрать?",
    "Привет. Слушаю — можем решить вопрос по чату или просто поговорить.",
)

def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def normal(text: str) -> str:
    return re.sub(r"[\\W_]+", "", text.casefold().replace("ё", "е"))

def walk_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from walk_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from walk_strings(item)

def main() -> int:
    manifest = read("manifest.json")
    entry = [x for x in manifest["packs"] if x["path"] == DIALOGUE]
    assert len(entry) == 1, "dialogue should occur once in manifest"
    actual = hashlib.sha256((ROOT / DIALOGUE).read_bytes()).hexdigest()
    assert actual == entry[0]["sha256"], "greeting pack SHA mismatch"
    pack = read(DIALOGUE)
    assert pack["schema_version"] == 1 and pack["language"] == "ru"
    assert pack["pack_version"] == manifest["knowledge_version"], "cache version must change with pack"
    replies = pack["reactions"]["greeting"]
    assert len(replies) == 22, "expected first increment: 2 existing + 20 new"
    assert tuple(replies[:2]) == BASE_ANSWERS, "do not rewrite legacy consumer replies"
    normalized = [normal(x) for x in replies]
    assert len(normalized) == len(set(normalized)), "duplicate greeting responses"
    assert all(isinstance(x, str) and 15 <= len(x) <= 180 for x in replies)
    assert all(not any(z in x.casefold() for z in ("правила", "📜", "🧩", "автобан", "накаж", "github")) for x in replies), "unwanted help/moderation injected into greeting"
    # No repeat of the new answers already carried by other verified packs.
    existing = set()
    for item in manifest["packs"]:
        path = item["path"]
        if path != DIALOGUE:
            existing.update(normal(x) for x in walk_strings(read(path)))
    assert all(normal(x) not in existing for x in replies[2:]), "duplicate with another pack"
    intents = read("packs/ru/intents.json")["intents"]
    greeting = [x for x in intents if x["id"] == "greeting"]
    assert len(greeting) == 1 and "привет" in greeting[0]["examples"]
    print("PASS greeting replies: +20, 22/100; no normalized/cross-pack duplicates; SHA/version and intent OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
