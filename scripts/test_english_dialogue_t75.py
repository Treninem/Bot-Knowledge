"""T75: original EN contextual replies, exact manifest SHA and scoped retrieval."""
import hashlib
import json
import re
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question
from scripts.search_knowledge import KnowledgeSearch
ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/english_dialogues.json"
PREFIX = "en_t75_"
EXPECTED = 60
def main():
    raw = (ROOT / REL).read_bytes()
    assert len(raw) < 2*1024*1024
    manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
    assert hashlib.sha256(raw).hexdigest() == next(x["sha256"] for x in manifest["packs"] if x["path"] == REL)
    cases = json.loads(raw)["cases"]
    assert len(cases) >= 1030 + EXPECTED
    new = [r for r in cases if r["id"].startswith(PREFIX)]
    assert len(new) == EXPECTED
    assert len({r["id"] for r in cases}) == len(cases)
    for key in ("input", "response"):
        norm = [normalize_question(r[key]) for r in cases]
        assert len(norm) == len(set(norm)), key
    lookup = KnowledgeSearch()
    for r in new:
        assert r["audiences"] == ["all_ai_bots"] and r["language"] == "en"
        assert r["kind"] in {"conversation","context","support","slang","sarcasm","rules","deception","creative"}
        assert all(isinstance(r[k],str) and r[k].strip() for k in ("input","response","meaning_ru","avoid"))
        assert not re.search(r"https?://|@[A-Za-z0-9_]+|\b\d{10,}\b|token\s*[:=]|password\s*[:=]",json.dumps(r,ensure_ascii=False),re.I)
        assert not set(r) & {"action","sanction","auto_apply","execute","ban","mute"}
        hits = lookup.search(r["input"],audience="all_ai_bots",limit=20)
        assert any(hit[0] == r["id"] for hit in hits),r["id"]
    print(f"T75 EN PASS: {EXPECTED} new, total {len(cases)}")
if __name__ == "__main__":
    main()
