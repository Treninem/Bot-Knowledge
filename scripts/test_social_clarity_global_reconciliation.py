"""Cross-catalog T488→T493/T496–T498 accounting. Never double count preexisting 100/100 intents."""
import hashlib,json,re,unicodedata,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OLD_BLOB="14a3abb9d24ff83c2ed2a2550116e89cea290954"
IDS=("clarify_previous","disagreement","unknown_fact","ambiguous")
def norm(s):return " ".join(re.findall(r"\w+",unicodedata.normalize("NFKC",s).lower().replace("ё","е")))
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
class GlobalProgress(unittest.TestCase):
 def test_global_not_newly_finished(self):
  pack=json.loads((ROOT/"packs/ru/dialogue.json").read_text("utf-8"))
  old_bytes=(ROOT/"staging/ru/scoped_repair_t488_context_pool.json").read_bytes()
  self.assertEqual(blob(old_bytes),OLD_BLOB)
  old=json.loads(old_bytes)
  self.assertEqual(old["checkpoint"]["total"],400)
  self.assertEqual(old["checkpoint"]["finished_100"],4)
  self.assertEqual({e["intent_id"] for e in old["entries"]},set(IDS))
  source=pack["scoped_repair_reactions"]["intents"]
  phases=[json.loads((ROOT/"staging/ru"/f"social_clarity_t{t}_context_pool.json").read_text("utf-8")) for t in (493,496,497,498)]
  baseline_sum=0;totals={};seen=set()
  for intent in IDS:
   baseline=len(pack["reactions"][intent])+sum(len(c["replies"]) for c in source[intent]["contexts"].values())
   baseline_sum+=baseline
   prior=next(e for e in old["entries"] if e["intent_id"]==intent)
   self.assertEqual(prior["baseline_including_previous_stage"]+len(prior["replies"]),100)
   incoming=[r for phase in phases for e in phase["entries"] if e["intent_id"]==intent for r in e["replies"]]
   for reply in incoming:
    key=(intent,norm(reply["text"]))
    self.assertNotIn(key,seen,reply["id"]);seen.add(key)
   totals[intent]=100+len(incoming)
  self.assertEqual(baseline_sum,69)
  self.assertEqual(totals,{"clarify_previous":198,"disagreement":199,"unknown_fact":199,"ambiguous":199})
  self.assertEqual(sum(totals.values()),795)
  cp=phases[-1]["checkpoint"]
  self.assertEqual(cp["newly_finished_global_intents"],0)
  self.assertEqual(cp["finished_100"],0)
  self.assertEqual(cp["finished_100_within_separate_stream"],4)
  self.assertEqual(cp["preexisting_complete_stage_blob_sha"],OLD_BLOB)
  self.assertEqual(cp["global_candidate_total_with_t488_t493_t496_t497_t498"],795)
  self.assertFalse(phases[-1]["consumer_registered"])
if __name__=="__main__":unittest.main()
