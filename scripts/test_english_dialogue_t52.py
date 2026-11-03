"""T52: English contextual examples, exact pack SHA, privacy and scoped lookup."""
import hashlib, json, re
from collections import Counter
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/english_dialogues.json"
KINDS = ("conversation", "slang", "sarcasm", "rules", "deception", "support", "creative")
def norm(s):
    return " ".join(re.findall(r"[^\\W_]+", s.casefold()))
def main():
    raw = (ROOT / REL).read_bytes()
    pack = json.loads(raw)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    digest = next(p["sha256"] for p in manifest["packs"] if p["path"] == REL)
    assert hashlib.sha256(raw).hexdigest() == digest
    assert len(raw) < 2 * 1024 * 1024
    rows = [r for r in pack["cases"] if r["id"].startswith("en_t52_")]
    assert len(rows) == 56 and len(pack["cases"]) >= 522
    assert Counter(r["kind"] for r in rows) == dict.fromkeys(KINDS, 8)
    assert len({r["id"] for r in pack["cases"]}) == len(pack["cases"])
    for f in ("input", "response"):
        keys = [norm(r[f]) for r in pack["cases"]]
        assert len(keys) == len(set(keys)), f
    search = KnowledgeSearch()
    for r in rows:
        assert r["language"] == "en" and r["audiences"] == ["all_ai_bots"]
        assert all(r[f].strip() for f in ("input", "response", "meaning_ru", "avoid"))
        assert not re.search(r"@\\w+|\\b\\d{9,}\\b|(?:api[_-]?key|access_token)\\s*[:=]", str(r), re.I)
        assert any(hit[0] == r["id"] for hit in search.search(r["input"], audience="all_ai_bots", limit=20)), r["id"]
    print(f"T52_ENGLISH_OK added={len(rows)} total={len(pack['cases'])}")
if __name__ == "__main__": main()
