#!/usr/bin/env python3
"""Verify previously accepted 113 v013 answers after lossless v014 formatting."""
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path
from validate_pack import evaluate_snapshot_budget, MAX_CONSUMER_SNAPSHOT_BYTES
from validate_qa_v1 import validate_qa_manifest, MAX_QA_PACK_BYTES
ROOT = Path(__file__).resolve().parents[1]
BASE = "f5804f9fc08dda7df63029f30ab6530c73517302"
PATH = "packs/ru/impuls_help_qa.json"
VERSION = "2026.11.16.014"
EXPECTED_HASH = "966d0362ca71ea7ff4d538526a7b5902023ec933ab79b6bdb2022f78138356bc"
CHANGED = set(["access_claim_via_screenshot","access_read_link_not_modify","conversation_disagree_without_justifying","conversation_abbreviation_multiple_meanings","knowledge_partial_download","knowledge_audience_not_global","knowledge_unmerged_pr_not_ready","knowledge_manifest_pack_mismatch","knowledge_ci_not_live_test","knowledge_source_not_approval","knowledge_failed_update_fallback","knowledge_candidate_privacy","privacy_blur_screenshot","privacy_secret_in_url","privacy_forwarded_private_text","privacy_small_group_summary","pulses_unverified_points","warn_meaning","warn_vs_mute","warn_vs_ban","warn_why_no_reason","warn_count_unknown","warn_limit_unknown","warn_ban_threshold","warn_expiry","warn_enabled","warn_first_offense","warn_duplicate_notice","warn_delayed_notice","warn_issued_by_whom","warn_private_count","warn_chat_isolation","warn_old_status","warn_deleted_notice","warn_no_screenshot","warn_private_appeal","warn_appeal_pending","warn_apology_effect","warn_admin_cannot_see","warn_cancel_unknown","warn_overturned","warn_private_chat_scope","warn_state_ack","warn_updated_policy","warn_repeat_complaint","warn_moderator_rights","warn_which_section","warn_bk_section_fallback","warn_hypothetical","warn_two_rules","warn_public_ranking","warn_no_logs","warn_emotional_support","warn_minimal_question","warn_status_different","warn_explain_rule","warn_authority_claim","report_start","report_not_ban","report_not_ticket","report_current_status","report_group_scope","report_duplicate","report_no_target","report_unknown_author","report_no_private_chat","report_without_proof","report_not_vote","report_technical_vs_rule","report_retracted","report_false_accusation","report_against_moderator","report_after_exit","report_reply_is_not_resolution","report_wrong_chat","report_screenshot_unsafe","report_same_word_multiple_meanings","rule_recommendation","rule_not_published","rule_request_version","rule_pinned_conflict","rule_chat_claim","rule_suggestion","rule_exception_one_time","rule_exception_person","rule_discretion","rule_inconsistent_enforcement","rule_chat_dm","rule_channel_discussion","rule_topic_scope","rule_time_zone","rule_vague_spam","rule_absent_link_ban","rule_contextual_quote","rule_no_sanction_list","rule_first_time","rule_unavailable_in_outage","rule_chat_copy","rule_screenshot_old","rule_change_request_no_rights","rule_bk_not_override","rule_no_hidden_punishment","rule_explicit_exception","rule_moderator_statement","rule_other_platform","rule_joke_permission","rule_proposal_vs_active","rule_untrusted_forward","rule_no_action_on_explanation","rule_temporary_restriction","rule_human_review_edge","notice_under_review","deleted_without_warning"])

def norm(text):
    return " ".join(re.sub(r"[^\w]+"," ",text.casefold().replace("ё","е")).split())

class NewContextAnswers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=subprocess.check_output(["git","show","a3d1fc914e9e4a4991a2e91aaa5481e11a5a58c8:"+PATH],cwd=ROOT)
        cls.pack=json.loads(cls.raw)
        cls.old=json.loads(subprocess.check_output(["git","show",f"{BASE}:{PATH}"],cwd=ROOT))
        cls.manifest_bytes=subprocess.check_output(["git","show","a3d1fc914e9e4a4991a2e91aaa5481e11a5a58c8:manifest.json"],cwd=ROOT)
        cls.manifest=json.loads(cls.manifest_bytes)

    def test_bytes_manifest_version_budget(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),EXPECTED_HASH)
        self.assertEqual(self.pack["pack_version"],VERSION)
        self.assertEqual(self.manifest["knowledge_version"],VERSION)
        self.assertEqual(next(p["sha256"] for p in self.manifest["packs"] if p["path"]==PATH),EXPECTED_HASH)
        self.assertLessEqual(len(self.raw),MAX_QA_PACK_BYTES)
        total,remaining=evaluate_snapshot_budget(len(self.manifest_bytes),[(ROOT/p["path"]).stat().st_size for p in json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))["packs"]])
        self.assertLessEqual(total,MAX_CONSUMER_SNAPSHOT_BYTES)
        self.assertGreaterEqual(remaining,0)
        self.assertEqual(validate_qa_manifest(ROOT),[])

    def test_exact_delta_and_context(self):
        a={r["id"]:r for r in self.old["records"]}
        b={r["id"]:r for r in self.pack["records"]}
        self.assertEqual(len(a),869)
        self.assertEqual(set(a),set(b))
        self.assertEqual({k:v for k,v in self.old.items() if k not in ("records","pack_version")},{k:v for k,v in self.pack.items() if k not in ("records","pack_version")})
        changes=set()
        for k in a:
            old,new=a[k],b[k]
            self.assertEqual({x:y for x,y in old.items() if x!="variants"},{x:y for x,y in new.items() if x!="variants"},k)
            self.assertEqual(new["variants"][:len(old["variants"])],old["variants"],k)
            difference=new["variants"][len(old["variants"]):]
            self.assertEqual(len(difference),1 if k in CHANGED else 0,k)
            if difference: changes.add(k)
            self.assertLessEqual(len(new["variants"]),8,k)
            forms=[norm(x) for x in [new["answer"],*new["variants"]]]
            self.assertEqual(len(forms),len(set(forms)),k)
            for text in difference:
                self.assertTrue(65<=len(text)<=1600,k)
                self.assertFalse(re.search(r"https?://|t\.me/|@[A-Za-z0-9_]|[0-9]{10,}",text,re.I),k)
        self.assertEqual(changes,CHANGED)
        self.assertEqual(len(CHANGED), 113)
        self.assertEqual(sum(len(r["variants"]) for r in b.values()),2278)

    def test_no_publish_or_sanction_capabilities(self):
        self.assertEqual(self.pack["catalog"]["audiences"],["impuls"])
        self.assertEqual(self.pack["catalog"]["constraints"],{"read_only":True,"requires_direct_address":True,"no_personal_data":True})
        self.assertFalse(any(x["path"].startswith("staging/") for x in self.manifest["packs"]))

    def test_deferred_originals_preserved_and_disjoint(self):
        deferred = json.loads((ROOT/"staging/ru/impuls_qa_v1_warnings_deferred_20261116.json").read_text(encoding="utf-8"))
        self.assertFalse(deferred["consumer_registered"])
        self.assertEqual(deferred["source_pr"],671)
        self.assertEqual(deferred["base_main_sha"], BASE)
        self.assertEqual(deferred["registered_count_candidate"], 113)
        self.assertEqual(deferred["deferred_count"], 17)
        keys=[x["intent_id"] for x in deferred["deferred_entries"]]
        self.assertEqual(len(keys),len(set(keys)))
        self.assertFalse(set(keys)&CHANGED)
        self.assertEqual(len(keys),17)
        self.assertTrue(all(x["read_only"] and x["editorial_status"]=="pending_independent_review" for x in deferred["deferred_entries"]))
        self.assertFalse(any(re.search(r"https?://|t\\.me/|@[A-Za-z0-9_]|[0-9]{10,}",x["answer"],re.I) for x in deferred["deferred_entries"]))

if __name__=="__main__":
    unittest.main()
