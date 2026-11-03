"""T66: original English contexts, SHA, privacy, normalization and search."""
from collections import Counter
from pathlib import Path
import hashlib, json, re
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/english_dialogues.json"
PREFIX="en_t66_"
EXPECTED=61
def main():
    raw=(ROOT/REL).read_bytes()
    manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    assert len(raw)<2*1024*1024
    assert hashlib.sha256(raw).hexdigest()==next(x["sha256"] for x in manifest["packs"] if x["path"]==REL)
    pack=json.loads(raw)
    rows=pack["cases"]
    added=[r for r in rows if r["id"].startswith(PREFIX)]
    assert len(added)==EXPECTED
    assert len(rows)==933
    assert len({r["id"] for r in rows})==len(rows)
    for k in ("input","response"):
        normalized=[normalize_question(r[k]) for r in rows]
        assert len(set(normalized))==len(normalized),k
    search=KnowledgeSearch()
    for r in added:
        assert r["kind"] in {"conversation","support","slang","sarcasm","context","rules","deception","creative"}
        assert r["language"]=="en" and r["audiences"]==["all_ai_bots"]
        assert all(r[k].strip() for k in ("input","response","meaning_ru","avoid"))
        assert not re.search(r"(?i)https?://|@\\w+|\\b\\d{10,}\\b",json.dumps(r,ensure_ascii=False))
        assert not any(k in r for k in ("action","sanction","auto_apply","ban","mute"))
        hits=search.search(r["input"],audience="all_ai_bots",limit=20)
        assert any(hit[0]==r["id"] for hit in hits),r["id"]
    print(f"T66_ENGLISH_OK accepted={len(added)} total={len(rows)}")
if __name__=="__main__":main()
