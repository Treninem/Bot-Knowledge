"""Executable RU/EN discourse relation contracts: 30 cases, 90 choices."""
from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path

from discourse_links import DiscourseLinks, PACK, ROOT, REGISTERS, load_pack
from search_knowledge import KnowledgeSearch
from validate_discourse_links import validate_discourse

assert validate_discourse() == [], validate_discourse()
book = load_pack()
cases = book["cases"]
assert len(cases) == 30
engine = DiscourseLinks()
index = KnowledgeSearch()
assert len(index.records) == 1131, len(index.records)
assert len({row["id"] for row in cases}) == 30

for row in cases:
    for tone in REGISTERS:
        proposal = engine.suggest(relation=row["relation"],
            confirmed_relation=row["relation"], language=row["language"],
            register=tone)
        assert proposal["status"] == "proposal", (row["id"], proposal)
        assert proposal["connector"] == row["variants"][tone]
        assert proposal["relation"] == row["relation"]
        assert proposal["id"] == row["id"]
        assert engine.suggest(relation=row["relation"],
            confirmed_relation=row["wrong_relation"],
            language=row["language"], register=tone)["status"] == "relation_conflict"
        assert engine.suggest(relation=row["relation"],
            confirmed_relation=None, language=row["language"],
            register=tone)["status"] == "needs_semantic_context"
        assert engine.suggest(relation=row["relation"],
            confirmed_relation=row["relation"], language=row["language"],
            register=tone, addressed=False)["status"] == "not_addressed"
        assert engine.suggest(relation=row["relation"],
            confirmed_relation=row["relation"], language=row["language"],
            register=tone, quoted=True)["status"] == "quoted_ignored"
        assert engine.suggest(relation=row["relation"],
            confirmed_relation=row["relation"], language=row["language"],
            register=tone, recent=[row["variants"][tone]])["status"] == "already_used"
    hits = index.search(row["input"], "all_ai_bots", 20)
    assert hits and hits[0][0] == row["id"], (row["id"], hits)
    assert hits[0][1] == PACK

assert engine.suggest(relation="unknown", confirmed_relation="unknown")["status"] == "unknown_relation"
for invalid in (
    {"language": "de"}, {"register": "coercive"}, {"audience": "administrator"},
    {"addressed": "yes"}, {"quoted": 1}, {"recent": "x"},
    {"recent": ["a"] * 17}, {"recent": [0]}, {"relation": 5},
):
    kwargs = dict(relation="addition", confirmed_relation="addition")
    kwargs.update(invalid)
    try:
        engine.suggest(**kwargs)
    except ValueError:
        pass
    else:
        raise AssertionError("Accepted invalid caller parameter: " + str(invalid))

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / PACK).parent.mkdir(parents=True)
    (root / "manifest.json").write_bytes((ROOT / "manifest.json").read_bytes())
    (root / PACK).write_bytes((ROOT / PACK).read_bytes() + b" ")
    try:
        DiscourseLinks(root)
    except ValueError as exc:
        assert "SHA-256" in str(exc)
    else:
        raise AssertionError("Accepted tampered discourse pack")

start = time.perf_counter()
for cycle in range(1, 11):
    for row in cases:
        for register in REGISTERS:
            assert engine.suggest(relation=row["relation"],
                confirmed_relation=row["relation"], language=row["language"],
                register=register)["status"] == "proposal"
    print(f"DISCOURSE_PASS {cycle}/10 cases=30 registers=3")
for _ in range(1000):
    assert engine.suggest(relation="concession",
        confirmed_relation="concession", language="en",
        register="neutral")["connector"] == "Nevertheless"
print(f"DISCOURSE_1000_CALLS_OK elapsed_with_10_rounds_ms={(time.perf_counter()-start)*1000:.2f}")
print("DISCOURSE_10_ROUNDS_OK")
