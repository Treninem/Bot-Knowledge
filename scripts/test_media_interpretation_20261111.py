"""Original synthetic media and attachment interpretation, staged/read-only QA."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "staging/ru"
FILES = [STAGING / "media_interpretation_20261111_context_pool.json"]
TOKEN = re.compile(r"[^\\W_]+", flags=re.UNICODE)

def norm(s: str) -> str:
    return " ".join(TOKEN.findall(unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")))

def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\\0" + raw).hexdigest()

class MediaInterpretation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stages = [json.loads(f.read_text("utf-8")) for f in FILES]
        cls.rows = [r for stage in cls.stages for entry in stage["entries"] for r in entry["replies"]]

    def test_source_and_manifest_unchanged(self):
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        sha_by_path = {p["path"]: p["sha256"] for p in manifest["packs"]}
        for stage in self.stages:
            source = stage["source_pack"]
            raw = (ROOT / source).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), stage["source_pack_manifest_sha256"])
            self.assertEqual(git_blob(raw), stage["source_pack_blob_sha"])
            self.assertEqual(sha_by_path[source], stage["source_pack_manifest_sha256"])
        self.assertTrue(all(str(p.relative_to(ROOT)) not in sha_by_path for p in FILES))

    def test_structure_and_stable_intents(self):
        names = {e["intent_id"] for e in self.stages[0]["entries"]}
        self.assertEqual(len(names), 10)
        for i,(stage,path) in enumerate(zip(self.stages, FILES)):
            self.assertEqual(stage["schema_version"], 1)
            self.assertEqual(stage["stage_type"], "supplemental_contextual_reply_pool")
            self.assertFalse(stage["consumer_registered"])
            self.assertEqual(stage["language"], "ru")
            self.assertEqual(stage["audiences"], ["all_ai_bots"])
            for k in ("read_only", "requires_direct_address", "no_personal_data",
                      "no_sanctions", "requires_context_match"):
                self.assertIs(stage["constraints"][k], True)
            if i:
                self.assertEqual(stage["parent_stage"], str(FILES[i-1].relative_to(ROOT)))
                self.assertEqual(stage["parent_stage_blob_sha"], git_blob(FILES[i-1].read_bytes()))
            cp = stage["checkpoint"]
            self.assertEqual(cp["added_candidates"], 100)
            self.assertEqual(cp["cumulative_candidates"], (i+1)*100)
            self.assertEqual(cp["prior_candidates"], i*100)
            self.assertEqual(cp["processed_intents"], 10)
            self.assertEqual(cp["remaining_total"], 900-i*100)
            self.assertEqual({e["intent_id"] for e in stage["entries"]}, names)
            for entry in stage["entries"]:
                self.assertEqual(len(entry["replies"]), 10)
                self.assertEqual(entry["prior_for_stable_id"], i*10)
                self.assertEqual(entry["total_staged"], (i+1)*10)
                self.assertEqual(entry["remaining"], 90-i*10)
                self.assertEqual(entry["target"], 100)
                for n,r in enumerate(entry["replies"],start=i*10+1):
                    self.assertEqual(r["id"], f'{entry["intent_id"]}_{n:02d}')
                    self.assertEqual(r["language"], "ru")
                    self.assertEqual(r["audiences"], ["all_ai_bots"])
                    self.assertEqual(r["context"], "direct")
                    self.assertIs(r["read_only"], True)
                    self.assertGreaterEqual(len(r["text"].strip()), 45)
                    self.assertGreaterEqual(len(r["context_note"].strip()), 18)
                    self.assertIn("не применять санкции", r["avoid"])

    def test_unique_and_lexical_scope(self):
        count = len(FILES)*100
        self.assertEqual(len(self.rows), count)
        for key in ("id", "text", "context_note"):
            strings = [r[key] if key == "id" else norm(r[key]) for r in self.rows]
            self.assertEqual(len(set(strings)), count, key)
        texts = [set(norm(r["text"]).split()) for r in self.rows]
        for i,a in enumerate(texts):
            for b in texts[i+1:]:
                self.assertLess(len(a & b) / len(a | b), 0.80)

    def test_registered_cross_corpus_exact(self):
        manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
        registered = set()
        for p in manifest["packs"]:
            data = json.loads((ROOT / p["path"]).read_text("utf-8"))
            if isinstance(data, dict):
                for rec in data.get("records", []):
                    if not isinstance(rec, dict):
                        continue
                    answer = rec.get("answer")
                    if isinstance(answer, str):
                        registered.add(norm(answer))
                    variants = rec.get("variants", [])
                    if isinstance(variants, list):
                        registered.update(norm(s) for s in variants if isinstance(s, str))
        self.assertTrue(registered)
        for r in self.rows:
            self.assertNotIn(norm(r["text"]), registered, r["id"])

    def test_privacy_and_no_actions(self):
        for r in self.rows:
            s = r["text"]
            self.assertNotRegex(s, r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,}")
            self.assertNotRegex(s, r"(?:\\+?\\d[ -]?){11,}")
            self.assertNotRegex(s, r"(?i)(?:бот|я) (?:забанил|замутил|уже отправил|изменил настройки)")
            self.assertNotIn("token", s.casefold())

if __name__ == "__main__":
    unittest.main()
