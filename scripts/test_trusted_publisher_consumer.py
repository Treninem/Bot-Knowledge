"""Offline reviewed candidate -> SHA-pinned QA -> ImPULS catalog check.

Run with --impuls-root pointing to a local ImPULS checkout. No network or token.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import patch

try:
    from scripts import trusted_publish_qa as publisher
    from scripts.test_trusted_publisher_scope import candidate, PATH, ROOT
except ModuleNotFoundError:
    import trusted_publish_qa as publisher
    from test_trusted_publisher_scope import candidate, PATH, ROOT


def main(impuls_root: Path) -> None:
    pack_raw = (ROOT / PATH).read_bytes()
    manifest_raw = (ROOT / "manifest.json").read_bytes()
    def local_contents(path, *, token, ref):
        return {"sha": "local-fixture"}, pack_raw if path == PATH else manifest_raw
    with patch.object(publisher, "_contents", side_effect=local_contents):
        path, pack_text, manifest_text, _ = publisher.prepare_changes(
            candidate(), token="unused", base="main")
    pack = json.loads(pack_text)
    manifest = json.loads(manifest_text)
    entry = next(x for x in manifest["packs"] if x["path"] == path)
    assert hashlib.sha256(pack_text.encode()).hexdigest() == entry["sha256"]
    sys.path.insert(0, str(impuls_root.resolve()))
    from src.bot.knowledge.catalog import build_catalog
    from src.bot.knowledge.search import build_search_index, ranked_search
    catalog = build_catalog({path: pack}, [entry], manifest["knowledge_version"])
    section = next(x for x in catalog.sections if x.path == path)
    assert section.status == "supported", (section.status, section.reason)
    index = build_search_index(catalog)
    result = ranked_search(catalog, index, candidate()["record"]["question"],
                           audience="impuls", context="direct")
    assert not result.ambiguous and result.hits
    assert result.hits[0].candidate.record_id == "reviewed_scope_probe"
    assert not ranked_search(catalog, index, candidate()["record"]["question"],
                             audience="all_ai_bots", context="direct").hits
    print("reviewed candidate -> pack and manifest SHA -> ImPULS catalog and scope: OK")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--impuls-root", required=True, type=Path)
    args = parser.parse_args()
    main(args.impuls_root)
