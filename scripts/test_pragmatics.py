"""Verify 48 distinct ambiguity pairs, cue abstention and safe audience boundaries.

These are data and deterministic matcher tests, NOT real-language model accuracy.
"""
from __future__ import annotations
import hashlib
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from interpret_pragmatics import interpret, load, norm

def main() -> None:
    data = load()
    pairs = data["pairs"]
    assert len(pairs) == 48
    assert len({p["id"] for p in pairs}) == 48
    assert len({norm(p["expression"]) for p in pairs}) == 48
    assert Counter(p["category"] for p in pairs) == {c: 4 for c in data["categories"]}
    assert Counter(p["language"] for p in pairs) == {"ru":24,"en":24}
    all_responses = []
    for pair in pairs:
        assert len(pair["readings"]) == 2
        assert pair["audiences"] == (["chat_moderators"] if pair["category"]=="moderation_context" else ["all_ai_bots"])
        assert interpret(data, pair["expression"])["status"] == ("unrecognized" if pair["category"]=="moderation_context" else "needs_context")
        for idx, rd in enumerate(pair["readings"]):
            assert len(rd["cues"]) == 2
            assert len(set(norm(c) for c in rd["cues"])) == 2
            assert 4 <= len(rd["meaning"]) <= 250
            assert rd["decision"] in {"respond","support","clarify","human_review"}
            all_responses.append(rd["suggested_response"])
            res = interpret(data, pair["expression"], rd["context"],
                            "chat_moderators" if pair["category"]=="moderation_context" else "all_ai_bots")
            assert res["status"] == "example_match" and res["tag"] == rd["tag"], (pair["id"],res)
            assert res["response"] == rd["suggested_response"]
            limited = interpret(data, pair["expression"], rd["cues"][0],
                                "chat_moderators" if pair["category"]=="moderation_context" else "all_ai_bots")
            assert limited["status"] == "needs_context"
        # Conflicting cues cannot produce overconfident interpretations.
        combo = " ".join([*pair["readings"][0]["cues"], *pair["readings"][1]["cues"]])
        assert interpret(data, pair["expression"], combo, "chat_moderators")["status"]=="needs_context"
    assert len(all_responses)==96
    assert len(set(norm(x) for x in all_responses))==96
    assert interpret(data,"unseen novel expression","some context")["status"]=="unrecognized"
    try:
        interpret(data,"hi","",audience="root")
        raise AssertionError("Unauthorized audience accepted")
    except ValueError:
        pass
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)
        (p/"packs/ru").mkdir(parents=True)
        (p/"manifest.json").write_bytes((ROOT/"manifest.json").read_bytes())
        original=(ROOT/"packs/ru/pragmatic_contrasts.json").read_bytes()
        (p/"packs/ru/pragmatic_contrasts.json").write_bytes(original+b" ")
        try:
            load(p)
            raise AssertionError("Invalid checksum accepted")
        except ValueError as e:
            assert "SHA" in str(e)
    for run in range(1,11):
        assert all(len(p["readings"])==2 for p in pairs)
        print(f"PRAGMATICS_PASS {run}/10 pairs=48 readings=96")
    print("PRAGMATICS_10_ROUNDS_OK")

if __name__=="__main__":
    main()
