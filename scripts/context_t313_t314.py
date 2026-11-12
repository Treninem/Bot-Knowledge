"""T313/T314 provenance and read-only consumer opt-in; not registered."""
import json,hashlib
from pathlib import Path
from scripts.colloquial_t305 import ROOT,norm,blob_sha,PRIVATE
from scripts.context_t311_t312 import Stage as ParentStage
from scripts.context_t309_t310 import _read,GUARDS,CONTEXTS,FIELDS
from scripts.staged_context_selector import StagedSelection
C={
"T313":dict(source="packs/ru/colloquial_ru_pragmatics_qa.json",previous="staging/ru/colloquial_t311_context_pool.json",earlier=["staging/ru/colloquial_t305_context_pool.json","staging/ru/colloquial_t307_context_pool.json","staging/ru/colloquial_t309_context_pool.json"],stage="staging/ru/colloquial_t313_context_pool.json",parent="T311",intents=22,prior=15),
"T314":dict(source="packs/ru/practical_recovery_qa.json",previous="staging/ru/practical_t312_context_pool.json",earlier=["staging/ru/practical_t306_salvage.json","staging/ru/practical_t308_context_pool.json","staging/ru/practical_t310_context_pool.json"],stage="staging/ru/practical_t314_context_pool.json",parent="T312",intents=24,prior=14)}
class Stage:
 def __init__(self,label,root=ROOT):
  if label not in C:raise ValueError("unknown stage")
  c=C[label];self.label=label;root=Path(root).resolve(strict=True);ParentStage(c["parent"],root)
  man=json.loads(_read(root,"manifest.json"));listed={p["path"]:p["sha256"] for p in man["packs"]}
  source_bytes=_read(root,c["source"]);prev_bytes=_read(root,c["previous"])
  source=json.loads(source_bytes);stage=json.loads(_read(root,c["stage"]))
  canonical={r["id"]:r for r in source["records"]}
  cp=dict(stage_id=label,processed_intents=c["intents"],baseline_registered=c["intents"]*9,baseline_staged=c["intents"]*c["prior"],added_candidates=c["intents"]*2,finished_100=0,partial_intents=c["intents"],remaining_total=c["intents"]*(100-9-c["prior"]-2),rejected=0)
  if(c["stage"] in listed or hashlib.sha256(source_bytes).hexdigest()!=listed.get(c["source"]) or
     len(canonical)!=c["intents"] or len(source["records"])!=c["intents"] or
     stage.get("schema_version")!=1 or stage.get("stage_type")!="supplemental_contextual_reply_pool" or
     stage.get("consumer_registered") is not False or stage.get("language")!="ru" or
     stage.get("audiences")!=["all_ai_bots"] or stage.get("constraints")!=GUARDS or
     stage.get("source_pack")!=c["source"] or stage.get("source_pack_manifest_sha256")!=listed[c["source"]] or
     stage.get("source_pack_blob_sha")!=blob_sha(source_bytes) or stage.get("previous_stage")!=c["previous"] or
     stage.get("previous_stage_blob_sha")!=blob_sha(prev_bytes) or stage.get("checkpoint")!=cp):
   raise ValueError("source or parent checksum changed")
  texts=set();ids=set();notes=set()
  for row in source["records"]:
   if len(row.get("variants",[]))!=8:raise ValueError("unexpected registered baseline")
   for text in [row["answer"],*row["variants"]]:
    if norm(text) in texts:raise ValueError("baseline duplicate")
    texts.add(norm(text))
  for path in [*c["earlier"],c["previous"]]:
   for e in json.loads(_read(root,path))["entries"]:
    for x in e["replies"]:
     if x["id"] in ids or norm(x["text"]) in texts or norm(x["context_note"]) in notes:raise ValueError("older duplicate")
     ids.add(x["id"]);texts.add(norm(x["text"]));notes.add(norm(x["context_note"]))
  if len(ids)!=c["intents"]*c["prior"]:raise ValueError("old reply inventory")
  self.by_intent={}
  entries=stage.get("entries")
  if not isinstance(entries,list) or len(entries)!=c["intents"]:raise ValueError("entry count")
  for entry in entries:
   ident=entry.get("intent_id");items=entry.get("replies")
   if(ident not in canonical or ident in self.by_intent or entry.get("question")!=canonical[ident]["question"] or
      entry.get("baseline_registered")!=9 or entry.get("previous_staged")!=c["prior"] or
      entry.get("new_staged")!=2 or not isinstance(items,list) or len(items)!=2):
    raise ValueError("canonical mismatch")
   current=[]
   for k,x in enumerate(items,1):
    if not isinstance(x,dict) or set(x)!=FIELDS:raise ValueError("unexpected keys")
    key=norm(x["text"]);note=norm(x["context_note"])
    if(x["id"]!=f"{ident}_{label.lower()}_{k:02d}" or x["id"] in ids or key in texts or
       note in notes or not key or not note or len(x["text"])>1600 or len(x["context_note"])>500 or
       x["language"]!="ru" or x["style"]!="neutral" or x["audiences"]!=["all_ai_bots"] or
       x["context"] not in CONTEXTS or x["read_only"] is not True or
       not isinstance(x["avoid"],str) or not x["avoid"].strip() or
       PRIVATE.search(x["text"]) or PRIVATE.search(x["context_note"])):
     raise ValueError("unsafe or repeated response")
    ids.add(x["id"]);texts.add(key);notes.add(note);current.append(x)
   self.by_intent[ident]=tuple(current)
  if len(texts)!=(c["prior"]+11)*c["intents"] or set(self.by_intent)!=set(canonical):
   raise ValueError("total mismatch")
  self.checkpoint=cp;self.stage_path=c["stage"]
  self.cache_identity=(man["knowledge_version"],listed[c["source"]],blob_sha(prev_bytes),blob_sha(_read(root,c["stage"])))
 def select(self,intent_id,*,approved_reply_ids,audience,context,addressed=False,local_permission=False,recent_ids=()):
  if(addressed is not True or local_permission is not True or audience!="all_ai_bots" or
     context not in CONTEXTS or not isinstance(approved_reply_ids,frozenset) or
     not isinstance(recent_ids,tuple) or not all(isinstance(x,str) for x in recent_ids)):
   return None
  for x in self.by_intent.get(intent_id,()):
   if x["id"] in approved_reply_ids and x["id"] not in recent_ids and x["context"]==context:
    return StagedSelection(id=x["id"],text=x["text"],intent_id=intent_id,context_note=x["context_note"],stage_path=self.stage_path)
  return None
def validate_both(root=ROOT):
 a,b=Stage("T313",root),Stage("T314",root)
 texts=[norm(x["text"]) for model in (a,b) for items in model.by_intent.values() for x in items]
 notes=[norm(x["context_note"]) for model in (a,b) for items in model.by_intent.values() for x in items]
 if len(texts)!=92 or len(set(texts))!=92 or len(set(notes))!=92:raise ValueError("cross-stage repeat")
 return a,b
if __name__=="__main__":
 a,b=validate_both();print("PASS 44+48 original, read-only, unregistered choices")
