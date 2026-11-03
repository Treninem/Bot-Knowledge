"""Exact manifest-derived index count for local search regression tests.

Keeps strict equality across approved data expansions; validates every pack's
byte digest independently of the search index. No network or execution.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS = ("skills", "cases", "intents", "pairs", "triggers", "paraphrases", "scenarios")


def expected_index_count(root: Path = ROOT) -> int:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("packs"), list):
        raise AssertionError("invalid snapshot manifest")
    seen = set()
    count = 0
    for entry in manifest["packs"]:
        rel = entry.get("path", "")
        if (not isinstance(rel, str) or not rel.startswith("packs/ru/")
                or ".." in Path(rel).parts or rel in seen):
            raise AssertionError("invalid or repeated pack path")
        seen.add(rel)
        path = root / rel
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise AssertionError("unsafe pack path")
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != entry.get("sha256"):
            raise AssertionError("snapshot SHA mismatch: " + rel)
        payload = json.loads(raw)
        for key in COLLECTIONS:
            values = payload.get(key, [])
            if not isinstance(values, list):
                raise AssertionError("invalid indexed collection")
            count += sum(isinstance(x, dict) for x in values)
        catalog = payload.get("catalog")
        if isinstance(catalog, dict) and catalog.get("adapter") == "qa.v1":
            rows = payload.get(catalog.get("records", "records"), [])
            if not isinstance(rows, list):
                raise AssertionError("invalid qa.v1 indexed collection")
            count += sum(isinstance(x, dict) for x in rows)
    return count
