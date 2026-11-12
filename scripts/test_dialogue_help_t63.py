"""T63: independently authored context-aware universal QA; offline only."""
import hashlib, json
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/dialogue_help_qa.json"
PREFIX="dlg_t63_"
EXPECTED=46

def main():
 raw=(ROOT/REL).read_bytes()
 manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
 assert len(raw)<1024*1024
 assert hashlib.sha256(raw).hexdigest()==next(e["sha256"] for e in manifest["packs"] if e["path"]==REL)
 pack=json.loads(raw)
 rows=pack["records"]
 group=[r for r in rows if r["id"].startswith(PREFIX)]
 assert len(group)==EXPECTED
 assert len({r["id"] for r in rows})==len(rows)
 queries=[normalize_question(x) for r in rows for x in [r["question"],*r.get("aliases",[])]]
 assert len(queries)==len(set(queries))
 search=KnowledgeSearch()
 for r in group:
  assert len(r["variants"])==2 and r["audiences"]==["all_ai_bots"]
  assert r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True}
  assert r["source"].startswith("https://github.com/Treninem/Bot-Knowledge/blob/")
  assert not any(key in r for key in ("action","auto_apply","sanction","ban","mute"))
  hits=search.search(r["question"],audience="all_ai_bots",limit=20)
  assert any(hit[0]==r["id"] for hit in hits),r["id"]
 print(f"T63_QA_OK accepted={len(group)} baseline=601 new_total={len(rows)}")
if __name__=="__main__":main()
