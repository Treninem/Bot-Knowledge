"""T160/T171/T174: response-boundary QA, staged continuation and scope."""
import hashlib, json, re, unicodedata
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question
ROOT=Path(__file__).resolve().parents[1]
PATH="packs/ru/response_boundaries_qa.json"
def norm(s):
 s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
 return " ".join("".join(" " if unicodedata.category(c)[0] in ("P","S") else c for c in s).split())
def main():
 raw=(ROOT/PATH).read_bytes(); pack=json.loads(raw)
 manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
 assert hashlib.sha256(raw).hexdigest()==next(x["sha256"] for x in manifest["packs"] if x["path"]==PATH)
 assert validate_qa_pack(pack)==31
 rows=pack["records"]
 assert len({r["id"] for r in rows})==31
 assert all(len(r["variants"])==8 for r in rows)
 assert all(r["audiences"]==["all_ai_bots"] and set(r["contexts"])=={"direct","private","group_addressed"} for r in rows)
 assert all(r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True} for r in rows)
 assert all(r["source"].endswith("/AGENTS.md") for r in rows)
 replies=[s for r in rows for s in [r["answer"],*r["variants"]]]
 assert len(replies)==279 and len({norm(s) for s in replies})==279
 assert not any(re.search(r"(?i)(ghp_|sk-|bot_token|chat_id|user_id|bearer\\s+)",s) for s in replies)
 assert all(normalize_question(r["question"]) for r in rows)

 # Registered qa.v1 must be discoverable through the exact, SHA-checked local index.
 from scripts.search_knowledge import KnowledgeSearch
 index=KnowledgeSearch(ROOT)
 for row in rows:
  for ctx in ("direct","private","group_addressed"):
   hits=index.search(row["question"],audience="all_ai_bots",limit=20,context=ctx)
   assert any(h[0]==row["id"] and h[1]==PATH for h in hits), (row["id"],ctx)
 # Also enforce no cross-pack exact duplicates in the current manifest snapshot.
 qset={normalize_question(r["question"]) for r in rows}
 aset={norm(s) for s in replies}
 for entry in manifest["packs"]:
  p=entry["path"]
  if p==PATH or not p.endswith("_qa.json"):
   continue
  existing=json.loads((ROOT/p).read_text("utf-8"))
  for other in existing.get("records",[]):
   assert not qset.intersection(normalize_question(s) for s in (other["question"],*other.get("aliases",[]))),p
   assert not aset.intersection(norm(s) for s in (other["answer"],*other.get("variants",[]))),p

 # T167/T171: supplemental context pool, not a consumer pack.
 stage_path="staging/ru/boundaries_t167_context_pool.json"
 stage=json.loads((ROOT/stage_path).read_text("utf-8"))
 assert stage["schema_version"]==1 and stage["stage_type"]=="supplemental_contextual_reply_pool"
 assert stage["consumer_registered"] is False and stage["source_pack"]==PATH
 gitblob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
 assert stage["source_pack_blob_sha"]==gitblob
 assert stage["source_pack_manifest_sha256"]==hashlib.sha256(raw).hexdigest()
 assert stage_path not in {x["path"] for x in manifest["packs"]}
 assert stage["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True}
 assert stage["audiences"]==["all_ai_bots"] and stage["language"]=="ru"
 cp=stage["checkpoint"]
 assert cp["base_main_sha"]=="309e5edd22f8ca4a6dcf59a4b2213a4c8696d36b"
 assert cp["registered_count"]==279 and cp["added_candidates"]==744
 assert cp["latest_added"]==62 and cp["latest_rejected"]==0
 assert cp["per_intent_total"]==33 and cp["remaining_per_intent"]==67
 assert cp["partial_intents"]==31 and cp["finished_100"]==0 and cp["remaining_total"]==2077
 assert len(stage["entries"])==31
 extra=[]; stage_ids=set()
 for original,entry in zip(rows,stage["entries"]):
  assert entry["intent_id"]==original["id"] and entry["question"]==original["question"]
  assert entry["registered_reply_count"]==9 and entry["staged_reply_count"]==24
  assert len(entry["replies"])==24
  assert sum(r["id"].startswith(entry["intent_id"]+"_t167_") for r in entry["replies"])==3
  assert sum(r["id"].startswith(entry["intent_id"]+"_t171_") for r in entry["replies"])==2
  assert sum(r["id"].startswith(entry["intent_id"]+"_t174_") for r in entry["replies"])==2
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
  for r in entry["replies"]:
   assert r["id"] not in stage_ids and (r["id"].startswith(entry["intent_id"]+"_t167_") or r["id"].startswith(entry["intent_id"]+"_t171_") or r["id"].startswith(entry["intent_id"]+"_t174_") or r["id"].startswith(entry["intent_id"]+"_t175_") or r["id"].startswith(entry["intent_id"]+"_t176_") or r["id"].startswith(entry["intent_id"]+"_t177_") or r["id"].startswith(entry["intent_id"] + "_t178_") or r["id"].startswith(entry["intent_id"] + "_t179_") or r["id"].startswith(entry["intent_id"] + "_t180_") or r["id"].startswith(entry["intent_id"] + "_t181_") or r["id"].startswith(entry["intent_id"] + "_t182_") or r["id"].startswith(entry["intent_id"] + "_t183_") or r["id"].startswith(entry["intent_id"] + "_t184_") or r["id"].startswith(entry["intent_id"] + "_t185_"))
   stage_ids.add(r["id"])
   assert r["language"]=="ru" and r["style"]=="neutral"
   assert r["context"] in {"direct","private","group_addressed"}
   assert r["audiences"]==["all_ai_bots"] and r["read_only"] is True
   assert r["context_note"].strip() and r["avoid"].strip()
   assert 0<len(r["text"])<=1600
   assert not re.search(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})",r["text"])
   extra.append(r["text"])
 assert len(extra)==744 and len({norm(s) for s in replies+extra})==1023
 stage_keys={norm(s) for s in extra}
 for item in manifest["packs"]:
  otherpath=item["path"]
  if otherpath==PATH or not otherpath.endswith("_qa.json"):continue
  other=json.loads((ROOT/otherpath).read_text("utf-8"))
  for row in other.get("records",[]):
   assert not stage_keys.intersection(norm(s) for s in [row["answer"],*row.get("variants",[])]),otherpath
 print("T185 PASS: 31 boundary intents, 279 registered + 744 staged; source SHA, privacy and uniqueness")
if __name__=="__main__":main()
