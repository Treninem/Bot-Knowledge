"""T110: verify expanded existing precision QA intents without consumer-side effects."""
import hashlib
import json
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question, validate_qa_pack

ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/conversation_precision_qa.json"

def main():
    raw = (ROOT / REL).read_bytes()
    manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
    pack = json.loads(raw)
    expected = next(x["sha256"] for x in manifest["packs"] if x["path"] == REL)
    assert hashlib.sha256(raw).hexdigest() == expected
    assert len(raw) < 2 * 1024 * 1024
    assert validate_qa_pack(pack) == 132
    assert len(pack["records"]) == 132
    assert len({r["id"] for r in pack["records"]}) == 132
    variants = [len(r["variants"]) for r in pack["records"]]
    assert variants[:42] == [5] * 42
    assert variants[42:] == [4] * 90
    assert sum(variants) == 570
    replies = [a for r in pack["records"] for a in (r["answer"], *r["variants"])]
    assert len(replies) == 702
    assert len({normalize_question(a) for a in replies}) == 702
    for r in pack["records"]:
        assert r["audiences"] == ["all_ai_bots"]
        assert r["contexts"] == ["direct", "private", "group_addressed"]
        assert r["constraints"] == {"read_only": True, "requires_direct_address": True, "no_personal_data": True}
        assert r["language"] == "ru"
        assert not set(r).intersection({"action", "execute", "auto_apply", "sanction", "ban", "mute"})
    print("T110 PASS: 132 intents, 702 total replies, 306 added versus base")

if __name__ == "__main__":
    main()
