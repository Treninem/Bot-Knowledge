"""T61: new general QA, manifest SHA, normalized questions and offline search."""
import hashlib, json
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question,validate_qa_pack
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/dialogue_help_qa.json"
PREFIX="dlg_t61_"
COUNT=43
def main():
 raw=(ROOT/REL).read_bytes()
 manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
 assert len(raw)<1024*1024
 assert hashlib.sha256(raw).hexdigest()==next(e["sha256"] for e in manifest["packs"] if e["path"]==REL)
 pack=json.loads(raw)
 assert validate_qa_pack(pack)==len(pack["records"])
 new=[r for r in pack["records"] if r["id"].startswith(PREFIX)]
 assert len(new)==COUNT
 seen=set()
 for r in pack["records"]:
  for p in [r["question"],*r["aliases"]]:
   s=normalize_question(p)
   assert s not in seen,(r["id"],p)
   seen.add(s)
 index=KnowledgeSearch()
 checks=0
 for r in new:
  assert r["audiences"]==["all_ai_bots"]
  assert r["contexts"]==["direct","private","group_addressed"]
  assert r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True}
  assert r["source"]=="https://github.com/Treninem/Bot-Knowledge/blob/0c1c814cd5d2724439ce078947761521f4f12570/docs/REQUIREMENTS_21.md"
  assert r["language"]=="ru" and len(r["variants"])==2 and len(r["aliases"])==2
  assert len(set([r["answer"],*r["variants"]]))==3
  assert not any(k in r for k in ("action","auto_apply","ban","mute","execute"))
  for q in [r["question"],*r["aliases"]]:
   hits=index.search(q,audience="all_ai_bots",limit=20)
   assert any(hit[0]==r["id"] for hit in hits),(r["id"],q)
   checks+=1
 print(f"T61_OK records={COUNT} answers={COUNT*3} queries={checks}")
if __name__=="__main__": main()
