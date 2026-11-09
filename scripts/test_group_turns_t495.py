"""T495: six group dialogue intents, 120 new context-specific synthetic Russian replies."""
import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "staging/ru/group_turns_t495_context_pool.json"
SOURCE_SHA = "3e63012f2823ea1896e9d9612f68f19a3cf2fe6bbf2c8296fc98ac29fb18a024"
SOURCE_BLOB = "b881d145f634b6104c8538fef708d45162ef3125"
PREVIOUS = [
    ("group_turns_t492_context_pool.json", "427e870e1d243540f8d2264b32ae5b4ac678109a", 72),
    ("group_turns_t494_context_pool.json", "e1e142f743e10466d0bb87c77c161351d5db32df", 108),
]

def norm(s):
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", s).lower().replace("ё", "е")))

def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def extract(obj):
    if isinstance(obj, dict):
        for k,v in obj.items():
            if k in ("text", "answer", "reply", "response", "assistant_response", "response_text", "reply_text") and isinstance(v, str):
                yield v
            else:
                yield from extract(v)
    elif isinstance(obj, list):
        for val in obj:
            yield from extract(val)

class T495Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stage=json.loads(STAGE.read_text("utf-8"))
        cls.source=(ROOT/"packs/ru/dialogue.json").read_bytes()

    def test_source_lineage(self):
        self.assertEqual(hashlib.sha256(self.source).hexdigest(), SOURCE_SHA)
        self.assertEqual(blob(self.source), SOURCE_BLOB)
        man=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        self.assertEqual(next(p["sha256"] for p in man["packs"] if p["path"]=="packs/ru/dialogue.json"), SOURCE_SHA)
        self.assertFalse(self.stage["consumer_registered"])
        self.assertTrue(self.stage["constraints"]["requires_direct_address"])
        self.assertTrue(self.stage["constraints"]["read_only"])
        self.assertEqual(len(self.stage["previous_stages"]), 2)
        for info,(name,expected,num) in zip(self.stage["previous_stages"],PREVIOUS):
            raw=(STAGE.parent/name).read_bytes()
            self.assertEqual(info["git_blob"], expected)
            self.assertEqual(blob(raw), expected)
            doc=json.loads(raw)
            self.assertEqual(sum(len(e["replies"]) for e in doc["entries"]), num)

    def test_checkpoint_and_metadata(self):
        stage=self.stage
        self.assertEqual(stage["checkpoint"]["added_candidates"],120)
        self.assertEqual(stage["checkpoint"]["total_staged"],300)
        self.assertEqual(stage["checkpoint"]["remaining_total"],300)
        self.assertEqual(stage["checkpoint"]["finished_100"],0)
        self.assertEqual(len(stage["entries"]),6)
        self.assertEqual(len(set(e["intent_id"] for e in stage["entries"])),6)
        ids=set()
        for e in stage["entries"]:
            self.assertEqual(e["target"],100)
            self.assertEqual(e["baseline_including_previous_stages"],30)
            self.assertEqual(e["added_candidates"],20)
            self.assertEqual(len(e["replies"]),20)
            self.assertEqual(e["total_staged"],50)
            self.assertEqual(e["remaining"],50)
            for x in e["replies"]:
                self.assertNotIn(x["id"],ids)
                ids.add(x["id"])
                self.assertEqual(x["language"],"ru")
                self.assertEqual(x["audiences"],["all_ai_bots"])
                self.assertEqual(x["context"],"group_addressed")
                self.assertEqual(x["style"],"neutral")
                self.assertTrue(x["read_only"])
                self.assertGreater(len(x["context_note"]),30)
                self.assertGreater(len(x["avoid"]),100)
                self.assertFalse(re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|https?://|@[a-z0-9_]+)",x["text"]))
        self.assertEqual(len(ids),120)

    def test_global_unique_and_lexical_near_duplicates(self):
        # Fail on exact or >=0.78 token-Jaccard; semantic review is additional.
        known=set()
        for directory in (ROOT/"packs/ru",ROOT/"staging/ru"):
            for p in sorted(directory.glob("*.json")):
                if p==STAGE: continue
                obj=json.loads(p.read_text("utf-8"))
                known.update(norm(s) for s in extract(obj) if s.strip())
        source=json.loads(self.source)
        known.update(norm(x) for arr in source["reactions"].values() for x in arr)
        known.discard("")
        groups={}
        for text in known:
            tokens=frozenset(text.split())
            groups.setdefault(len(tokens),[]).append(tokens)
        for entry in self.stage["entries"]:
            for reply in entry["replies"]:
                k=norm(reply["text"])
                self.assertNotIn(k,known,reply["id"])
                tok=frozenset(k.split())
                for size in range(max(1,int(len(tok)*0.78)),int(len(tok)/0.78)+2):
                    for prev in groups.get(size,()):
                        common=len(tok & prev)
                        self.assertLess(common/(len(tok)+len(prev)-common),0.78,reply["id"])
                known.add(k)
                groups.setdefault(len(tok),[]).append(tok)

if __name__=="__main__":
    unittest.main()
