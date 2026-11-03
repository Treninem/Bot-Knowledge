"""T64: original English context, scoped meaning, local retrieval."""
import hashlib,json
from pathlib import Path
from scripts.validate_qa_v1 import normalize_question
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/english_dialogues.json"
PREFIX="en_t64_"
N=58
EXPECTED={'conversation':10,'support':8,'slang':7,'sarcasm':7,'context':8,'rules':5,'deception':5,'creative':8}
def main():
 raw=(ROOT/REL).read_bytes()
 m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
 assert hashlib.sha256(raw).hexdigest()==next(x["sha256"] for x in m["packs"] if x["path"]==REL)
 assert len(raw)<2*1024*1024
 cases=json.loads(raw)["cases"]
 latest=[x for x in cases if x["id"].startswith(PREFIX)]
 assert len(latest)==N
 from collections import Counter
 assert dict(Counter(x["kind"] for x in latest))==EXPECTED
 assert len({x["id"] for x in cases})==len(cases)
 for field in ("input","response"):
  normalized=[normalize_question(x[field]) for x in cases]
  assert len(set(normalized))==len(normalized),field
 search=KnowledgeSearch()
 for r in latest:
  assert r["language"]=="en" and r["audiences"]==["all_ai_bots"]
  assert all(r[k].strip() for k in ("input","response","meaning_ru","avoid"))
  assert not any(k in r for k in ("sanction","action","auto_apply","ban","mute"))
  assert any(x[0]==r["id"] for x in search.search(r["input"],audience="all_ai_bots",limit=20)),r["id"]
 print("T64_EN_OK accepted=%s baseline=814 total=%s"%(len(latest),len(cases)))
if __name__=="__main__":main()
