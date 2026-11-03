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
    print(f"UNIVERSAL_DIALOGUE_QA_SEARCH_OK records={len(selected)} aliases={checked - len(selected)} checks={checked}")

if __name__ == "__main__":
    main()
