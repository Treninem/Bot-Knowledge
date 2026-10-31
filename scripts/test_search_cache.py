"""Offline regression: SHA-verified snapshot refresh and bounded cache lifetime.

All mutation is in a temporary synthetic fixture, never in repository packs.
No network, GitHub credentials, moderation actions or live bot updates.
"""
from __future__ import annotations

import gc
import hashlib
import json
import tempfile
import weakref
from pathlib import Path

from search_knowledge import KnowledgeSearch, ROOT

PACK = "packs/ru/short_turns.json"
PROBE = "syntheticcacheprobezz"


def verify_obsolete_snapshot_collectable() -> None:
    def cached_reference():
        index = KnowledgeSearch(ROOT)
        assert index.search("да", "all_ai_bots")
        assert index.search("да", "all_ai_bots")
        assert index._cached_search.cache_info().hits >= 1
        return weakref.ref(index)

    reference = cached_reference()
    gc.collect()
    assert reference() is None, "An old snapshot was pinned by a global cache"


def verify_sha_and_refresh() -> None:
    source_manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert any(item["path"] == PACK for item in source_manifest["packs"])
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        for item in source_manifest["packs"]:
            path = root / item["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / item["path"]).read_bytes())
        (root / "manifest.json").write_text(
            json.dumps(source_manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        old = KnowledgeSearch(root)
        assert old.search(PROBE, "all_ai_bots") == ()
        pack_path = root / PACK
        document = json.loads(pack_path.read_text(encoding="utf-8"))
        original = document["cases"][0]["input"]
        case_id = document["cases"][0]["id"]
        document["cases"][0]["input"] = PROBE  # Synthetic fixture, not published.
        payload = (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        pack_path.write_bytes(payload)

        try:
            KnowledgeSearch(root)
        except ValueError as exc:
            assert "SHA mismatch" in str(exc), str(exc)
        else:
            raise AssertionError("Modified package was accepted without a new SHA")

        updated = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        updated["knowledge_version"] = "test-only-cache-refresh"
        next(item for item in updated["packs"] if item["path"] == PACK)["sha256"] = (
            hashlib.sha256(payload).hexdigest()
        )
        (root / "manifest.json").write_text(
            json.dumps(updated, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        fresh = KnowledgeSearch(root)
        found = fresh.search(PROBE, "all_ai_bots")
        assert found and found[0][0] == case_id, found
        assert old.search(PROBE, "all_ai_bots") == ()
        assert any(row[0] == case_id for row in old.search(original, "all_ai_bots"))
        assert all(row[0] != case_id for row in fresh.search(original, "all_ai_bots"))
        assert len(old.records) == len(fresh.records)

        # High-cardinality queries must not grow a per-snapshot cache without bound.
        for i in range(600):
            fresh.search(f"syntheticcachemiss{i}", "all_ai_bots")
        assert fresh._cached_search.cache_info().currsize <= 512


def main() -> None:
    verify_obsolete_snapshot_collectable()
    verify_sha_and_refresh()
    print("SEARCH_CACHE_SHA_REFRESH_LIFECYCLE_OK: 25 packs unchanged in public data")


if __name__ == "__main__":
    main()
