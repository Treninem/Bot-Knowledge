"""T44: 36 original social cases, exact SHA, distinct meaning and retrieval."""
import hashlib
import json
import re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch

ROOT = Path(__file__).resolve().parents[1]
REL = "packs/ru/social_dialogues.json"
KINDS = ("congratulations", "support", "humor", "profanity", "conversation", "creative")
def norm(v):
    return " ".join(re.findall(r"[^\W_]+", v.casefold().replace("ё", "е")))
def main():
    raw = (ROOT / REL).read_bytes()
    pack = json.loads(raw)
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == next(x["sha256"] for x in manifest["packs"] if x["path"] == REL)
    assert len(raw) < 2 * 1024 * 1024
    rows = [x for x in pack["cases"] if x["id"].startswith("talk_t44_")]
    assert {x["id"] for x in rows} == {f"talk_t44_{i:03d}" for i in range(1, 37)}
    assert all(sum(x["kind"] == k for x in rows) == 6 for k in KINDS)
    assert len({x["id"] for x in pack["cases"]}) == len(pack["cases"])
    assert len({norm(x["input"]) for x in pack["cases"]}) == len(pack["cases"])
    assert len({norm(x["response"]) for x in pack["cases"]}) == len(pack["cases"])
    search = KnowledgeSearch()
    for x in rows:
        assert x["audiences"] == ["all_ai_bots"]
        assert all(x[k].strip() for k in ("context", "input", "response", "avoid"))
        assert not re.search(r"@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=]", str(x), re.I)
        assert any(h[0] == x["id"] for h in search.search(x["input"], audience="all_ai_bots", limit=20)), x["id"]
    print(f"T44_SOCIAL_OK rows={len(rows)} pack_bytes={len(raw)}")
if __name__ == "__main__":
    main()
