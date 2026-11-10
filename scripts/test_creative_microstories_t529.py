"""T529: 620 opt-in creative microstories; cumulative counts, IDs and scope."""
import hashlib, json, subprocess, unicodedata, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"packs/ru/social_dialogues.json"
STAGES=(524,525,526,527,528,529)
DELTAS={524:12,525:12,526:10,527:8,528:10,529:10}
def norm(s):
    s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
    return " ".join("".join(c if c.isalnum() else " " for c in s).split())
class T529Quality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stages={n:json.loads((ROOT/f"staging/ru/creative_microstories_t{n}_context_pool.json").read_text("utf-8")) for n in STAGES}
        cls.manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    def test_source_pinning_and_isolation(self):
        sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
        blob=subprocess.check_output(["git","hash-object",str(SOURCE)],cwd=ROOT,text=True).strip()
        self.assertIn({"path":"packs/ru/social_dialogues.json","sha256":sha},self.manifest["packs"])
        for n,pack in self.stages.items():
            self.assertEqual(pack["source_pack_manifest_sha256"],sha)
            self.assertEqual(pack["source_pack_blob_sha"],blob)
            self.assertFalse(pack["consumer_registered"])
            self.assertTrue(pack["constraints"]["requires_explicit_creative_request"])
            self.assertTrue(pack["constraints"]["no_sanctions"])
            self.assertTrue(pack["constraints"]["fiction_must_be_labeled"])
            self.assertNotIn(f"staging/ru/creative_microstories_t{n}_context_pool.json",[p["path"] for p in self.manifest["packs"]])
    def test_all_four_stages(self):
        stable={e["intent_id"]:e["canonical_question"] for e in self.stages[524]["entries"]}
        self.assertEqual(len(stable),10)
        ids,texts,notes,vectors=set(),set(),set(),[]
        previous=0
        for n,pack in self.stages.items():
            self.assertEqual(set(stable),{e["intent_id"] for e in pack["entries"]})
            self.assertEqual(pack["checkpoint"]["added_candidates"],DELTAS[n]*10)
            total=previous+DELTAS[n]
            self.assertEqual(pack["checkpoint"]["remaining_total"],(100-total)*10)
            self.assertEqual(pack["checkpoint"]["finished_100"],0)
            for e in pack["entries"]:
                self.assertEqual(e["canonical_question"],stable[e["intent_id"]])
                self.assertEqual(e["added_candidates"],DELTAS[n])
                self.assertEqual(e["total_staged"],total)
                self.assertEqual(e["remaining"],100-total)
                self.assertEqual(len(e["replies"]),DELTAS[n])
                if n!=524:self.assertEqual(e["prior_for_stable_id"],previous)
                for r in e["replies"]:
                    self.assertNotIn(r["id"],ids)
                    self.assertNotIn(norm(r["text"]),texts)
                    self.assertNotIn(norm(r["context_note"]),notes)
                    ids.add(r["id"]); texts.add(norm(r["text"]));notes.add(norm(r["context_note"]))
                    self.assertEqual(r["language"],"ru")
                    self.assertEqual(r["context"],"direct")
                    self.assertEqual(r["format"],"microstory")
                    self.assertEqual(r["audiences"],["all_ai_bots"])
                    self.assertTrue(r["read_only"])
                    self.assertIn("Это вымысел",r["avoid"])
                    self.assertIn("вымышленную",r["context_note"])
                    self.assertTrue(50<=len(r["text"])<=480)
                    self.assertNotRegex(r["text"],r"(?i)https?://|@\w+|(?:\+7|\b8)\d{10}\b")
                    tok=set(norm(r["text"]).split())
                    for old in vectors:self.assertLess(len(tok&old)/len(tok|old),0.78)
                    vectors.append(tok)
            previous=total
        self.assertEqual(previous,62)
        self.assertEqual(len(ids),620)
        self.assertEqual(len(texts),620)
        self.assertEqual(len(notes),620)
if __name__=="__main__":unittest.main()
