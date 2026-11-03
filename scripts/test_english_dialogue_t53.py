"""T53: 36 distinct EN cases (dark_humor, profanity, context) plus exact SHA."""
import hashlib, json, re
from collections import Counter
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/english_dialogues.json"
KINDS = ("dark_humor", "profanity", "context")
def norm(s):
    return " ".join(re.findall(r"[^\W_]+", s.casefold()))
def main():
    raw = (ROOT / REL).read_bytes()
    pack = json.loads(raw)
    m = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    digest = next(x["sha256"] for x in m["packs"] if x["path"] == REL)
    assert hashlib.sha256(raw).hexdigest() == digest
    assert len(raw) < 2 * 1024 * 1024
    rows = [x for x in pack["cases"] if x["id"].startswith("en_t53_")]
    assert len(rows) == 36 and len(pack["cases"]) >= 558
    assert Counter(x["kind"] for x in rows) == dict.fromkeys(KINDS, 12)
    assert len({x["id"] for x in pack["cases"]}) == len(pack["cases"])
    for f in ("input", "response"):
        values = [norm(x[f]) for x in pack["cases"]]
        assert len(values) == len(set(values)), f
    search = KnowledgeSearch()
    for x in rows:
        assert x["language"] == "en" and x["audiences"] == ["all_ai_bots"]
        assert all(x[k].strip() for k in ("input", "response", "meaning_ru", "avoid"))
        assert not re.search(r"@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=]", str(x), re.I)
        assert any(h[0] == x["id"] for h in search.search(x["input"], audience="all_ai_bots", limit=20)), x["id"]
    print(f"T53_ENGLISH_OK added={len(rows)} total={len(pack['cases'])}")
if __name__ == "__main__": main()
