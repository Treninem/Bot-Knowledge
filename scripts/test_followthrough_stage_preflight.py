"""Fail-closed pinned-stage preflight at the current main catalog; no live actions."""
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.colloquial_t305 import ROOT
from scripts.followthrough_stage_catalog import (
    FollowthroughStageCatalog, SOURCE, STAGES, _PINNED_STAGE_BLOBS,
)


class StagePinPreflightTests(unittest.TestCase):
    def test_all_stages_pinned(self):
        self.assertEqual(set(STAGES), set(STAGES) & set(_PINNED_STAGE_BLOBS))
        self.assertEqual(len(STAGES), len(set(STAGES)))

    def test_mutation_detected_before_selectors_are_constructed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for rel in ("manifest.json", SOURCE, *STAGES):
                target = root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, target)
            for rel in (STAGES[0], STAGES[len(STAGES)//2], STAGES[-1]):
                target = root / rel
                original = target.read_bytes()
                target.write_bytes(original + b" ")
                with patch(
                    "scripts.followthrough_stage_catalog.StagedContextSelector",
                    side_effect=AssertionError("selector must not be constructed after tampering"),
                ):
                    with self.assertRaisesRegex(ValueError, "stage blob mismatch"):
                        FollowthroughStageCatalog(root)
                target.write_bytes(original)

    def test_missing_pin_rejected_before_selector(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "packs/ru").mkdir(parents=True)
            shutil.copyfile(ROOT / "manifest.json", root / "manifest.json")
            shutil.copyfile(ROOT / SOURCE, root / SOURCE)
            with patch.dict(_PINNED_STAGE_BLOBS, {}, clear=True):
                with patch(
                    "scripts.followthrough_stage_catalog.StagedContextSelector",
                    side_effect=AssertionError("selector must not be constructed without pin"),
                ):
                    with self.assertRaisesRegex(ValueError, "missing immutable pin"):
                        FollowthroughStageCatalog(root)


if __name__ == "__main__":
    unittest.main()
