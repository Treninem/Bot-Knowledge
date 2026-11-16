#!/usr/bin/env python3
"""Check exact v016 dialogue-help expansion against published v015 source."""
import hashlib, json, re, subprocess, unittest
from pathlib import Path
from validate_pack import evaluate_snapshot_budget, MAX_CONSUMER_SNAPSHOT_BYTES
from validate_qa_v1 import validate_qa_manifest
ROOT=Path(__file__).resolve().parents[1]
BASE="57d28d2640ce3c32f74964f52121555836b562ea"
PACK="packs/ru/dialogue_help_qa.json"
EXPECTED="26f3f9de5546b694294cfd113fe1603745fd62aa6b2e7acd50dd258c8a41bec3"
IDS=["dlg_greet_after_pause","dlg_bye_without_pressure","dlg_resume_topic_after_aside","dlg_ambiguous_not_that","dlg_correct_only_number","dlg_t7_group_reply_only_direct","dlg_t7_group_answer_one_person","dlg_t7_group_sensitive_detail","dlg_t7_group_conflicting_requests","dlg_t7_group_context_without_names","dlg_t7_ack_without_restart","dlg_t7_topic_switch_explicit","dlg_t7_cancel_previous_choice","dlg_t7_one_word_refusal","dlg_t7_asked_for_example_only","dlg_t7_asked_for_steps_only","dlg_t7_two_alternatives_tradeoff","dlg_t7_yes_no_with_exception","dlg_t7_what_is_missing_single","dlg_t7_ambiguous_units","dlg_t7_approximation_labels","dlg_t7_current_vs_static","dlg_t7_image_unclear_detail","dlg_t7_quoted_instruction_not_command","dlg_t7_embedded_untrusted_demand","dlg_t7_conflicting_user_constraints","dlg_t7_different_asks_same_message","dlg_t7_new_info_changes_conclusion","dlg_t7_repeat_error_apology","dlg_t7_frustration_no_defensive","dlg_t7_feedback_too_generic","dlg_t7_feedback_keep_core","dlg_t7_silent_no_action","dlg_t7_interest_without_interrogation","dlg_t7_opinion_vs_fact","dlg_t7_constructive_disagreement","dlg_t7_tone_joke_on_request","dlg_t7_joke_failed_repair","dlg_t7_creative_no_real_case","dlg_t7_harmful_generalization","dlg_t7_private_third_party","dlg_t7_rules_not_all_same","dlg_t7_warning_without_logs","dlg_t7_moderation_quoted_text","dlg_t7_unverified_permissions","dlg_t7_live_vs_readme","dlg_t7_status_without_exaggeration","dlg_t7_unknown_reference","dlg_t7_safety_vs_style","dlg_t7_stop_when_answered"]
def norm(s):
    return " ".join(re.sub(r"[^\w]+", " ", s.casefold().replace("ё","е")).split())
class DialogueHelpV016(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.newraw=(ROOT/PACK).read_bytes()
        cls.cur=json.loads(cls.newraw)
        cls.old=json.loads(subprocess.check_output(["git","show",f"{BASE}:{PACK}"],cwd=ROOT))
        cls.man=json.loads((ROOT/"manifest.json").read_text(encoding="utf8"))
    def test_lossless_and_exact_delta(self):
        self.assertEqual(len(self.cur["records"]),len(self.old["records"]))
        before={r["id"]:r for r in self.old["records"]}
        after={r["id"]:r for r in self.cur["records"]}
        self.assertEqual(set(before),set(after))
        self.assertEqual({k:v for k,v in self.cur.items() if k not in ("records","pack_version")},{k:v for k,v in self.old.items() if k not in ("records","pack_version")})
        changed=[];added=[]
        for ident,a in after.items():
            b=before[ident]
            self.assertEqual({k:v for k,v in a.items() if k!="variants"},{k:v for k,v in b.items() if k!="variants"})
            self.assertEqual(a["variants"][:len(b["variants"])],b["variants"])
            extension=a["variants"][len(b["variants"]):]
            self.assertEqual(len(extension),2 if ident in IDS else 0)
            self.assertLessEqual(len(a["variants"]),8)
            if extension:changed.append(ident);added+=extension
        self.assertEqual(set(changed),set(IDS))
        self.assertEqual(len(added),100)
        alltexts=[s for r in after.values() for s in [r["answer"],*r["variants"]]]
        self.assertEqual(len(alltexts),len(set(map(norm,alltexts))))
        for s in added:
            self.assertFalse(re.search(r"https?://|t\.me/|@[a-z0-9_]{3,}|\d{10,}",s,re.I))
        self.assertEqual(sum(len(r["variants"]) for r in after.values())-sum(len(r["variants"]) for r in before.values()),100)
    def test_real_hash_and_budget(self):
        self.assertEqual(hashlib.sha256(self.newraw).hexdigest(),EXPECTED)
        self.assertEqual(self.man["knowledge_version"],"2026.11.16.016")
        self.assertEqual(next(p["sha256"] for p in self.man["packs"] if p["path"]==PACK),EXPECTED)
        mbytes=(ROOT/"manifest.json").read_bytes()
        total,remain=evaluate_snapshot_budget(len(mbytes),[(ROOT/p["path"]).stat().st_size for p in self.man["packs"]])
        self.assertLessEqual(total,MAX_CONSUMER_SNAPSHOT_BYTES)
        self.assertGreaterEqual(remain,0)
        self.assertEqual(validate_qa_manifest(ROOT),[])
if __name__=="__main__":
    unittest.main()
