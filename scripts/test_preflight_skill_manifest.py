"""Ten independent synthetic pre-publication fixture rounds; no network or repository writes."""
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
from pathlib import Path

from preflight_skill_manifest import validate_bundle


def _write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _fixture(root: Path, index: int):
    candidate = {
        "candidate_id": f"synthetic_context_rule_{index}",
        "statement": "Если смысл цитаты неясен, запросить контекст и не назначать санкцию автоматически.",
        "when": ["человек цитирует фразу для обсуждения"],
        "avoid": ["цитата используется для прямой травли"],
        "audiences": ["chat_moderators"],
        "origin": "synthetic",
        "reviewed": True,
    }
    skill = {
        "id": candidate["candidate_id"],
        "kind": "moderation_language",
        "when": copy.deepcopy(candidate["when"]),
        "avoid": copy.deepcopy(candidate["avoid"]),
        "examples": ["Сначала уточните контекст цитаты; решение остаётся за администрацией."],
        "audiences": copy.deepcopy(candidate["audiences"]),
    }
    pack = {
        "schema_version": 1,
        "language": "ru",
        "usage_policy": {
            "shared_between_bots": True,
            "user_data_allowed": False,
            "automatic_sanctions_allowed": False,
            "initiative_requires_local_authorization": True,
            "scope_filter_required": True,
        },
        "skills": [skill],
    }
    candidate_path = root / "candidate.json"
    reviewed_skill_path = root / "reviewed_skill.json"
    pack_path = root / "packs/ru/skills.json"
    manifest_path = root / "manifest.json"
    _write(candidate_path, candidate)
    _write(reviewed_skill_path, skill)
    _write(pack_path, pack)
    manifest = {
        "schema_version": 1,
        "knowledge_version": "2026.10.31.1",
        "language": "ru",
        "packs": [{"path": "packs/ru/skills.json", "sha256": hashlib.sha256(pack_path.read_bytes()).hexdigest()}],
    }
    _write(manifest_path, manifest)
    return candidate_path, reviewed_skill_path, pack_path, manifest_path, candidate, pack, manifest


def _snapshot(root: Path) -> dict[str, bytes]:
    return {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}


def _rejected(root: Path, candidate_path: Path, reviewed_skill_path: Path, manifest_path: Path) -> None:
    before = _snapshot(root)
    try:
        validate_bundle(root, candidate_path, reviewed_skill_path, manifest_path)
    except ValueError:
        pass
    else:
        raise AssertionError("unsafe bundle accepted")
    assert _snapshot(root) == before, "preflight wrote to fixture"


def main() -> None:
    work = Path(__file__).resolve().parents[1] / "work" / "preflight_skill_manifest"
    work.mkdir(parents=True, exist_ok=True)
    try:
        for index in range(10):
            with tempfile.TemporaryDirectory(prefix=f"round_{index}_", dir=work) as folder:
                root = Path(folder)
                candidate_path, reviewed_skill_path, pack_path, manifest_path, candidate, pack, manifest = _fixture(root, index)
                safe_candidate = copy.deepcopy(candidate)
                safe_pack = copy.deepcopy(pack)
                safe_manifest = copy.deepcopy(manifest)
                before = _snapshot(root)
                validate_bundle(root, candidate_path, reviewed_skill_path, manifest_path)
                assert _snapshot(root) == before, "preflight wrote to fixture"

                if index == 0:
                    candidate["statement"] += " https://example.invalid/private"
                    _write(candidate_path, candidate)
                elif index == 1:
                    pack["skills"][0]["examples"][0] += " @private_user_123"
                    _write(pack_path, pack)
                    manifest["packs"][0]["sha256"] = hashlib.sha256(pack_path.read_bytes()).hexdigest()
                    _write(manifest_path, manifest)
                elif index == 2:
                    candidate["raw_message"] = "synthetic private text"
                    _write(candidate_path, candidate)
                elif index == 3:
                    candidate["reviewed"] = False
                    _write(candidate_path, candidate)
                elif index == 4:
                    manifest["packs"][0]["sha256"] = "0" * 64
                    _write(manifest_path, manifest)
                elif index == 5:
                    manifest["packs"][0]["path"] = "packs/ru/../private.json"
                    _write(manifest_path, manifest)
                elif index == 6:
                    manifest["packs"].append(copy.deepcopy(manifest["packs"][0]))
                    _write(manifest_path, manifest)
                elif index == 7:
                    pack["skills"][0]["auto_apply"] = True
                    _write(pack_path, pack)
                    manifest["packs"][0]["sha256"] = hashlib.sha256(pack_path.read_bytes()).hexdigest()
                    _write(manifest_path, manifest)
                elif index == 8:
                    pack["skills"][0]["when"] = ["другое безопасное условие"]
                    _write(pack_path, pack)
                    manifest["packs"][0]["sha256"] = hashlib.sha256(pack_path.read_bytes()).hexdigest()
                    _write(manifest_path, manifest)
                else:
                    candidate["statement"] += " 123e4567-e89b-12d3-a456-426614174000"
                    _write(candidate_path, candidate)
                _rejected(root, candidate_path, reviewed_skill_path, manifest_path)

                if index == 0:
                    # A changed response with a valid new SHA must not inherit the original review.
                    _write(candidate_path, safe_candidate)
                    pack["skills"][0]["examples"] = ["Совершенно иная реакция, не прошедшая обзор."]
                    _write(pack_path, pack)
                    manifest["packs"][0]["sha256"] = hashlib.sha256(pack_path.read_bytes()).hexdigest()
                    _write(manifest_path, manifest)
                    _rejected(root, candidate_path, reviewed_skill_path, manifest_path)
                if index == 1:
                    _write(pack_path, safe_pack)
                    _write(manifest_path, safe_manifest)
                    duplicate = manifest_path.read_text(encoding="utf-8").replace(
                        '"packs": [', '"packs": [], "packs": [', 1,
                    )
                    manifest_path.write_text(duplicate, encoding="utf-8")
                    _rejected(root, candidate_path, reviewed_skill_path, manifest_path)
            print(f"PREFLIGHT_SKILL_MANIFEST_ROUND_PASS {index + 1}/10", flush=True)
    finally:
        work.rmdir()
    print("PREFLIGHT_SKILL_MANIFEST_PASS 10/10")


if __name__ == "__main__":
    main()
