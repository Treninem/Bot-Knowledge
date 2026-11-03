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

if __name__ == "__main__":
    main()
