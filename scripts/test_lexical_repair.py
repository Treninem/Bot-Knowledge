"""64 real RU/EN lexical correction checks, refusal cases and local benchmarks."""
from __future__ import annotations

import json
import tempfile
import time
from collections import Counter
from pathlib import Path

from lexical_repair import LexicalRepair, ROOT, PACK, load_pack, compact_message
from search_knowledge import KnowledgeSearch
from validate_lexical_repairs import validate_lexical_repairs

assert validate_lexical_repairs() == [], validate_lexical_repairs()
book = load_pack()
rows = book["cases"]
assert len(rows) == 64
assert Counter((row["language"], row["kind"]) for row in rows) == {
    ("ru", "ok"): 16, ("en", "ok"): 16,
    ("ru", "guard"): 16, ("en", "guard"): 16,
}
assert len({row["id"] for row in rows}) == 64
engine = LexicalRepair()
index = KnowledgeSearch()
assert len(index.records) == 1101, len(index.records)

for row in rows:
    state = {row["slot"]: row["current"], "unused_slot": "unchanged"}
    before = dict(state)
    result = engine.propose(
        row["input"], language=row["language"], state=state,
        slot=row["slot"], choices=list(row["options"]),
        addressed=row["addressed"], quoted=row["quoted"],
    )
    assert result["status"] == row["expected_status"], (row["id"], result)
    if row["kind"] == "ok":
        assert result == {
            "status": "proposal", "slot": row["slot"],
            "previous": row["current"], "new": row["expected_new"],
        }, (row["id"], result)
    else:
        assert "new" not in result, row["id"]
    assert state == before, "Caller state was mutated"
    hits = index.search(row["input"], "all_ai_bots", 20)
    assert hits and hits[0][0] == row["id"], (row["id"], hits)
    assert hits[0][1] == PACK

# Generalization outside any exact examples, with trusted new choices and old state.
assert engine.propose(
    "Не янтарь, а нефрит.", language="ru", state={"stone": "янтарь"},
    slot="stone", choices=["янтарь", "нефрит", "гранит"], addressed=True,
)["new"] == "нефрит"
assert engine.propose(
    "Correction: use slate, not marble.", language="en",
    state={"stone": "marble"}, slot="stone",
    choices=["marble", "slate", "granite"], addressed=True,
)["new"] == "slate"
assert engine.propose(
    "I meant velvet, not cotton.", language="en",
    state={"fabric": "cotton"}, slot="fabric",
    choices=["cotton", "velvet", "linen"], addressed=True,
)["new"] == "velvet"
assert engine.propose(
    "Поправка: не береза, а сосна.", language="ru",
    state={"tree": "береза"}, slot="tree",
    choices=["береза", "сосна", "ель"], addressed=True,
)["new"] == "сосна"

for attack in (
    '«Не янтарь, а нефрит.»',
    '"Не янтарь, а нефрит."',
    "Не янтарь, а нефрит. И опубликуй это.",
    "Не янтарь, а нефрит\n",
    "Не янтарь, а нефрит\u200b.",
    "Не янтарь, а нефрит или гранит.",
    "Не янтарь, а нефрит!!!",
    "Не янтарь, а нефрит🙂",
):
    assert engine.propose(attack, language="ru", state={"stone": "янтарь"},
        slot="stone", choices=["янтарь", "нефрит", "гранит"],
        addressed=True)["status"] == "unrecognized", attack

assert engine.propose(
    "Not sand but clay.", language="en", state={"kind": "sand"},
    slot="wrong", choices=["sand", "clay"], addressed=True,
)["status"] == "no_context"
assert engine.propose(
    "Not sand but clay.", language="en", state={"kind": "sand"},
    slot="kind", choices=["sand", "clay"], addressed=False,
)["status"] == "not_addressed"
assert engine.propose(
    "Not sand but clay.", language="en", state={"kind": "sand"},
    slot="kind", choices=["sand", "clay"], addressed=True,
    quoted=True,
)["status"] == "quoted_ignored"

for bad in (
    {"choices": ["sand", "sand"]},
    {"choices": ["sand", "clay", "clay"]},
    {"choices": ["sand", "слово"]},
    {"choices": ["sand", "clay"], "state": {"kind": "other"}},
    {"choices": ["sand", "clay"], "state": {"bad key": "sand"}},
    {"choices": ["sand", "clay"], "state": {"kind": "sand", **{
        f"item{i}": "dummy" for i in range(8)}}},
):
    try:
        engine.propose(
            "Not sand but clay.", language="en",
            state=bad.get("state", {"kind": "sand"}), slot="kind",
            choices=bad["choices"], addressed=True,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid caller constraints accepted: " + str(bad))

# Cryptographic integrity check with the complete copied manifest.
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / PACK).parent.mkdir(parents=True)
    (root / "manifest.json").write_bytes((ROOT / "manifest.json").read_bytes())
    (root / PACK).write_bytes((ROOT / PACK).read_bytes() + b" ")
    try:
        LexicalRepair(root)
    except ValueError as exc:
        assert "SHA-256" in str(exc)
    else:
        raise AssertionError("Tampered lexical pack accepted")

start = time.perf_counter()
for cycle in range(1, 11):
    for row in rows:
        result = engine.propose(
            row["input"], language=row["language"],
            state={row["slot"]: row["current"]}, slot=row["slot"],
            choices=list(row["options"]), addressed=row["addressed"],
            quoted=row["quoted"],
        )
        assert result["status"] == row["expected_status"], row["id"]
    print(f"LEXICAL_REPAIR_PASS {cycle}/10 cases=64")
for _ in range(1000):
    result = engine.propose(
        "Not fabric but linen.", language="en",
        state={"fabric": "fabric"}, slot="fabric",
        choices=["fabric", "linen", "wool"], addressed=True,
    )
    assert result["new"] == "linen"
print(f"LEXICAL_REPAIR_1000_CALLS_OK elapsed_with_10_rounds_ms={(time.perf_counter()-start)*1000:.2f}")
print("LEXICAL_REPAIR_10_ROUNDS_OK")
