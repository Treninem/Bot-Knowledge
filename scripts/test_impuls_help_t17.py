"""T17 verified synthetic ImPULS guidance, safe scopes and local retrieval."""
from __future__ import annotations
import hashlib, json, re
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack
from scripts.search_knowledge import KnowledgeSearch
ROOT=Path(__file__).resolve().parents[1]
TARGET="packs/ru/impuls_help_qa.json"
IDS=["help_t17_safe_first_start","help_t17_rules_draft_review","help_t17_rule_change_announcement","help_t17_moderation_preview","help_t17_clear_not_dry_run","help_t17_reply_vs_permissions","help_t17_guide_without_owner_menu","help_t17_two_changes_order","help_t17_diagnostics_synthetic_example","help_t17_checklist_vs_problem","help_t17_archive_not_backup","help_t17_release_notes_not_enabled","help_t17_visual_preview_without_apply","help_t17_hub_vs_leaders","help_t17_season_journal_vs_history","help_t17_weekly_gift_meaning","help_t17_inventory_vs_showcase","help_t17_shop_item_no_admin","help_t17_stars_unconfirmed_purchase","help_t17_draw_win_vs_delivery","help_t17_game_roles_not_chat_rights","help_t17_pulse_same_word","help_t17_dm_settings_not_public","help_t17_rhythm_not_personal_surveillance","help_t17_game_and_report_separate","help_t17_gift_without_public_identity","help_t17_backup_plan_if_github_down"]
def normalize(s):
    return re.sub(r"[^\w]+", " ", s.casefold().replace("ё", "е")).strip()
def main():
    raw=(ROOT/TARGET).read_bytes()
    pack=json.loads(raw)
    manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    entry=next(x for x in manifest["packs"] if x["path"]==TARGET)
    if hashlib.sha256(raw).hexdigest()!=entry["sha256"]: raise ValueError("T17 manifest hash mismatch")
    if len(raw)>1024*1024: raise ValueError("T17 qa.v1 size exceeded")
    if validate_qa_pack(pack)!=len(pack["records"]): raise ValueError("T17 invalid schema")
    chosen=[r for r in pack["records"] if r["id"].startswith("help_t17_")]
    if len(chosen)!=len(IDS) or set(x["id"] for x in chosen)!=set(IDS): raise ValueError("T17 incomplete set")
    index=KnowledgeSearch()
    seen=set()
    for row in chosen:
        if row["audiences"]!=["impuls"] or row["contexts"]!=["direct","private","group_addressed"]: raise ValueError("scope")
        if row["constraints"]!={"read_only":True,"requires_direct_address":True,"no_personal_data":True}: raise ValueError("constraints")
        if len(row["aliases"])!=2 or len(row["variants"])!=2: raise ValueError("variants")
        for phrase in [row["question"],*row["aliases"]]:
            key=normalize(phrase)
            if key in seen: raise ValueError("duplicate query")
            seen.add(key)
            results=index.search(phrase,audience="impuls",limit=40)
            if not any(hit[0]==row["id"] for hit in results): raise ValueError(f"not found {row['id']}: {phrase}")
            other=index.search(phrase,audience="all_ai_bots",limit=40)
            if any(hit[0]==row["id"] for hit in other): raise ValueError("audience leak")
    print(f"T17_IMPULS_HELP_OK records={len(chosen)} replies={len(chosen)*3} searches={len(seen)}")
if __name__=="__main__": main()
