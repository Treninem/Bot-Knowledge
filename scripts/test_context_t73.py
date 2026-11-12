"""T73: 30 synthetic context boundaries, no executions or sanctions."""
from collections import Counter
import hashlib, json, re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/context_cases.json"
def norm(s):return re.sub(r"[^a-zа-я0-9]+"," ",s.casefold().replace("ё","е")).strip()
def main():
    raw=(ROOT/REL).read_bytes()
    manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    expected=next(x["sha256"] for x in manifest["packs"] if x["path"]==REL)
    assert hashlib.sha256(raw).hexdigest()==expected
    data=json.loads(raw)
    assert data["pack_version"]=="2026.11.04.007"
    assert data["usage_policy"]["automatic_sanctions_allowed"] is False
    rows=data["cases"];added=[x for x in rows if x["id"].startswith("t73_")]
    assert len(rows)==170 and len(added)==30
    assert len(set(x["id"] for x in rows))==170
    assert len(set(norm(x["input"]) for x in rows))==170
    assert Counter(x["category"] for x in added)=={k:3 for k in {x["category"] for x in rows}}
    assert Counter(x["category"] for x in rows)=={k:17 for k in {x["category"] for x in rows}}
    for item in added:
        assert set(item)=={"id","category","audiences","context","input","decision","expected_behavior","forbidden_behavior"}
        assert item["expected_behavior"].strip()!=item["forbidden_behavior"].strip()
        assert not any(x in item for x in ("action","execute","sanction","auto_apply"))
        assert item["audiences"]==(["chat_moderators"] if item["category"]=="moderation_semantics" else ["community_bots"] if item["category"]=="permissions" else ["all_ai_bots"])
        assert item["decision"]=="human_review" if item["category"]=="moderation_semantics" else item["decision"] in {"answer","clarify","abstain","refuse_claim"}
        assert not re.search(r"https?://|@[a-zA-Z0-9_]+|token\\s*[:=]|password\\s*[:=]",json.dumps(item,ensure_ascii=False),re.I)
    search=KnowledgeSearch()
    for item in added:
        hits=search.search(item["input"],audience=item["audiences"][0],limit=20)
        assert any(z[0]==item["id"] for z in hits),item["id"]
        if item["category"] in ("permissions","moderation_semantics"):
            outside=search.search(item["input"],audience="all_ai_bots",limit=20)
            assert not any(z[0]==item["id"] for z in outside)
    print("T73_CONTEXT_OK 30 new, 170 total, 10 categories, no sanctions")
if __name__=="__main__":main()
