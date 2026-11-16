#!/usr/bin/env python3
"""Read-only original situational-humor qa.v1 pack regression."""
import hashlib
import json
import pathlib
import re
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
FILE=ROOT/"packs/ru/situational_microhumor_qa.json"
SHA="469ff1f0f05a4ef14cae1881af4c72632f31c9d5d70e7f5c694a13e69544e4d5"
VERSION="2026.11.16.008"
def norm(s):
    return " ".join(re.findall(r"[^\W_]+",s.casefold().replace("ё","е"),flags=re.UNICODE))
class MicroHumorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack=json.loads(FILE.read_text(encoding="utf-8"))
    def test_manifest_and_budget(self):
        self.assertEqual(hashlib.sha256(FILE.read_bytes()).hexdigest(),SHA)
        man=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        found=[x for x in man["packs"] if x["path"]=="packs/ru/situational_microhumor_qa.json"]
        self.assertEqual(len(found),1)
        self.assertEqual(found[0]["sha256"],SHA)
        self.assertEqual(self.pack["pack_version"],VERSION)
        self.assertLessEqual(sum((ROOT/x["path"]).stat().st_size for x in man["packs"]),8*1024*1024)
        self.assertLessEqual(FILE.stat().st_size,2*1024*1024)
    def test_originality_and_scope(self):
        rec=self.pack["records"]
        self.assertEqual(len(rec),12)
        self.assertEqual(len({x["id"] for x in rec}),12)
        phrases=[]
        for r in rec:
            self.assertTrue(r["question"].lower().startswith(("пошути","придумай","расскажи","дай")))
            self.assertEqual(len(r["variants"]),12)
            self.assertEqual(r["audiences"],["all_ai_bots"])
            self.assertEqual(r["constraints"],{"read_only":True,"requires_direct_address":True,"no_personal_data":True})
            self.assertEqual(r["language"],"ru")
            phrases.extend([r["answer"],*r["variants"]])
        self.assertEqual(len(phrases),156)
        self.assertEqual(len(set(map(norm,phrases))),108)
        self.assertTrue(all(not re.search(r"https?://|t\.me/|@[A-Za-z0-9_]|[0-9]{10,}",s,re.I) for s in phrases))
if __name__=="__main__":
    unittest.main()
