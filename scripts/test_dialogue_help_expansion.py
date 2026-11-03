"""Exact-head universal dialogue qa.v1 search, aliases and scope checks."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from search_knowledge import KnowledgeSearch

def main() -> None:
    rel = "packs/ru/dialogue_help_qa.json"
    raw = (ROOT / rel).read_bytes()
    pack = json.loads(raw)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    entry = next(row for row in manifest["packs"] if row["path"] == rel)
    assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
    selected = [r for r in pack["records"] if r["id"].startswith("dlg_t7_")]
    assert len(selected) == 45, len(selected)
    assert len({r["id"] for r in selected}) == len(selected)
    index = KnowledgeSearch()
    checked = 0
    for row in selected:
        assert row["audiences"] == ["all_ai_bots"]
        assert row["contexts"] == (["group_addressed"] if row["id"].startswith("dlg_t7_group_") else ["direct", "private", "group_addressed"])
        assert len(row["aliases"]) == len(row["variants"]) == 2
        for phrase in [row["question"], *row["aliases"]]:
            hits = index.search(phrase, audience="all_ai_bots", limit=5)
            assert hits and hits[0][0] == row["id"], (row["id"], phrase, hits)
            checked += 1

    expanded = [r for r in pack["records"] if r["id"].startswith("dlg_t8_")]
    assert len(expanded) == 36, len(expanded)
    assert len({r["id"] for r in expanded}) == len(expanded)
    for row in expanded:
        assert row["audiences"] == ["all_ai_bots"]
        assert row["contexts"] == ["direct", "private", "group_addressed"]
        assert len(row["aliases"]) == len(row["variants"]) == 2
        for phrase in [row["question"], *row["aliases"]]:
            hits = index.search(phrase, audience="all_ai_bots", limit=5)
            assert hits and hits[0][0] == row["id"], (row["id"], phrase, hits)
            checked += 1
    print(f"UNIVERSAL_DIALOGUE_QA_T8_OK records={len(expanded)} checks={len(expanded) * 3}")
    newer = [r for r in pack["records"] if r["id"].startswith("dlg_t9_")]
    assert len(newer) == 29, len(newer)
    assert len({r["id"] for r in newer}) == len(newer)
    for row in newer:
        assert row["audiences"] == ["all_ai_bots"]
        assert row["contexts"] == ["direct", "private", "group_addressed"]
        assert len(row["aliases"]) == len(row["variants"]) == 2
        for phrase in [row["question"], *row["aliases"]]:
            hits = index.search(phrase, audience="all_ai_bots", limit=5)
            assert hits and hits[0][0] == row["id"], (row["id"], phrase, hits)
    print("UNIVERSAL_DIALOGUE_QA_T9_OK 29/29")
    print(f"UNIVERSAL_DIALOGUE_QA_SEARCH_OK records={len(selected)} aliases={checked - len(selected)} checks={checked}")

    latest = [r for r in pack["records"] if r["id"].startswith("dlg_t10_")]
    assert len(latest) == 42, len(latest)
    assert len({r["id"] for r in latest}) == len(latest)
    for row in latest:
        assert row["audiences"] == ["all_ai_bots"]
        assert row["contexts"] == ["direct", "private", "group_addressed"]
        assert len(row["aliases"]) == len(row["variants"]) == 2
        for phrase in [row["question"], *row["aliases"]]:
            hits = index.search(phrase, audience="all_ai_bots", limit=5)
            assert hits and hits[0][0] == row["id"], (row["id"], phrase, hits)
    print("UNIVERSAL_DIALOGUE_QA_T10_OK 42/42")

    newest = [r for r in pack["records"] if r["id"].startswith("dlg_t11_")]
    assert len(newest) == 40, len(newest)
    assert len({r["id"] for r in newest}) == len(newest)
    for row in newest:
        assert row["audiences"] == ["all_ai_bots"]
        assert row["contexts"] == ["direct", "private", "group_addressed"]
        assert len(row["aliases"]) == len(row["variants"]) == 2
        for phrase in [row["question"], *row["aliases"]]:
            hits = index.search(phrase, audience="all_ai_bots", limit=5)
            assert hits and hits[0][0] == row["id"], (row["id"], phrase, hits)
    print("UNIVERSAL_DIALOGUE_QA_T11_OK 40/40")

    # T12: new scoped canonical intents and paraphrased retrieval. Do not widen group-only references.
    t12 = [r for r in pack["records"] if r["id"].startswith("dlg_t12_")]
    assert len(t12) == 30, len(t12)
    assert len({r["id"] for r in t12}) == len(t12)
    expected_groups = ["dlg_t12_013","dlg_t12_014","dlg_t12_015","dlg_t12_016","dlg_t12_017","dlg_t12_018","dlg_t12_019","dlg_t12_020"]
    assert {r["id"] for r in t12 if r["contexts"] == ["group_addressed"]} == set(expected_groups)
    for row in t12:
        assert row["audiences"] == ["all_ai_bots"]
        assert len(row["aliases"]) == len(row["variants"]) == 2
        for query in [row["question"], *row["aliases"]]:
            hits = index.search(query, audience="all_ai_bots", limit=5)
            assert hits and hits[0][0] == row["id"], (row["id"], query, hits)
    print("UNIVERSAL_DIALOGUE_QA_T12_OK 30/30 searches=90")


    # T13: independently authored, scoped question and alias retrieval.
    t13 = [r for r in pack["records"] if r["id"].startswith("dlg_t13_")]
    assert len(t13) == 32, len(t13)
    assert len({r["id"] for r in t13}) == len(t13)
    expected_groups = {"dlg_t13_026", "dlg_t13_027", "dlg_t13_028", "dlg_t13_029", "dlg_t13_030", "dlg_t13_031", "dlg_t13_032"}
    assert {r["id"] for r in t13 if r["contexts"] == ["group_addressed"]} == expected_groups
    for row in t13:
        assert row["audiences"] == ["all_ai_bots"]
        assert len(row["aliases"]) == len(row["variants"]) == 2
        for phrase in [row["question"], *row["aliases"]]:
            hits = index.search(phrase, audience="all_ai_bots", limit=5)
            assert hits and hits[0][0] == row["id"], (row["id"], phrase, hits)
    print("UNIVERSAL_DIALOGUE_QA_T13_OK 32/32 searches=96")

    # Prevent accidental duplicate canonical questions and alias collisions,
    # including case, punctuation, yo/e and cosmetic-emoji differences.
    from copy import deepcopy
    from validate_qa_v1 import normalize_question, validate_qa_pack
    assert normalize_question("  Ёж, привет! 😀  ") == normalize_question("еж привет")
    assert validate_qa_pack(pack) == len(pack["records"])
    cases = []
    second_record = deepcopy(pack)
    second_record["records"][-1]["aliases"].append(pack["records"][0]["question"].upper() + " 😃")
    cases.append(second_record)
    same_record = deepcopy(pack)
    same_record["records"][0]["aliases"][0] = pack["records"][0]["question"] + " 🙂"
    cases.append(same_record)
    for invalid in cases:
        try:
            validate_qa_pack(invalid)
        except ValueError as exc:
            assert str(exc) == "duplicate_normalized_question_or_alias", str(exc)
        else:
            raise AssertionError("duplicate alias was not rejected")
    print("QA_NORMALIZED_QUERY_DEDUP_OK 2_negative + current_pack")

if __name__ == "__main__":
    main()
