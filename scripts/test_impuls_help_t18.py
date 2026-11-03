"""T18 fact-scoped ImPULS help and source-matched natural queries."""
import hashlib,json,re
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
IDS=["help_t18_conflict_signal_readout","help_t18_conflict_hotspot_meaning","help_t18_conflict_shield_guide","help_t18_after_storm_review","help_t18_conflict_alarm_context","help_t18_local_reason_categories","help_t18_combine_similar_reasons","help_t18_training_hint_correction","help_t18_local_learning_not_global_rules","help_t18_learning_vs_manual_review","help_t18_reason_vs_rule_text","help_t18_guide_vs_diagnostics","help_t18_first_run_vs_release","help_t18_release_center_vs_bundle","help_t18_published_guide_vs_live_menu","help_t18_event_vs_rating","help_t18_contribution_vs_season","help_t18_weekly_gift_vs_regular_gift","help_t18_visual_presets_and_roles","help_t18_pulse_boost_vs_stars","help_t18_inventory_item_not_purchase","help_t18_moderation_history_vs_learning","help_t18_public_help_vs_private_panel","help_t18_conflict_pause_vs_punish","help_t18_category_not_sanction","help_t18_diagnostics_no_user_blame"]
def norm(s):
    return re.sub(r"[^\w]+"," ",s.casefold().replace("ё","е")).strip()
def main():
    path="packs/ru/impuls_help_qa.json"
    raw=(ROOT/path).read_bytes()
    pack=json.loads(raw)
    m=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(e["sha256"] for e in m["packs"] if e["path"]==path)
    assert len(raw)<1024*1024 and validate_qa_pack(pack)==len(pack["records"])
    selected=[r for r in pack["records"] if r["id"].startswith("help_t18_")]
    assert len(selected)==len(IDS) and {r["id"] for r in selected}==set(IDS)
    index=KnowledgeSearch()
    seen=set()
    for r in selected:
        assert r["audiences"]==["impuls"] and r["contexts"]==["direct","private","group_addressed"]
        assert r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True}
        assert len(r["aliases"])==len(r["variants"])==2
        for phrase in [r["question"],*r["aliases"]]:
            key=norm(phrase)
            assert key not in seen
            seen.add(key)
            assert any(hit[0]==r["id"] for hit in index.search(phrase,audience="impuls",limit=20)), (r["id"],phrase)
            assert all(hit[0]!=r["id"] for hit in index.search(phrase,audience="all_ai_bots",limit=20))
    print(f"T18_IMPULS_HELP_OK questions={len(selected)} answers={len(selected)*3} searches={len(seen)}")
if __name__=="__main__":main()
