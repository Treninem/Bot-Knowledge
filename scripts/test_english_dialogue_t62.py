"""T62 original English dialogue meanings, ambiguity and offline index."""
import json,hashlib
from pathlib import Path
from collections import Counter
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/english_dialogues.json"
PREFIX="en_t62_"
N=41
EXPECTED={'conversation':7,'support':7,'slang':7,'sarcasm':7,'context':6,'creative':7}
def main():
 raw=(ROOT/REL).read_bytes()
 m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
 assert len(raw)<2*1024*1024
 assert hashlib.sha256(raw).hexdigest()==next(v["sha256"] for v in m["packs"] if v["path"]==REL)
 cases=json.loads(raw)["cases"]
 new=[r for r in cases if r["id"].startswith(PREFIX)]
 assert len(new)==N
 assert dict(Counter(r["kind"] for r in new))==EXPECTED
 for fld in ["input","response"]:
  norm=[normalize_question(r[fld]) for r in cases]
  assert len(set(norm))==len(norm),fld
 assert len({r["id"] for r in cases})==len(cases)
 idx=KnowledgeSearch()
 for r in new:
  assert r["audiences"]==["all_ai_bots"] and r["language"]=="en"
  assert all(r[x].strip() for x in ["input","response","meaning_ru","avoid"])
  assert not any(x in r for x in ["action","auto_apply","sanction","ban","mute"])
  found=idx.search(r["input"],audience="all_ai_bots",limit=20)
  assert any(x[0]==r["id"] for x in found),r["id"]
 print(f"T62_EN_OK accepted={N} total={len(cases)}")
if __name__=="__main__":main()
