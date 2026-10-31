"""Build an offline, reviewable skills pack draft; never publish it."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

from preflight_skill_manifest import SKILL_PATH, _read_json, _safe_pack_path, validate_bundle


def _version(value: str) -> tuple[int, ...]:
    if not re.fullmatch(r"[0-9]{4}\.[0-9]{1,2}\.[0-9]{1,2}\.[0-9]+", value):
        raise ValueError("invalid version")
    return tuple(map(int, value.split(".")))


def build(root: Path, candidate: Path, reviewed_skill: Path, output: Path,
          pack_version: str, knowledge_version: str) -> None:
    if output.exists():
        raise ValueError("output already exists")
    root = root.resolve(strict=True)
    output = output.resolve()
    if output == root or root in output.parents:
        raise ValueError("output must be outside baseline")
    base_manifest = _read_json(root / "manifest.json", max_bytes=128 * 1024)
    base_pack = _read_json(root / SKILL_PATH, max_bytes=128 * 1024)
    reviewed = _read_json(reviewed_skill, max_bytes=16 * 1024)
    candidate_data = _read_json(candidate, max_bytes=16 * 1024)
    if _version(pack_version) <= _version(base_pack["pack_version"]):
        raise ValueError("pack version must increase")
    if _version(knowledge_version) <= _version(base_manifest["knowledge_version"]):
        raise ValueError("knowledge version must increase")
    if (not isinstance(reviewed, dict) or not isinstance(candidate_data, dict)
            or reviewed.get("id") != candidate_data.get("candidate_id")):
        raise ValueError("reviewed skill identity mismatch")
    if any(row.get("id") == reviewed["id"] for row in base_pack["skills"]):
        raise ValueError("skill already exists")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="skill-draft-", dir=output.parent) as temporary:
        draft = Path(temporary)
        for entry in base_manifest["packs"]:
            relative = entry["path"]
            if _safe_pack_path(relative) != relative:
                raise ValueError("unsafe baseline pack path")
            source = root / relative
            if source.is_symlink() or not source.is_file() or not source.resolve().is_relative_to(root):
                raise ValueError("unsafe baseline pack")
            if hashlib.sha256(source.read_bytes()).hexdigest() != entry["sha256"]:
                raise ValueError("baseline pack SHA mismatch")
            target = draft / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        base_pack["pack_version"] = pack_version
        base_pack["skills"].append(reviewed)
        (draft / SKILL_PATH).write_text(json.dumps(base_pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest = dict(base_manifest)
        manifest["knowledge_version"] = knowledge_version
        manifest["packs"] = [dict(entry) for entry in base_manifest["packs"]]
        for entry in manifest["packs"]:
            if entry["path"] == SKILL_PATH:
                entry["sha256"] = hashlib.sha256((draft / SKILL_PATH).read_bytes()).hexdigest()
        (draft / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        validate_bundle(draft, candidate, reviewed_skill, draft / "manifest.json", root, root / "manifest.json")
        draft.rename(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-root", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--reviewed-skill", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pack-version", required=True)
    parser.add_argument("--knowledge-version", required=True)
    args = parser.parse_args()
    try:
        build(args.baseline_root, args.candidate, args.reviewed_skill, args.output,
              args.pack_version, args.knowledge_version)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"DRAFT_REJECTED: {exc}")
        return 1
    print("DRAFT_OK; human privacy review and PR required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
