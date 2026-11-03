"""T34: source-grounded natural ImPULS FAQ, SHA, privacy, retrieval."""
import hashlib,json,re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import validate_qa_pack,normalize_question
ROOT=Path(__file__).resolve().parents[1]
PREFIX="help_t34_"
COUNT=24
def main():
    rel="packs/ru/impuls_help_qa.json"
    raw=(ROOT/rel).read_bytes()
    manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(p["sha256"] for p in manifest["packs"] if p["path"]==rel)
    assert len(raw)<1024*1024
    pack=json.loads(raw)
    assert validate_qa_pack(pack)==len(pack["records"])
    new=[r for r in pack["records"] if r["id"].startswith(PREFIX)]
    assert len(new)==COUNT
    assert {r["id"] for r in new}=={f"{PREFIX}{i:03d}" for i in range(1,COUNT+1)}
    phrases=[normalize_question(z) for r in pack["records"] for z in (r["question"],*r["aliases"])]
    assert len(set(phrases))==len(phrases)
    assert len({r["id"] for r in pack["records"]})==len(pack["records"])
    idx=KnowledgeSearch()
    for r in new:
        assert r["audiences"]==["impuls"] and r["contexts"]==["direct","private","group_addressed"]
        assert r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True}
        assert r["language"]=="ru" and len(r["aliases"])==2 and len(r["variants"])==2
        assert r["source"].startswith("https://github.com/Treninem/Bot-Knowledge/")
        assert not re.search(r"(?:@\w+|\b\d{9,}\b|(?:api[_-]?key|access_token)\s*[:=])",str([r["question"],r["aliases"],r["answer"],r["variants"]]),re.I)
        for phrase in [r["question"],*r["aliases"]]:
            assert any(z[0]==r["id"] for z in idx.search(phrase,audience="impuls",limit=20)),(r["id"],phrase)
            assert all(z[0]!=r["id"] for z in idx.search(phrase,audience="all_ai_bots",limit=20))
    print(f"T34_IMPULS_OK questions={COUNT} answers={COUNT*3} aliases={COUNT*2}")
if __name__=="__main__":main()
