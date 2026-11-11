"""Read-only exact-content QA: preserve 500 historical alternate group replies without ID collisions."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ARCHIVE=ROOT/"staging/ru/group_pragmatics_t611_alternatives_review_only.json"
MAIN=[ROOT/"staging/ru/group_pragmatics_t600_context_pool.json"]+[
    ROOT/f"staging/ru/group_pragmatics_t{n}_context_delta.json" for n in range(601,610)
]
TOKEN=re.compile(r"[^\\W_]+",re.UNICODE)
def norm(v):
    return " ".join(TOKEN.findall(unicodedata.normalize("NFKC",v).casefold().replace("ё","е")))

class AlternativeSalvage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.archive=json.loads(ARCHIVE.read_text("utf-8"))
        cls.base=[json.loads(path.read_text("utf-8")) for path in MAIN]
        cls.alternates=[r for e in cls.archive["entries"] for r in e["review_only_alternates"]]
        cls.primary=[r for stage in cls.base for e in stage["entries"] for r in e["replies"]]
    def test_source_and_isolation(self):
        a=self.archive
        manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        source=(ROOT/a["source_pack"]).read_bytes()
        sha=hashlib.sha256(source).hexdigest()
        expect={p["path"]:p["sha256"] for p in manifest["packs"]}
        self.assertEqual(a["consumer_registered"],False)
        self.assertEqual(a["stage_type"],"historical_review_only_alternative_context_archive")
        self.assertEqual(a["audiences"],["all_ai_bots"])
        self.assertEqual(a["source_pack_manifest_sha256"],sha)
        self.assertEqual(expect[a["source_pack"]],sha)
        self.assertNotIn(str(ARCHIVE.relative_to(ROOT)),expect)
        for key in ("read_only","requires_direct_address","no_personal_data","no_sanctions","requires_context_match"):
            self.assertIs(a["constraints"][key],True)
        self.assertEqual(a["source_pr_number"],611)
        self.assertEqual(a["source_original_head_sha"],"d234d00fc0405015100b78ebba4b953e0df91907")
        self.assertEqual(len(a["source_stage_blobs"]),5)
        self.assertEqual([x["sha"] for x in a["source_stage_blobs"]],[
            "32aa5d17a746cafb54857e8db272e0bfef256c12",
            "4a833521cdd3d59b388833726e91834cb0d7a350",
            "907424733c2cbf89a0af5a55bc3460bb0d002813",
            "f84fdbcc0224a1ae23c40a12c35aa62a5dd3ee86",
            "285cd412ed2e85f3368ced3d2f87f41003cf6532"])
    def test_shape_and_stable_intents(self):
        a=self.archive
        self.assertEqual(len(self.primary),1000)
        self.assertEqual(len(self.alternates),500)
        self.assertEqual(len(a["entries"]),10)
        self.assertEqual(a["checkpoint"]["newly_authored"],0)
        self.assertEqual(a["checkpoint"]["preserved_from_old_pr"],500)
        original_ids=[e["intent_id"] for e in self.base[0]["entries"]]
        self.assertEqual([e["intent_id"] for e in a["entries"]],original_ids)
        for e in a["entries"]:
            self.assertEqual(e["registered_main_staged_count"],100)
            self.assertEqual(len(e["review_only_alternates"]),50)
            for idx,r in enumerate(e["review_only_alternates"]):
                self.assertEqual(r["original_id"],f'{e["intent_id"]}_{41+idx:02}')
                self.assertEqual(r["id"],"t611_alt_"+r["original_id"])
                self.assertEqual(r["original_stage"],604+idx//10)
                self.assertIs(r["alternative_only"],True)
                self.assertIs(r["read_only"],True)
                self.assertEqual(r["context"],"direct")
                self.assertEqual(r["audiences"],["all_ai_bots"])
                self.assertGreaterEqual(len(r["text"]),24)
                self.assertGreaterEqual(len(r["context_note"]),18)
    def test_global_noncollision_and_privacy(self):
        ids={r["id"] for r in self.primary}
        self.assertFalse(ids.intersection(r["id"] for r in self.alternates))
        for key in ("id","text","context_note"):
            vals=[r[key] if key=="id" else norm(r[key]) for r in self.alternates]
            self.assertEqual(len(vals),len(set(vals)),key)
        primary_text={norm(r["text"]) for r in self.primary}
        self.assertFalse(primary_text.intersection(norm(r["text"]) for r in self.alternates))
        all_tokens=[set(norm(r["text"]).split()) for r in self.primary+self.alternates]
        for idx in range(len(self.primary),len(all_tokens)):
            a=all_tokens[idx]
            for b in all_tokens[:idx]:
                self.assertLess(len(a&b)/len(a|b),0.80,self.alternates[idx-len(self.primary)]["id"])
        for r in self.alternates:
            self.assertNotRegex(r["text"],r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}")
            self.assertNotIn("ghp_",r["text"])
            self.assertNotIn("я забанил",norm(r["text"]))
            self.assertNotIn("я замутил",norm(r["text"]))
if __name__=="__main__":
    unittest.main()
