#!/usr/bin/env python3
"""v019 pinned exact published-delta and read-only consumer budget checks."""
import hashlib,json,re,subprocess,unicodedata,unittest
from pathlib import Path
from validate_pack import MAX_CONSUMER_SNAPSHOT_BYTES,evaluate_snapshot_budget
from validate_qa_v1 import validate_qa_manifest
ROOT=Path(__file__).resolve().parents[1]
PATH="packs/ru/conversation_precision_qa.json"
OLD="059ee2f93892b47891cf181be266cae005f97305"
OLD_HASH="976b073b94eb26eaa8f5cbffe4be161b37940c8679b368819b72b9fd8c1db394"
NEW_HASH="de8a9735838a31d13dc9702c691a4feda32cbea9f81aed748922366c2cda274f"
IDS=set(["precision_t77_001","precision_t77_002","precision_t77_003","precision_t77_004","precision_t77_005","precision_t77_006","precision_t77_007","precision_t77_008","precision_t77_009","precision_t77_010","precision_t77_011","precision_t77_012","precision_t77_013","precision_t77_014","precision_t77_015","precision_t77_016","precision_t77_017","precision_t77_018","precision_t77_019","precision_t77_020","precision_t77_021","precision_t77_022","precision_t77_023","precision_t77_024","precision_t77_025","precision_t77_026","precision_t77_027","precision_t77_028","precision_t77_029","precision_t77_030","precision_t77_031","precision_t77_032","precision_t77_033","precision_t77_034","precision_t77_035","precision_t77_036","precision_t77_037","precision_t77_038","precision_t77_039","precision_t77_040","precision_t77_041","precision_t77_042","precision_t82_001","precision_t82_002","precision_t82_003","precision_t82_004","precision_t82_005","precision_t82_006","precision_t82_007","precision_t82_008","precision_t82_009","precision_t82_010","precision_t82_011","precision_t82_012","precision_t82_013","precision_t82_014","precision_t82_015","precision_t82_016","precision_t82_017","precision_t82_018","precision_t82_019","precision_t82_020","precision_t82_021","precision_t82_022","precision_t82_023","precision_t82_024","precision_t82_025","precision_t82_026","precision_t82_027","precision_t82_028","precision_t82_029","precision_t82_030","precision_t82_031","precision_t82_032","precision_t82_033","precision_t82_034","precision_t82_035","precision_t82_036","precision_t82_037","precision_t82_038","precision_t82_039","precision_t82_040","precision_t82_041","precision_t82_042","precision_t85_001","precision_t85_002","precision_t85_003","precision_t85_004","precision_t85_005","precision_t85_006","precision_t85_007","precision_t85_008","precision_t85_009","precision_t85_010","precision_t85_011","precision_t85_012","precision_t85_013","precision_t85_014","precision_t85_015","precision_t85_016","precision_t85_017","precision_t85_018","precision_t85_019","precision_t85_020","precision_t85_021","precision_t85_022","precision_t85_023","precision_t85_024","precision_t85_025","precision_t85_026","precision_t85_027","precision_t85_028","precision_t85_029","precision_t85_030","precision_t85_031","precision_t85_032","precision_t85_033","precision_t85_034","precision_t85_035","precision_t85_036","precision_t85_037","precision_t85_038","precision_t85_039","precision_t85_040","precision_t85_041","precision_t85_042","precision_t85_043","precision_t85_044","precision_t85_045","precision_t85_046","precision_t85_047","precision_t85_048"])
def norm(s):return " ".join(re.sub(r"[^\\w\\s]"," ",unicodedata.normalize("NFKC",s).casefold().replace("ё","е")).split())
def overlap(a,b):
 a,b=set(norm(a).split()),set(norm(b).split())
 return len(a&b)/len(a|b) if a|b else 0
class PrecisionV019(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.old_bytes=subprocess.check_output(["git","show",f"{OLD}:{PATH}"],cwd=ROOT)
  cls.new_bytes=(ROOT/PATH).read_bytes()
  cls.old=json.loads(cls.old_bytes);cls.new=json.loads(cls.new_bytes)
  cls.manifest=json.loads((ROOT/"manifest.json").read_bytes())
 def test_delta(self):
  self.assertEqual(hashlib.sha256(self.old_bytes).hexdigest(),OLD_HASH)
  self.assertEqual(hashlib.sha256(self.new_bytes).hexdigest(),NEW_HASH)
  self.assertEqual(self.new["pack_version"],"2026.11.16.019")
  o={x["id"]:x for x in self.old["records"]};n={x["id"]:x for x in self.new["records"]}
  self.assertEqual(len(o),132);self.assertEqual(set(o),set(n))
  fresh=[]
  for key,prior in o.items():
   cur=n[key];self.assertEqual({k:v for k,v in prior.items() if k!="variants"},{k:v for k,v in cur.items() if k!="variants"},key)
   self.assertEqual(cur["variants"][:len(prior["variants"])],prior["variants"],key)
   delta=cur["variants"][len(prior["variants"]):]
   self.assertEqual(len(delta),int(key in IDS),key)
   for x in delta:
    self.assertLess(max(overlap(x,v) for v in [prior["answer"],*prior["variants"]]),.56,key)
    self.assertFalse(re.search(r"https?://|t\\.me/|@[A-Za-z0-9_]{3,}|\\b\\d{10,}\\b|(?:ghp_|sk-)[A-Za-z0-9]{12,}",x,re.I))
    fresh.append(x)
  self.assertEqual(len(fresh),132)
  self.assertEqual(len(set(map(norm,fresh))),len(fresh))
 def test_registered(self):
  self.assertEqual(self.manifest["knowledge_version"],"2026.11.16.019")
  self.assertEqual(next(x["sha256"] for x in self.manifest["packs"] if x["path"]==PATH),NEW_HASH)
  self.assertEqual(validate_qa_manifest(ROOT),[])
  raw=(ROOT/"manifest.json").read_bytes()
  total,remaining=evaluate_snapshot_budget(len(raw),[(ROOT/x["path"]).stat().st_size for x in self.manifest["packs"]])
  self.assertLessEqual(total,MAX_CONSUMER_SNAPSHOT_BYTES);self.assertGreaterEqual(remaining,0)
if __name__=="__main__":unittest.main()
