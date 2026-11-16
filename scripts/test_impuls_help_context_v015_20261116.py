#!/usr/bin/env python3
"""Verify 17 preserved v013 replies and 84 new replies on compact v014 lineage."""
import hashlib, json, re, subprocess, unittest
from pathlib import Path
from validate_pack import evaluate_snapshot_budget, MAX_CONSUMER_SNAPSHOT_BYTES
from validate_qa_v1 import validate_qa_manifest
ROOT = Path(__file__).resolve().parents[1]
SRC = "a3d1fc914e9e4a4991a2e91aaa5481e11a5a58c8"
PACK = "packs/ru/impuls_help_qa.json"
DEFERRED = "staging/ru/impuls_qa_v1_warnings_deferred_20261116.json"
HASH = "2520d36e43b44ca3fa143d85079656fd2d72b90fe0ff8f2452a639b1407c6cc5"
DEFERRED_IDS = set(["conversation_first_answer_then_detail","conversation_quote_not_new_topic","conversation_emoji_not_authorization","conversation_audio_uncertain_words","conversation_one_constraint_changed","conversation_timezone_in_schedule","help_issue_one_device","help_network_vs_permission","help_reinstall_data_risk","help_check_after_error","help_time_order_unsure","help_accessible_instructions","help_cropped_screen_limit","help_one_change_at_time","game_disconnect_fairness","game_tie_rule_before_start","raffle_multiple_accounts_eligibility"])
ALL_CHANGED_IDS = set(["conversation_first_answer_then_detail","conversation_quote_not_new_topic","conversation_emoji_not_authorization","conversation_audio_uncertain_words","conversation_one_constraint_changed","conversation_timezone_in_schedule","help_issue_one_device","help_network_vs_permission","help_reinstall_data_risk","help_check_after_error","help_time_order_unsure","help_accessible_instructions","help_cropped_screen_limit","help_one_change_at_time","game_disconnect_fairness","game_tie_rule_before_start","raffle_multiple_accounts_eligibility","report_problem","game_help","reply_more","chat_selection","conversation_forget","reply_off_topic","game_switch_rights","game_start_diagnosis","conversation_group_interrupt","conversation_topic_thread","conversation_missing_attachment","conversation_language_ambiguity","help_no_action_receipt","help_missing_permission_scope","help_partial_outage","help_nonexistent_button","help_no_tool_access","help_offline_cached_reply","help_restart_not_proof","conversation_grief_boundaries","conversation_sarcastic_thanks","conversation_correction_without_shame","game_simultaneous_turns","conversation_instruction_conflict","help_report_without_logs"])

def norm(s):
    return " ".join(re.sub(r"[^\w]+"," ",s.casefold().replace("ё","е")).split())

class ContextExtensionV015(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=(ROOT/PACK).read_bytes()
        cls.cur=json.loads(cls.raw)
        cls.old=json.loads(subprocess.check_output(["git","show",f"{SRC}:{PACK}"],cwd=ROOT))
        cls.deferral=json.loads((ROOT/DEFERRED).read_text(encoding="utf-8"))
        cls.manifest_raw=(ROOT/"manifest.json").read_bytes()
        cls.manifest=json.loads(cls.manifest_raw)

    def test_exact_delta(self):
        original={r["id"]:r for r in self.old["records"]}
        latest={r["id"]:r for r in self.cur["records"]}
        self.assertEqual(set(original),set(latest))
        self.assertEqual(len(latest),869)
        self.assertEqual(self.old["pack_version"],"2026.11.16.014")
        self.assertEqual(self.cur["pack_version"],"2026.11.16.015")
        for k in set(self.old)-{"records","pack_version"}:
            self.assertEqual(self.old[k],self.cur[k],k)
        deferred={x["intent_id"]:x["answer"] for x in self.deferral["deferred_entries"]}
        self.assertEqual(set(deferred),DEFERRED_IDS)
        touched=set()
        normalized=set(norm(t) for r in original.values() for t in [r["answer"],*r["variants"]])
        promoted=authored=0
        for k,old in original.items():
            new=latest[k]
            for field in set(old)-{"variants"}:
                self.assertEqual(old[field],new[field],k)
            self.assertEqual(new["variants"][:len(old["variants"])],old["variants"],k)
            extra=new["variants"][len(old["variants"]):]
            self.assertEqual(len(extra),(3 if k in DEFERRED_IDS else 2) if k in ALL_CHANGED_IDS else 0,k)
            self.assertLessEqual(len(new["variants"]),8,k)
            for s in extra:
                self.assertTrue(s.strip() and len(s)<1600,k)
                self.assertFalse(re.search(r"https?://|t\.me/|@[a-z_]|[0-9]{10,}",s,re.I),k)
                self.assertNotIn(norm(s),normalized,k)
                normalized.add(norm(s))
            if extra:
                touched.add(k)
                if k in DEFERRED_IDS:
                    self.assertEqual(extra[0],deferred[k],k)
                    promoted+=1
                authored+=len(extra)-(1 if k in DEFERRED_IDS else 0)
        self.assertEqual(touched,ALL_CHANGED_IDS)
        self.assertEqual(len(touched),42)
        self.assertEqual(promoted,17)
        self.assertEqual(authored,84)
        self.assertEqual(sum(len(r["variants"]) for r in latest.values()),2379)

    def test_actual_bytes_manifest_and_budget(self):
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),HASH)
        self.assertEqual(self.manifest["knowledge_version"],"2026.11.16.015")
        self.assertEqual(next(p["sha256"] for p in self.manifest["packs"] if p["path"]==PACK),HASH)
        total,remaining=evaluate_snapshot_budget(len(self.manifest_raw),[(ROOT/p["path"]).stat().st_size for p in self.manifest["packs"]])
        self.assertLessEqual(total,MAX_CONSUMER_SNAPSHOT_BYTES)
        self.assertGreaterEqual(remaining,0)
        self.assertEqual(validate_qa_manifest(ROOT),[])

if __name__=="__main__":
    unittest.main()
