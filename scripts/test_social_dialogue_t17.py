"""T17 synthetic natural social cases: hash, privacy, contexts, retrieval."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
IDS=["talk_t17_001","talk_t17_002","talk_t17_003","talk_t17_004","talk_t17_005","talk_t17_006","talk_t17_007","talk_t17_008","talk_t17_009","talk_t17_010","talk_t17_011","talk_t17_012","talk_t17_013","talk_t17_014","talk_t17_015","talk_t17_016","talk_t17_017","talk_t17_018","talk_t17_019","talk_t17_020","talk_t17_021","talk_t17_022","talk_t17_023","talk_t17_024","talk_t17_025","talk_t17_026","talk_t17_027","talk_t17_028","talk_t17_029","talk_t17_030","talk_t17_031","talk_t17_032","talk_t17_033","talk_t17_034","talk_t17_035","talk_t17_036"]
def normalized(s):
    return re.sub(r"[^\w]+"," ",s.casefold().replace("ё","е")).strip()
def main():
    rel="packs/ru/social_dialogues.json"
    raw=(ROOT/rel).read_bytes()
    m=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    expected=next(x["sha256"] for x in m["packs"] if x["path"]==rel)
    if hashlib.sha256(raw).hexdigest()!=expected or len(raw)>=2*1024*1024: raise ValueError("T17 integrity")
    rows=json.loads(raw)["cases"]
    chosen=[x for x in rows if x["id"].startswith("talk_t17_")]
    if len(chosen)!=len(IDS) or set(x["id"] for x in chosen)!=set(IDS): raise ValueError("T17 coverage")
    unique=set()
    index=KnowledgeSearch()
    for r in chosen:
        if not (r["context"] and r["response"] and r["avoid"] and r["audiences"]==["all_ai_bots"]): raise ValueError("T17 context")
        k=normalized(r["input"])
        if k in unique: raise ValueError("T17 duplicate")
        unique.add(k)
        if not any(x[0]==r["id"] for x in index.search(r["input"],audience="all_ai_bots",limit=40)): raise ValueError("T17 missing: "+r["id"])
    print("T17_SOCIAL_OK cases="+str(len(chosen))+" retrieval="+str(len(unique)))
if __name__=="__main__": main()
