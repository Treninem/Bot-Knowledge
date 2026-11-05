"""T124: preserved structured intents, per-intent contextual diversity, SHA and safety.

Run offline from the repository root:
    python -m scripts.test_structured_t124
No network, tokens, sanctions or consumer writes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question

ROOT = Path(__file__).resolve().parents[1]
PATH = "packs/ru/structured_information_qa.json"
SCOPE = {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
GROUPS = {"struct_t86_": 39, "struct_t88_": 25, "struct_t90_": 25, "struct_t93_": 25}

def main() -> None:
    raw = (ROOT / PATH).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    expected = next(item["sha256"] for item in manifest["packs"] if item["path"] == PATH)
    assert hashlib.sha256(raw).hexdigest() == expected, "manifest SHA must match actual bytes"
    assert len(raw) < 2 * 1024 * 1024, "per-pack consumer budget"
    data = json.loads(raw)
    assert validate_qa_pack(data) == 114
    assert data["catalog"]["purpose"] == "information_explanation"
    assert data["pack_version"] == manifest["knowledge_version"]
    assert len(data["records"]) == sum(GROUPS.values())
    ids = [row["id"] for row in data["records"]]
    assert len(set(ids)) == len(ids)
    for prefix, count in GROUPS.items():
        assert [v for v in ids if v.startswith(prefix)] == [
            f"{prefix}{i:03d}" for i in range(1, count + 1)
        ]
    normalized = set()
    for row in data["records"]:
        assert len(row["variants"]) == 8, row["id"]
        assert row["audiences"] == ["all_ai_bots"]
        assert row["contexts"] == ["direct", "private", "group_addressed"]
        assert row["language"] == "ru"
        assert row["constraints"] == SCOPE
        assert len(row["aliases"]) == 2
        assert not set(row).intersection({"action", "execute", "sanction", "mute", "ban"})
        for value in (row["answer"], *row["variants"]):
            token = normalize_question(value)
            assert token and token not in normalized, ("duplicate_reply", row["id"])
            normalized.add(token)
    assert len(normalized) == 1026
    print("T124 PASS: 114 preserved intents, +228 new contextual replies, 1026 unique, SHA/scope OK")

if __name__ == "__main__":
    main()
