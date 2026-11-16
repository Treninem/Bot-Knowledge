"""Run legacy, SHA-pinned followthrough tests against their exact historical source.

The published qa.v1 pack is allowed to evolve. Historical staged pools remain
unregistered and tied to the original 246-reply source: never weaken the SHA
checks or accept a changed source as that original release.

Only the named legacy test module is redirected to an isolated local fixture.
Normal manifest validation and tests for the current published pack run against
the real checkout, independently of this fixture.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "packs/ru/conversation_followthrough_qa.json"
HISTORICAL_VERSION = "2026.11.04.023"
HISTORICAL_SHA = "0862daf244df650bfd85217df3bedb9f2373a6e63dbabfa8d0c831a6fb289ff7"
HISTORICAL_BLOB = "707fcaa6440d398a730840362602d4532ab92036"

ALLOWED_MODULES = {
    "scripts.test_followthrough_stage_catalog",
    "scripts.test_recent_followthrough_selector",
    *(f"scripts.test_followthrough_t{n}" for n in range(384, 457)),
}


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def source_bytes() -> bytes:
    """Reconstruct and verify the actual byte-identical historical release."""
    live_raw = (ROOT / SOURCE).read_bytes()
    actual_manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
    current = [p for p in actual_manifest["packs"] if p["path"] == SOURCE]
    if len(current) != 1 or hashlib.sha256(live_raw).hexdigest() != current[0]["sha256"]:
        raise ValueError("current published pack is not manifest-verified")
    live = json.loads(live_raw)
    rows = live.get("records", [])
    if len(rows) != 82:
        raise ValueError("canonical inventory changed; do not infer historical contents")
    if len({row["id"] for row in rows}) != 82:
        raise ValueError("canonical IDs were changed")
    # The original registered release consisted of each record's answer and
    # its first two variants. Nothing else may be dropped or rewritten.
    live["pack_version"] = HISTORICAL_VERSION
    for row in rows:
        variants = row.get("variants")
        if not isinstance(variants, list) or len(variants) < 2:
            raise ValueError("historical answer variants missing")
        row["variants"] = variants[:2]
    raw = (json.dumps(live, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if hashlib.sha256(raw).hexdigest() != HISTORICAL_SHA or git_blob(raw) != HISTORICAL_BLOB:
        raise ValueError("historical source content no longer reconstructs exactly")
    return raw


def fixture_root() -> Path:
    raw = source_bytes()
    # A GitHub job's repeated test steps reuse one local fixture. The current
    # source SHA is part of the name so source changes invalidate the fixture.
    key = hashlib.sha256(
        (str(ROOT.resolve()) + hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest()).encode()
    ).hexdigest()[:20]
    target = Path(tempfile.gettempdir()) / ("bk-followthrough-pinned-" + key)
    pinned = target / SOURCE
    if target.is_dir():
        if pinned.is_file() and hashlib.sha256(pinned.read_bytes()).hexdigest() == HISTORICAL_SHA:
            return target
        raise ValueError("historical fixture directory exists but its source is invalid")

    scratch = Path(tempfile.mkdtemp(prefix="bk-followthrough-build-"))
    try:
        shutil.copytree(ROOT / "packs" / "ru", scratch / "packs" / "ru")
        shutil.copytree(ROOT / "staging" / "ru", scratch / "staging" / "ru")
        dest = scratch / SOURCE
        dest.write_bytes(raw)
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        record = [p for p in manifest["packs"] if p["path"] == SOURCE]
        if len(record) != 1:
            raise ValueError("unexpected historical manifest entries")
        record[0]["sha256"] = HISTORICAL_SHA
        (scratch / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        if hashlib.sha256(dest.read_bytes()).hexdigest() != HISTORICAL_SHA:
            raise ValueError("fixture source changed during construction")
        scratch.rename(target)
        return target
    finally:
        if scratch.exists():
            shutil.rmtree(scratch)


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in ALLOWED_MODULES:
        print("usage: python -m scripts.run_historical_followthrough_test scripts.test_followthrough_t384", file=sys.stderr)
        return 2
    module_name = sys.argv[1]
    pinned_root = fixture_root()
    # Most older tests import ROOT from colloquial_t305; two tests declare
    # their own ROOT. Patch only the loaded test process, never a consumer.
    root_module = importlib.import_module("scripts.colloquial_t305")
    root_module.ROOT = pinned_root
    module = importlib.import_module(module_name)
    if hasattr(module, "ROOT"):
        module.ROOT = pinned_root
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
