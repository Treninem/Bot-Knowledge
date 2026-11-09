"""T500: finish three group-context intents to 100/100 in a read-only staged candidate pool."""
import hashlib, json, re, unicodedata, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT/"staging/ru/group_turns_t500_context_pool.json"
SOURCE_SHA = "3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
SOURCE_BLOB = "b881d145f634b6104c8538fef708d45162ef3125"
PARENT_BLOB = "b6ee77de813846515fe411df11253aeec88853fc"
FINISHED = {"group_addressed_thread", "group_dispute_neutrality", "group_roles_readonly"}
UNFINISHED = {"group_private_boundary":70,"humor_consent_withdrawn":70,"rudeness_without_retaliation":70}

def norm(s):
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC",s).lower().replace("ё","е")))

def blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def extract(obj):
    if isinstance(obj,dict):
        for key,val in obj.items():
            if key in ("text","answer","reply","response","assistant_response","response_text","reply_text") and isinstance(val,str):
                yield val
            else:
                yield from extract(val)
    elif isinstance(obj,list):
        for val in obj:
            yield from extract(val)

class T500Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_raw=(ROOT/"packs/ru/dialogue.json").read_bytes()
        cls.parent_raw=(ROOT/"staging/ru/group_turns_t499_context_pool.json").read_bytes()
        cls.parent=json.loads(cls.parent_raw)
        cls.stage=json.loads(STAGE.read_text("utf-8"))

    def test_source_and_checkpoint(self):
        self.assertEqual(hashlib.sha256(self.source_raw).hexdigest(),SOURCE_SHA)
        self.assertEqual(blob(self.source_raw),SOURCE_BLOB)
        manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        self.assertEqual(next(x["sha256"] for x in manifest["packs"] if x["path"]=="packs/ru/dialogue.json"),SOURCE_SHA)
        self.assertEqual(blob(self.parent_raw),PARENT_BLOB)
        self.assertEqual(self.stage["previous_stage"]["git_blob"],PARENT_BLOB)
        self.assertEqual(self.stage["source_pack_blob_sha"],SOURCE_BLOB)
        self.assertEqual(self.stage["source_pack_manifest_sha256"],SOURCE_SHA)
        self.assertFalse(self.stage["consumer_registered"])
        self.assertTrue(self.stage["constraints"]["requires_direct_address"])
        self.assertTrue(self.stage["constraints"]["read_only"])
        self.assertEqual(self.stage["audiences"],["all_ai_bots"])
        ck=self.stage["checkpoint"]
        self.assertEqual(ck["stage_id"],"T500")
        self.assertEqual(ck["baseline_previous_six_intents"],420)
        self.assertEqual(ck["added_candidates"],90)
        self.assertEqual(ck["total_across_six_intents"],510)
        self.assertEqual(ck["finished_100_in_this_stage"],3)
        self.assertEqual(ck["remaining_partial_intents"],3)
        self.assertEqual(ck["remaining_total"],90)
        self.assertEqual(set(ck["complete_intent_ids"]),FINISHED)
        self.assertEqual(ck["partially_complete_untouched"],UNFINISHED)
        self.assertEqual({e["intent_id"] for e in self.stage["entries"]},FINISHED)
        for entry in self.stage["entries"]:
            old=next(e for e in self.parent["entries"] if e["intent_id"]==entry["intent_id"])
            self.assertEqual(old["total_staged"],70)
            self.assertEqual(entry["baseline_including_previous_stages"],70)
            self.assertEqual(entry["added_candidates"],30)
            self.assertEqual(len(entry["replies"]),30)
            self.assertEqual(entry["total_staged"],100)
            self.assertEqual(entry["target"],100)
            self.assertEqual(entry["remaining"],0)

    def test_context_privacy_and_distinctness(self):
        history=set()
        for folder in (ROOT/"packs/ru",ROOT/"staging/ru"):
            for p in folder.glob("*.json"):
                if p==STAGE:
                    continue
                history.update(norm(x) for x in extract(json.loads(p.read_text("utf-8"))) if x.strip())
        history.update(norm(x) for v in json.loads(self.source_raw)["reactions"].values() for x in v)
        history.discard("")
        buckets={}
        for k in history:
            t=frozenset(k.split())
            buckets.setdefault(len(t),[]).append(t)
        ids=set();seen=set();notes=set()
        for entry in self.stage["entries"]:
            for r in entry["replies"]:
                self.assertNotIn(r["id"],ids);ids.add(r["id"])
                self.assertEqual(r["language"],"ru")
                self.assertEqual(r["style"],"neutral")
                self.assertEqual(r["audiences"],["all_ai_bots"])
                self.assertEqual(r["context"],"group_addressed")
                self.assertTrue(r["read_only"])
                self.assertGreater(len(r["context_note"]),34)
                self.assertGreater(len(r["avoid"]),100)
                note=norm(r["context_note"])
                self.assertNotIn(note,notes);notes.add(note)
                self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)",r["text"]))
                self.assertFalse(re.search(r"(?i)\b(забань|замуть|заблокируй пользователя|удали чужое сообщение)\b",r["text"]))
                k=norm(r["text"])
                self.assertNotIn(k,history,r["id"])
                self.assertNotIn(k,seen,r["id"]);seen.add(k)
                t=frozenset(k.split())
                for n in range(max(1,int(len(t)*.78)),int(len(t)/.78)+2):
                    for other in buckets.get(n,()):
                        common=len(t & other)
                        self.assertLess(common/(len(t)+len(other)-common),.78,r["id"])
                buckets.setdefault(len(t),[]).append(t)
        self.assertEqual(len(ids),90)

if __name__=="__main__":
    unittest.main()
