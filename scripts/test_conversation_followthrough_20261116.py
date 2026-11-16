#!/usr/bin/env python3
"""Regression for the 82-intent conversation followthrough expansion."""
import hashlib
import json
import pathlib
import re
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
FILE=ROOT/"packs/ru/conversation_followthrough_qa.json"
DIGEST="e4393e724bf3852bac969cf7fbe2c1e02c86b04e232aa1aaf79b380d6f34eca5"
VERSION="2026.11.16.007"
def normalize(s):
    return " ".join(re.findall(r"[^\W_]+",s.casefold().replace("ё","е"),flags=re.UNICODE))
class TestFollowthrough(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads(FILE.read_text(encoding="utf-8"))
        cls.records=cls.data["records"]
    def test_hash_manifest(self):
        self.assertEqual(hashlib.sha256(FILE.read_bytes()).hexdigest(),DIGEST)
        self.assertEqual(self.data["pack_version"],VERSION)
        manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        found=[p for p in manifest["packs"] if p["path"]=="packs/ru/conversation_followthrough_qa.json"]
        self.assertEqual(len(found),1)
        self.assertEqual(found[0]["sha256"],DIGEST)
    def test_scope_variants_and_duplicates(self):
        self.assertEqual(len(self.records),82)
        self.assertEqual(len({r["id"] for r in self.records}),82)
        phrases=[]
        for r in self.records:
            self.assertEqual(len(r["variants"]),4,r["id"])
            self.assertEqual(r["audiences"],["all_ai_bots"])
            self.assertEqual(r["language"],"ru")
            self.assertEqual(r["constraints"],{"read_only":True,"requires_direct_address":True,"no_personal_data":True})
            phrases.extend([r["answer"],*r["variants"]])
        self.assertEqual(len(phrases),410)
        self.assertEqual(len(set(map(normalize,phrases))),410)
    def test_pack_and_snapshot_limits(self):
        manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        self.assertLessEqual(sum((ROOT/p["path"]).stat().st_size for p in manifest["packs"]),8*1024*1024)
        self.assertLessEqual(FILE.stat().st_size,2*1024*1024)
if __name__=="__main__":
    unittest.main()
