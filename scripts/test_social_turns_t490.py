import hashlib, json, re, unicodedata, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA = "3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
PARENT_BLOB = "faa2c9bb33543c9f7d5f72c2c3c2c4f032ba36f8"
EXPECTED = {"thanks": 35, "farewell": 35, "agreement": 50}
def norm(s):
    return " ".join(re.findall(r"\w+",unicodedata.normalize("NFKC",s).lower().replace("ё","е")))
def blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
class T490Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src_raw=(ROOT/"packs/ru/dialogue.json").read_bytes()
        cls.src=json.loads(cls.src_raw)
        cls.prev_raw=(ROOT/"staging/ru/social_turns_t489_context_pool.json").read_bytes()
        cls.prev=json.loads(cls.prev_raw)
        cls.stage=json.loads((ROOT/"staging/ru/social_turns_t490_context_pool.json").read_text("utf-8"))
    def test_source_sha_parent_and_read_only(self):
        self.assertEqual(hashlib.sha256(self.src_raw).hexdigest(),SOURCE_SHA)
        self.assertEqual(blob(self.prev_raw),PARENT_BLOB)
        m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        self.assertEqual(next(p["sha256"] for p in m["packs"] if p["path"]=="packs/ru/dialogue.json"),SOURCE_SHA)
        self.assertEqual(self.stage["previous_stage_blob_sha"],PARENT_BLOB)
        self.assertEqual(self.stage["source_pack_manifest_sha256"],SOURCE_SHA)
        self.assertFalse(self.stage["consumer_registered"])
        self.assertTrue(self.stage["constraints"]["requires_direct_address"])
        self.assertTrue(self.stage["constraints"]["read_only"])
    def test_counts_privacy_and_full_dedup(self):
        self.assertEqual({e["intent_id"]:len(e["replies"]) for e in self.stage["entries"]},EXPECTED)
        self.assertEqual(self.stage["checkpoint"]["added_candidates"],120)
        self.assertEqual(self.stage["checkpoint"]["remaining_total"],74)
        all_old=[s for a in self.src["reactions"].values() for s in a]
        for scoped in self.src["scoped_repair_reactions"]["intents"].values():
            for c in scoped["contexts"].values():
                all_old.extend(r["text"] for r in c["replies"])
        all_old.extend(r["text"] for e in self.prev["entries"] for r in e["replies"])
        existing={norm(t) for t in all_old}
        token_sets=[set(norm(t).split()) for t in all_old]
        unique_ids=set()
        for entry in self.stage["entries"]:
            self.assertEqual(entry["baseline_including_previous_stage"],len(self.src["reactions"][entry["intent_id"]])+len(next(e["replies"] for e in self.prev["entries"] if e["intent_id"]==entry["intent_id"])))
            self.assertLessEqual(entry["baseline_including_previous_stage"]+len(entry["replies"]),100)
            for r in entry["replies"]:
                self.assertNotIn(r["id"],unique_ids); unique_ids.add(r["id"])
                self.assertEqual(r["language"],"ru")
                self.assertEqual(r["audiences"],["all_ai_bots"])
                self.assertTrue(r["read_only"])
                self.assertIn(r["context"],("direct","private","group_addressed"))
                self.assertGreater(len(r["context_note"]),32)
                self.assertGreater(len(r["avoid"]),45)
                self.assertFalse(re.search(r"(?i)(https?://|ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|@[a-z0-9_]+)",r["text"]))
                k=norm(r["text"])
                self.assertNotIn(k,existing); existing.add(k)
                now=set(k.split())
                for prev in token_sets:
                    self.assertLess(len(now&prev)/len(now|prev),0.78,r["id"])
                token_sets.append(now)
        self.assertEqual(len(unique_ids),120)
if __name__=="__main__": unittest.main()
