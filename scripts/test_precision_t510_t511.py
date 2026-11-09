"""T510-T511: verify cumulative synthetic contextual replies and completion."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREFIX=ROOT/"staging/ru"
NAMES=("t507","t508","t509","t510","t511")
EXPECTED_NEW=(100,140,140,140,180)
EXPECTED_TOTALS=(100,240,380,520,700)
EXPECTED_REMAINING=(600,460,320,180,0)

def normalize(s):
    s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
    return " ".join(re.findall(r"\w+",s))

def jaccard(a,b):
    x,y=set(a.split()),set(b.split())
    return len(x & y)/len(x | y) if (x or y) else 1

class T511CompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stages=[]
        for name in NAMES:
            cls.stages.append(json.loads((PREFIX/f"precision_{name}_context_pool.json").read_text(encoding="utf-8")))

    def test_registered_source_unchanged_and_candidate_only(self):
        raw=(ROOT/"packs/ru/dialogue.json").read_bytes()
        sha=hashlib.sha256(raw).hexdigest()
        blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        self.assertIn({"path":"packs/ru/dialogue.json","sha256":sha},manifest["packs"])
        for s in self.stages:
            self.assertEqual(s["source_pack"],"packs/ru/dialogue.json")
            self.assertEqual(s["source_pack_manifest_sha256"],sha)
            self.assertEqual(s["source_pack_blob_sha"],blob)
            self.assertEqual(s["stage_type"],"supplemental_contextual_reply_pool")
            self.assertEqual(s["language"],"ru")
            self.assertEqual(s["audiences"],["all_ai_bots"])
            self.assertFalse(s["consumer_registered"])
            self.assertTrue(all(s["constraints"].values()))

    def test_cumulative_stability_and_quality_boundaries(self):
        seen_ids=set()
        seen_texts=[]
        seen_normalized=set()
        seen_notes=set()
        prev=None
        intent_ids=None
        for idx,stage in enumerate(self.stages):
            name=NAMES[idx].upper()
            entries={e["intent_id"]:e for e in stage["entries"]}
            self.assertEqual(len(entries),7)
            if intent_ids is None: intent_ids=set(entries)
            self.assertEqual(set(entries),intent_ids)
            self.assertEqual(stage["checkpoint"]["stage_id"],name)
            self.assertEqual(stage["checkpoint"]["added_candidates"],EXPECTED_NEW[idx])
            self.assertEqual(stage["checkpoint"]["remaining_total"],EXPECTED_REMAINING[idx])
            self.assertEqual(stage["checkpoint"]["processed_intents"],7)
            self.assertEqual(stage["checkpoint"]["previous_stage"],NAMES[idx-1].upper() if idx else "T506")
            if idx>=2:
                self.assertEqual(stage["checkpoint"]["base_commit"],"2d1c4a7f885c66ea5c8be4e81293ea643aa9a7d4")
            for key,entry in entries.items():
                if prev is not None:
                    self.assertEqual(entry["canonical_question"],prev[key]["canonical_question"])
                    self.assertEqual(entry["prior_for_stable_id"],prev[key]["total_staged"])
                    self.assertEqual(entry["total_staged"],prev[key]["total_staged"]+entry["added_candidates"])
                self.assertEqual(len(entry["replies"]),entry["added_candidates"])
                self.assertEqual(entry["target"],100)
                self.assertEqual(entry["remaining"],100-entry["total_staged"])
                for item in entry["replies"]:
                    txt=normalize(item["text"])
                    note=normalize(item["context_note"])
                    self.assertGreater(len(txt),45,item["id"])
                    self.assertGreater(len(note),20,item["id"])
                    self.assertNotIn(item["id"],seen_ids)
                    self.assertNotIn(txt,seen_normalized)
                    self.assertNotIn(note,seen_notes)
                    self.assertEqual(item["language"],"ru")
                    self.assertEqual(item["audiences"],["all_ai_bots"])
                    self.assertEqual(item["context"],"direct")
                    self.assertTrue(item["read_only"])
                    self.assertTrue(item["avoid"])
                    self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)",item["text"]))
                    self.assertFalse(re.search(r"(?i)\b(забань|замуть|удали чужое сообщение)\b",item["text"]))
                    for existing in seen_texts:
                        self.assertLess(jaccard(txt,existing),0.78,f"{item['id']} is too close to a prior reply")
                    seen_ids.add(item["id"])
                    seen_normalized.add(txt)
                    seen_notes.add(note)
                    seen_texts.append(txt)
            self.assertEqual(sum(e["total_staged"] for e in entries.values()),EXPECTED_TOTALS[idx])
            self.assertEqual(sum(e["remaining"] for e in entries.values()),EXPECTED_REMAINING[idx])
            prev=entries
        self.assertEqual(len(seen_texts),700)
        self.assertEqual(sum(e["total_staged"]==100 for e in prev.values()),7)
        self.assertEqual(self.stages[-1]["checkpoint"]["finished_100"],7)
        self.assertEqual(self.stages[-1]["checkpoint"]["partial_intents"],0)
        self.assertTrue(all(e["remaining"]==0 for e in prev.values()))

    def test_no_exact_overlap_with_related_practical_stages(self):
        normed={normalize(rep["text"]) for stage in self.stages for e in stage["entries"] for rep in e["replies"]}
        for name in ("t503","t504","t505","t506"):
            f=PREFIX/f"practical_turns_{name}_context_pool.json"
            if not f.exists(): continue
            o=json.loads(f.read_text(encoding="utf-8"))
            for e in o["entries"]:
                for reply in e["replies"]:
                    self.assertNotIn(normalize(reply["text"]),normed)

if __name__=="__main__":
    unittest.main()
