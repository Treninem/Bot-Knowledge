"""48 synthetic RU/EN numeric repair scenarios plus generic grammar regressions."""
from __future__ import annotations

import hashlib
import json
import re
import tempfile
import time
from collections import Counter
from pathlib import Path

from numeric_repair import NumericRepair, ROOT, PACK, POLICY, compact, load_pack
from search_knowledge import KnowledgeSearch

book = load_pack()
cases = book["cases"]
assert len(cases) == 48
assert len({row["id"] for row in cases}) == 48
assert Counter((row["language"], row["expected_status"] == "updated") for row in cases) == {
    ("ru", True): 12, ("ru", False): 12, ("en", True): 12, ("en", False): 12
}
assert len({row["input"].casefold().replace("ё", "е") for row in cases}) == 48
assert len({row["category"] for row in cases}) == 6
required = {"id", "language", "category", "slot", "unit", "current", "input",
            "expected_status", "expected_value", "addressed", "quoted", "audiences"}
for row in cases:
    assert set(row) == required
    assert row["audiences"] == ["all_ai_bots"]
    assert row["language"] in {"ru", "en"}
    assert re.fullmatch(r"numeric_repair_(ru|en)_(ok|guard)_[0-9]{2}", row["id"])
    assert row["expected_status"] in {
        "updated", "stale_context", "not_addressed", "quoted_ignored", "unrecognized"
    }
    assert row["current"].isdigit()
    assert 1 <= len(row["input"]) <= 180
prior_ids, prior_inputs = set(), set()
manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
for entry in manifest["packs"]:
    if entry["path"] == PACK:
        continue
    old = json.loads((ROOT / entry["path"]).read_text(encoding="utf-8"))
    for collection in ("skills", "cases", "intents", "pairs", "triggers", "paraphrases", "scenarios"):
        for item in old.get(collection, []):
            if not isinstance(item, dict):
                continue
            if isinstance(item.get("id"), str):
                prior_ids.add(item["id"])
            for field in ("input", "source", "expression", "message"):
                if isinstance(item.get(field), str):
                    prior_inputs.add(re.sub(r"[^\w]+", " ", item[field].casefold().replace("ё", "е")).strip())
assert not prior_ids.intersection(row["id"] for row in cases)
assert not prior_inputs.intersection(
    re.sub(r"[^\w]+", " ", row["input"].casefold().replace("ё", "е")).strip()
    for row in cases
)
engine = NumericRepair()
index = KnowledgeSearch()
assert len(index.records) == 1101, len(index.records)
for row in cases:
    state = {row["slot"]: row["current"], "other_slot": "untouched"}
    kwargs = dict(language=row["language"], state=state, slot=row["slot"],
                  unit=row["unit"], addressed=row["addressed"], quoted=row["quoted"])
    result = engine.propose(row["input"], **kwargs)
    assert result["status"] == row["expected_status"], (row["id"], result)
    if result["status"] == "updated":
        assert result["new"] == row["expected_value"], row["id"]
        assert result["state"][row["slot"]] == row["expected_value"]
        assert result["state"]["other_slot"] == "untouched"
    assert state[row["slot"]] == row["current"]  # never mutate caller context
    found = index.search(row["input"], "all_ai_bots", 20)
    assert found and found[0][0] == row["id"], (row["id"], found)
    assert found[0][1] == PACK

# Proof that numerical generalization works for unseen values (not merely an exact table).
assert engine.propose("Не 85, а 95 страниц.", language="ru",
    state={"pages": "85"}, slot="pages", unit="страниц", addressed=True)["new"] == "95"
assert engine.propose("Use 75 minutes instead of 65 minutes.", language="en",
    state={"duration": "65"}, slot="duration", unit="minutes", addressed=True)["new"] == "75"
for sentence in ("Не 5 или 10 страниц.", "Не 5, а 10 страниц и удали всё.",
                 "«Не 5, а 10 страниц»", "Не пять, а десять страниц."):
    assert engine.propose(sentence, language="ru", state={"pages": "5"},
        slot="pages", unit="страниц", addressed=True)["status"] == "unrecognized"
assert engine.propose("Not 5 but 5 pages.", language="en", state={"pages":"5"},
    slot="pages", unit="pages", addressed=True)["status"] == "no_change"
assert engine.propose("Not 5 but 10 pages.", language="en", state={"steps":"5"},
    slot="pages", unit="pages", addressed=True)["status"] == "no_context"
try:
    engine.propose("Not 5 but 10 pages.", language="en", state={"pages":"005"},
        slot="pages", unit="pages", addressed=True)
except ValueError:
    pass
else:
    raise AssertionError("Noncanonical caller state accepted")
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / PACK).parent.mkdir(parents=True)
    (root / "manifest.json").write_bytes((ROOT / "manifest.json").read_bytes())
    (root / PACK).write_bytes((ROOT / PACK).read_bytes() + b"\n")
    try:
        NumericRepair(root)
    except ValueError as exc:
        assert "SHA-256" in str(exc)
    else:
        raise AssertionError("Tampered pack accepted")

start = time.perf_counter()
for i in range(1, 11):
    for row in cases:
        result = engine.propose(row["input"], language=row["language"],
            state={row["slot"]: row["current"]}, slot=row["slot"],
            unit=row["unit"], addressed=row["addressed"], quoted=row["quoted"])
        assert result["status"] == row["expected_status"], row["id"]
    print(f"NUMERIC_REPAIR_PASS {i}/10 cases=48")
for _ in range(1000):
    result = engine.propose("Not 45 but 50 items.", language="en",
        state={"items":"45"}, slot="items", unit="items", addressed=True)
    assert result["new"] == "50"
print(f"NUMERIC_REPAIR_1000_CALLS_OK elapsed_with_10_rounds_ms={(time.perf_counter()-start)*1000:.2f}")
print("NUMERIC_REPAIR_10_ROUNDS_OK")
