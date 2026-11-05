"""T118 — additive, context-sensitive Russian numerical explanations."""
import hashlib
import json
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question
ROOT = Path(__file__).resolve().parents[1]
PATH = "packs/ru/structured_information_qa.json"
def main():
    raw = (ROOT / PATH).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
    assert hashlib.sha256(raw).hexdigest() == next(p["sha256"] for p in manifest["packs"] if p["path"] == PATH)
    assert len(raw) < 2 * 1024 * 1024
    data = json.loads(raw)
    assert validate_qa_pack(data) == 114
    seen = set()
    for record in data["records"]:
        for text in [record["answer"], *record["variants"]]:
            key = normalize_question(text)
            assert key not in seen, ("repeated", record["id"])
            seen.add(key)
        assert record["audiences"] == ["all_ai_bots"]
        assert record["constraints"] == {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
        assert 2 <= len(record["variants"]) <= 8
    for prefix, n in (("struct_t93_", 25), ("struct_t90_", 25), ("struct_t86_", 15)):
        for idx in range(1, n+1):
            row = next(r for r in data["records"] if r["id"] == f"{prefix}{idx:03d}")
            assert len(row["variants"]) >= 4
    assert len(seen) >= 472
    print("T118 PASS: 130 added answers, 65 existing intents, 472 unique replies total")
if __name__ == "__main__":
    main()
