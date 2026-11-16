"""v005 moderation language additions: immutable original variant prefix, QA and isolation."""
import hashlib, json, re, unicodedata, unittest
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack
from scripts.search_knowledge import KnowledgeSearch

ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/moderation_dialogue_fairness_qa.json"
EXPECTED_SHA="e2119d6d1883fb0bed641ca3734fa6348edd7389a246534848b098adafff01c7"
BASE_VARIANTS_SHA="c4e66f12eb75e1d84f9428df086d756d0410dad00eaa0c787607ed52bf07565d"
def normalize(s):
    s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
    return " ".join("".join(c if c.isalnum() else " " for c in s).split())
class FairnessV005(unittest.TestCase):
    def test_delta_and_provenance(self):
        raw=(ROOT/REL).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),EXPECTED_SHA)
        mf=json.loads((ROOT/"manifest.json").read_text("utf-8"))
        self.assertEqual(next(e["sha256"] for e in mf["packs"] if e["path"]==REL),EXPECTED_SHA)
        self.assertLess(len(raw),2*1024*1024)
        doc=json.loads(raw)
        self.assertEqual(doc["pack_version"],"2026.11.16.005")
        self.assertEqual(validate_qa_pack(doc),36)
        rows=doc["records"]
        self.assertEqual(len(rows),36)
        old=[r["variants"][:2] for r in rows]
        self.assertEqual(hashlib.sha256(json.dumps(old,ensure_ascii=False,separators=(",",":")).encode("utf-8")).hexdigest(),BASE_VARIANTS_SHA)
        self.assertEqual(sum(len(r["variants"])-2 for r in rows),108)
        self.assertTrue(all(len(r["variants"])==5 for r in rows))
        texts=[normalize(v) for r in rows for v in [r["answer"],*r["variants"]]]
        self.assertEqual(len(texts),len(set(texts)))
        for i,r in enumerate(rows,1):
            self.assertEqual(r["id"],f"modfair_t87_{i:03d}")
            self.assertEqual(r["audiences"],["chat_moderators","community_bots"])
            self.assertEqual(r["constraints"],{"read_only":True,"requires_direct_address":True,"no_personal_data":True})
            for v in r["variants"][2:]:
                self.assertTrue(len(v.strip())>25)
                self.assertFalse(re.search(r"(?<!\\w)@[A-Za-z0-9_]{4,}|(?<!\\d)\\d{10,}(?!\\d)",v))
    def test_scope(self):
        lookup=KnowledgeSearch()
        for row in json.loads((ROOT/REL).read_text("utf-8"))["records"]:
            self.assertTrue(any(r[0]==row["id"] for r in lookup.search(row["question"],audience="community_bots",limit=20)))
            self.assertFalse(any(r[0]==row["id"] for r in lookup.search(row["question"],audience="all_ai_bots",limit=20)))
if __name__=="__main__": unittest.main()
