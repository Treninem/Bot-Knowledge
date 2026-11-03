from __future__ import annotations
import hashlib, json, re, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PREFIXES = {"dialogue_help_qa.json": "dlg_t68_", "english_dialogues.json": "en_t68_", "social_dialogues.json": "talk_t68_"}
def normal(s):
    return re.sub(r"[^a-zа-я0-9]+", " ", s.lower().replace("ё","е")).strip()
class T68(unittest.TestCase):
    def test_new_contexts_and_sha(self):
        manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        for filename, prefix in PREFIXES.items():
            path=ROOT/"packs"/"ru"/filename
            data=json.loads(path.read_text(encoding="utf-8"))
            payload=path.read_bytes()
            self.assertLess(len(payload),2*1024*1024)
            expected=next(x["sha256"] for x in manifest["packs"] if x["path"]=="packs/ru/"+filename)
            self.assertEqual(hashlib.sha256(payload).hexdigest(), expected)
            records=data.get("records",data.get("cases"))
            self.assertEqual(len({x["id"] for x in records}),len(records))
            current=[x for x in records if x["id"].startswith(prefix)]
            self.assertGreaterEqual(len(current), 15)
            key="answer" if "records" in data else "response"
            answers=[x[key] for x in current]
            self.assertEqual(len({normal(x) for x in answers}),len(answers))
            for x in current:
                self.assertEqual(x["audiences"],["all_ai_bots"])
                if filename=="social_dialogues.json":
                    self.assertIn(x["kind"], {"conversation","support","humor","creative","congratulations","profanity"})
                self.assertNotIn("sanction",x)
                self.assertTrue(x[key].strip())
                if filename=="dialogue_help_qa.json":
                    self.assertEqual(x["contexts"],["direct","private","group_addressed"])
                    self.assertTrue(x["constraints"]["read_only"])
                    self.assertEqual(len(x["variants"]),2)
                    self.assertEqual(len(x["aliases"]),2)
                else:
                    self.assertTrue(x["avoid"].strip())
                    self.assertTrue((x.get("context") or x.get("meaning_ru")).strip())
if __name__ == "__main__":
    unittest.main()
