"""T16 synthetic natural replies, scoped qa.v1 and local lookup checks."""
from __future__ import annotations
import hashlib, json, unicodedata
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
def norm(s):
    return " ".join("".join(c if c.isalnum() else " " for c in unicodedata.normalize("NFKC",s).casefold().replace("ё","е")).split())
def main():
    m=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    index=KnowledgeSearch()
    for rel,prefix,count,collection in [("packs/ru/dialogue_help_qa.json","dlg_t16_",24,"records"),("packs/ru/social_dialogues.json","talk_t16_",42,"cases")]:
        raw=(ROOT/rel).read_bytes()
        sha=next(x["sha256"] for x in m["packs"] if x["path"]==rel)
        assert hashlib.sha256(raw).hexdigest()==sha
        assert len(raw)<2*1024*1024
        items=json.loads(raw)[collection]
        selected=[x for x in items if x["id"].startswith(prefix)]
        assert len(selected)==count and len(set(x["id"] for x in items))==len(items)
        assert len(set(norm(x["input"] if collection=="cases" else x["question"]) for x in selected))==count
        for x in selected:
            assert x["audiences"]==["all_ai_bots"]
            if collection=="records":
                assert len(x["variants"])==len(x["aliases"])==2 and x["contexts"]==["direct","private","group_addressed"]
                prompts=[x["question"],*x["aliases"]]
            else:
                assert x["context"] and x["avoid"] and x["response"]
                prompts=[x["input"]]
            for q in prompts:
                hits=index.search(q,audience="all_ai_bots",limit=20)
                assert any(h[0]==x["id"] for h in hits),(x["id"],q,hits)
    print("T16_NATURAL_HELP_OK qa=24 social=42 searches=114")
if __name__=="__main__":main()
