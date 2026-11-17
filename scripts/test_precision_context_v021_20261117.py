#!/usr/bin/env python3
"""v021: immutable v020 delta, formatting-only compaction, safety and snapshot budget."""
import hashlib, json, re, subprocess, unicodedata, unittest
from pathlib import Path
from validate_pack import MAX_CONSUMER_SNAPSHOT_BYTES, evaluate_snapshot_budget
from validate_qa_v1 import validate_qa_manifest
ROOT=Path(__file__).resolve().parents[1]
OLD="10fc0c437639eb8ad54d58cc97d0ad6958f74800"
PATH="packs/ru/conversation_precision_qa.json"
SECOND="packs/ru/structured_information_qa.json"
OLD_HASH="55204fa5f9109c1446a00e65beaa726b92d2848f285fd8e04d247cd8063bb66f"
NEW_HASH="b37d35a98d6dd919bace2275b838f61a7973b9d3a4207b44a7a1b6040164350b"
SECOND_OLD_HASH="55b3f6126d36cd92687d005b7fedf5a11df9ee61cf453103accdf1f13c8498f0"
SECOND_NEW_HASH="c51c28d1ed6d475b809666b3c2b23e2e6537629e85b81e463b5e0b67b20bbd9e"
def norm(s):
 return " ".join(re.sub(r"[^\w\s]", " ", unicodedata.normalize("NFKC",s).casefold().replace("ё","е")).split())
def similarity(a,b):
 a,b=set(norm(a).split()),set(norm(b).split())
 return len(a&b)/len(a|b) if a|b else 0
class PrecisionV021(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old_bytes=subprocess.check_output(["git","show",f"{OLD}:{PATH}"],cwd=ROOT)
  cls.new_bytes=(ROOT/PATH).read_bytes()
  cls.old=json.loads(cls.old_bytes);cls.new=json.loads(cls.new_bytes)
  cls.old_second=subprocess.check_output(["git","show",f"{OLD}:{SECOND}"],cwd=ROOT)
  cls.new_second=(ROOT/SECOND).read_bytes()
  cls.manifest=json.loads((ROOT/"manifest.json").read_bytes())
 def test_exact_delta(self):
  self.assertEqual(hashlib.sha256(self.old_bytes).hexdigest(),OLD_HASH)
  self.assertEqual(hashlib.sha256(self.new_bytes).hexdigest(),NEW_HASH)
  self.assertEqual(self.new["pack_version"],"2026.11.17.021")
  base={x["id"]:x for x in self.old["records"]};current={x["id"]:x for x in self.new["records"]}
  self.assertEqual(len(base),132);self.assertEqual(set(base),set(current))
  fresh=[]
  for key,p in base.items():
   q=current[key]
   self.assertEqual({k:v for k,v in q.items() if k!="variants"},{k:v for k,v in p.items() if k!="variants"},key)
   self.assertEqual(q["variants"][:len(p["variants"])],p["variants"],key)
   added=q["variants"][len(p["variants"]):]
   self.assertEqual(len(added),1,key)
   self.assertEqual(len(q["variants"]),8,key)
   answer=added[0]
   self.assertLess(max(similarity(answer,x) for x in [p["answer"],*p["variants"]]),.56,key)
   self.assertFalse(re.search(r"https?://|t\.me/|@[A-Za-z0-9_]{3,}|\b\d{10,}\b|(?:ghp_|sk-)[A-Za-z0-9]{12,}",answer,re.I),key)
   fresh.append(answer)
  self.assertEqual(len(fresh),132)
  self.assertEqual(len(set(map(norm,fresh))),132)
 def test_secondary_pack_semantic_only(self):
  self.assertEqual(hashlib.sha256(self.old_second).hexdigest(),SECOND_OLD_HASH)
  self.assertEqual(hashlib.sha256(self.new_second).hexdigest(),SECOND_NEW_HASH)
  self.assertEqual(json.loads(self.old_second),json.loads(self.new_second))
 def test_manifest_and_budget(self):
  self.assertGreaterEqual(tuple(int(n) for n in self.manifest["knowledge_version"].split(".")),(2026,11,17,21))
  hashes={x["path"]:x["sha256"] for x in self.manifest["packs"]}
  self.assertEqual(hashes[PATH],NEW_HASH)
  self.assertEqual(hashes[SECOND],SECOND_NEW_HASH)
  self.assertEqual(validate_qa_manifest(ROOT),[])
  total,free=evaluate_snapshot_budget((ROOT/"manifest.json").stat().st_size,[(ROOT/x["path"]).stat().st_size for x in self.manifest["packs"]])
  self.assertLessEqual(total,MAX_CONSUMER_SNAPSHOT_BYTES)
  self.assertGreaterEqual(free,0)
if __name__=="__main__":unittest.main()
