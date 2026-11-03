"""T38: source-grounded read-only ImPULS advice, privacy, hashes and lookup."""
import hashlib,json,re
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack,normalize_question
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]

def main():
    rel="packs/ru/impuls_help_qa.json"
    raw=(ROOT/rel).read_bytes()
    pack=json.loads(raw)
    manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(x["sha256"] for x in manifest["packs"] if x["path"]==rel)
    assert len(raw)<2*1024*1024
    assert validate_qa_pack(pack)==len(pack["records"])
    rows=[r for r in pack["records"] if r["id"].startswith("help_t38_")]
    assert len(rows)==24
    assert {r["id"] for r in rows}=={f"help_t38_{n:03d}" for n in range(1,25)}
    phrases=[normalize_question(p) for r in pack["records"] for p in [r["question"],*r["aliases"]]]
    assert len(set(phrases))==len(phrases)
    search=KnowledgeSearch()
    for r in rows:
        assert r["audiences"]==["impuls"]
        assert r["contexts"]==["direct","private","group_addressed"]
        assert r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True}
        assert len(r["variants"])==2 and len(r["aliases"])==2
        assert r["source"].startswith("https://github.com/Treninem/Bot-Knowledge/")
        assert not re.search(r"@\w+|\b\d{9,}\b|(?:access_token|api[_-]?key)\s*[:=]",str(r),re.I)
        for q in [r["question"],*r["aliases"]]:
            assert any(h[0]==r["id"] for h in search.search(q,audience="impuls",limit=20)),(r["id"],q)
            assert all(h[0]!=r["id"] for h in search.search(q,audience="all_ai_bots",limit=20)),(r["id"],q)
    print("T38_IMPULS_NATURAL_OK",len(rows),"answers",len(rows)*3,"aliases",len(rows)*2)
if __name__=="__main__": main()
