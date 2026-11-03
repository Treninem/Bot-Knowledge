"""Offline synthetic checks for the draft builder."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

from build_skill_draft import build
from test_preflight_skill_manifest import _fixture


def main() -> None:
    for index in range(10):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate, skill, _, _, baseline, _, _, _, _ = _fixture(root, index)
            output = root / "draft"
            build(baseline, candidate, skill, output, "2026.10.31.1", "2026.10.31.1")
            data = json.loads((output / "packs/ru/skills.json").read_text(encoding="utf-8"))
            assert data["skills"][-1]["id"] == f"synthetic_context_rule_{index}"
            assert len(data["skills"]) == 2
            try:
                build(baseline, candidate, skill, output, "2026.10.31.2", "2026.10.31.2")
            except ValueError:
                pass
            else:
                raise AssertionError("existing output overwritten")
            assert len(json.loads((output / "packs/ru/skills.json").read_text(encoding="utf-8"))["skills"]) == 2
            print(f"DRAFT_ROUND_PASS {index + 1}/10")
    print("DRAFT_PASS 10/10")


if __name__ == "__main__":
    main()
