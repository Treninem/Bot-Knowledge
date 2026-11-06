"""T158/T170/T174: registered recovery and staged contextual continuation."""
import hashlib, json, re, unicodedata
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack
ROOT=Path(__file__).resolve().parents[1]
PATH="packs/ru/practical_recovery_qa.json"
def norm(s):
    s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in ("P","S") else c for c in s).split())
def main():
    raw=(ROOT/PATH).read_bytes()
    pack=json.loads(raw)
    mf=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(v["sha256"] for v in mf["packs"] if v["path"]==PATH)
    assert validate_qa_pack(pack)==24
    rows=pack["records"]
    assert len({r["id"] for r in rows})==24
    assert all(r["id"].startswith("bk_recovery_") and len(r["variants"])==8 for r in rows)
    assert all(r["audiences"]==["all_ai_bots"] and set(r["contexts"])=={"direct","private","group_addressed"} for r in rows)
    assert all(r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True} for r in rows)
    ans=[a for r in rows for a in [r["answer"],*r["variants"]]]
    assert len(ans)==216 and len({norm(a) for a in ans})==216
    assert not any(re.search(r"(?i)(ghp_|sk-|bot_token|chat_id|user_id|bearer\\s+)",a) for a in ans)

    # T168/T170: supplemental scoped candidates are NOT consumer registered.
    stage_path="staging/ru/recovery_t168_context_pool.json"
    stage=json.loads((ROOT/stage_path).read_text("utf-8"))
    assert stage["schema_version"]==1 and stage["language"]=="ru"
    assert stage["consumer_registered"] is False and stage["source_pack"]==PATH
    assert stage["stage_type"]=="supplemental_contextual_reply_pool"
    expected_blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    assert stage["source_pack_blob_sha"]==expected_blob
    assert stage["source_pack_manifest_sha256"]==hashlib.sha256(raw).hexdigest()
    assert stage_path not in {item["path"] for item in mf["packs"]}
    assert stage["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True}
    assert stage["audiences"]==["all_ai_bots"]
    checkpoint=stage["checkpoint"]
    assert checkpoint["base_main_sha"]=="309e5edd22f8ca4a6dcf59a4b2213a4c8696d36b"
    assert checkpoint["registered_count"]==216 and checkpoint["added_candidates"]==624
    assert checkpoint["latest_added"]==48 and checkpoint["latest_rejected"]==0
    assert checkpoint["per_intent_registered"]==9 and checkpoint["per_intent_staged"]==26
    assert checkpoint["per_intent_total"]==35 and checkpoint["partial_intents"]==24
    assert checkpoint["finished_100"]==0 and checkpoint["remaining_total"]==1560
    assert checkpoint["remaining_per_intent"]==65
    assert len(stage["entries"])==24
    candidates=[]; ids=set()
    for prior,entry in zip(rows,stage["entries"]):
        assert entry["intent_id"]==prior["id"] and entry["question"]==prior["question"]
        assert entry["registered_reply_count"]==9 and entry["staged_reply_count"]==26
        assert len(entry["replies"])==26
        assert sum(r["id"].startswith(entry["intent_id"]+"_t168_") for r in entry["replies"])==3
        assert sum(r["id"].startswith(entry["intent_id"]+"_t170_") for r in entry["replies"])==3
        assert sum(r["id"].startswith(entry["intent_id"]+"_t174_") for r in entry["replies"])==3
        assert sum(r["id"].startswith(entry["intent_id"]+"_t175_") for r in entry["replies"])==1
        assert sum(r["id"].startswith(entry["intent_id"]+"_t176_") for r in entry["replies"])==2
        assert sum(r["id"].startswith(entry["intent_id"]+"_t177_") for r in entry["replies"])==1
        assert sum(r["id"].startswith(entry["intent_id"]+"_t178_") for r in entry["replies"])==2
        assert sum(r["id"].startswith(entry["intent_id"]+"_t179_") for r in entry["replies"])==2
        assert sum(r["id"].startswith(entry["intent_id"]+"_t180_") for r in entry["replies"])==1
        assert sum(r["id"].startswith(entry["intent_id"]+"_t181_") for r in entry["replies"])==1
        assert sum(r["id"].startswith(entry["intent_id"]+"_t182_") for r in entry["replies"])==1
        assert sum(r["id"].startswith(entry["intent_id"]+"_t183_") for r in entry["replies"])==2
        assert sum(r["id"].startswith(entry["intent_id"]+"_t184_") for r in entry["replies"])==2
        assert sum(r["id"].startswith(entry["intent_id"]+"_t185_") for r in entry["replies"])==2
        for entry_reply in entry["replies"]:
            assert entry_reply["id"] not in ids and (entry_reply["id"].startswith(entry["intent_id"]+"_t168_") or entry_reply["id"].startswith(entry["intent_id"]+"_t170_") or entry_reply["id"].startswith(entry["intent_id"]+"_t174_") or entry_reply["id"].startswith(entry["intent_id"]+"_t175_") or entry_reply["id"].startswith(entry["intent_id"]+"_t176_") or entry_reply["id"].startswith(entry["intent_id"]+"_t177_") or entry_reply["id"].startswith(entry["intent_id"]+"_t178_") or entry_reply["id"].startswith(entry["intent_id"]+"_t179_") or entry_reply["id"].startswith(entry["intent_id"]+"_t180_") or entry_reply["id"].startswith(entry["intent_id"]+"_t181_") or entry_reply["id"].startswith(entry["intent_id"]+"_t182_") or entry_reply["id"].startswith(entry["intent_id"]+"_t183_") or entry_reply["id"].startswith(entry["intent_id"]+"_t184_") or entry_reply["id"].startswith(entry["intent_id"]+"_t185_"))
            ids.add(entry_reply["id"])
            assert entry_reply["language"]=="ru" and entry_reply["style"]=="neutral"
            assert entry_reply["context"] in {"direct","private","group_addressed"}
            assert entry_reply["audiences"]==["all_ai_bots"] and entry_reply["read_only"] is True
            assert entry_reply["context_note"].strip() and entry_reply["avoid"].strip()
            assert 0<len(entry_reply["text"])<=1600
            assert not re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})",entry_reply["text"])
            candidates.append(entry_reply["text"])
    assert len(candidates)==624 and len({norm(s) for s in ans+candidates})==792
    staged_keys={norm(s) for s in candidates}
    for item in mf["packs"]:
        path=item["path"]
        if path==PATH or not path.endswith("_qa.json"): continue
        other=json.loads((ROOT/path).read_text("utf-8"))
        for record in other.get("records",[]):
            assert not staged_keys.intersection(
                norm(s) for s in [record["answer"],*record.get("variants",[])]),path
    print("T184 PASS: 24 recovery intents, 216 registered + 624 staged; SHA, privacy and uniqueness")
if __name__=="__main__":main()
