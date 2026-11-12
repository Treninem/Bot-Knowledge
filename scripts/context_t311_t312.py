"""Read-only T311/T312 context pool verification. No consumer auto-loading."""
import json, hashlib
from pathlib import Path
from scripts.colloquial_t305 import ROOT, norm, blob_sha, PRIVATE
from scripts.context_t309_t310 import ReadOnlyContextStage, GUARDS, CONTEXTS, FIELDS, _read
from scripts.staged_context_selector import StagedSelection

CONFIG={
"T311": dict(source="packs/ru/colloquial_ru_pragmatics_qa.json",previous="staging/ru/colloquial_t309_context_pool.json",earlier=["staging/ru/colloquial_t305_context_pool.json","staging/ru/colloquial_t307_context_pool.json"],stage="staging/ru/colloquial_t311_context_pool.json",parent="T309",intents=22,prior=12),
"T312": dict(source="packs/ru/practical_recovery_qa.json",previous="staging/ru/practical_t310_context_pool.json",earlier=["staging/ru/practical_t306_salvage.json","staging/ru/practical_t308_context_pool.json"],stage="staging/ru/practical_t312_context_pool.json",parent="T310",intents=24,prior=11)}
class Stage:
 def __init__(self,label,root=ROOT):
  if label not in CONFIG: raise ValueError("unknown stage")
  self.label=label;c=CONFIG[label];root=Path(root).resolve(strict=True)
  ReadOnlyContextStage(c["parent"],root)
  manifest=json.loads(_read(root,"manifest.json"))
  registered={x["path"]:x["sha256"] for x in manifest["packs"]}
  source_bytes=_read(root,c["source"]);previous_bytes=_read(root,c["previous"])
  base=json.loads(source_bytes);stage=json.loads(_read(root,c["stage"]))
  canonical={r["id"]:r for r in base["records"]}
  expected=dict(stage_id=label,processed_intents=c["intents"],baseline_registered=9*c["intents"],baseline_staged=c["prior"]*c["intents"],added_candidates=3*c["intents"],finished_100=0,partial_intents=c["intents"],remaining_total=(100-9-c["prior"]-3)*c["intents"],rejected=0)
  if (c["stage"] in registered or hashlib.sha256(source_bytes).hexdigest()!=registered.get(c["source"]) or
      len(canonical)!=c["intents"] or len(base["records"])!=c["intents"] or
      stage.get("schema_version")!=1 or stage.get("stage_type")!="supplemental_contextual_reply_pool" or
      stage.get("consumer_registered") is not False or stage.get("language")!="ru" or
      stage.get("audiences")!=["all_ai_bots"] or stage.get("constraints")!=GUARDS or
      stage.get("source_pack")!=c["source"] or
      stage.get("source_pack_manifest_sha256")!=registered[c["source"]] or
      stage.get("source_pack_blob_sha")!=blob_sha(source_bytes) or
      stage.get("previous_stage")!=c["previous"] or stage.get("previous_stage_blob_sha")!=blob_sha(previous_bytes) or
      stage.get("checkpoint")!=expected):
   raise ValueError("source provenance or checkpoint mismatch")
  ids=set();texts=set();notes=set()
  for r in base["records"]:
   if len(r.get("variants",[]))!=8: raise ValueError("registered baseline changed")
   for t in [r["answer"],*r["variants"]]:
    if norm(t) in texts: raise ValueError("registered repeat")
    texts.add(norm(t))
  for p in [*c["earlier"],c["previous"]]:
   for e in json.loads(_read(root,p))["entries"]:
    for x in e["replies"]:
     if x["id"] in ids or norm(x["text"]) in texts or norm(x["context_note"]) in notes:
      raise ValueError("prior inventory duplicate")
     ids.add(x["id"]);texts.add(norm(x["text"]));notes.add(norm(x["context_note"]))
  if len(ids)!=c["prior"]*c["intents"]:raise ValueError("prior inventory size")
  self.by_intent={}
  rows=stage.get("entries")
  if not isinstance(rows,list) or len(rows)!=c["intents"]:raise ValueError("stage inventory size")
  for e in rows:
   ident=e.get("intent_id");rs=e.get("replies")
   if (ident not in canonical or ident in self.by_intent or
       e.get("question")!=canonical[ident]["question"] or e.get("baseline_registered")!=9 or
       e.get("previous_staged")!=c["prior"] or e.get("new_staged")!=3 or
       not isinstance(rs,list) or len(rs)!=3):raise ValueError("entry mismatch")
   out=[]
   for n,x in enumerate(rs,1):
    if not isinstance(x,dict) or set(x)!=FIELDS:raise ValueError("unreviewed keys")
    key=norm(x["text"]);note=norm(x["context_note"])
    if (x["id"]!=f"{ident}_{label.lower()}_{n:02d}" or x["id"] in ids or
        not key or not note or key in texts or note in notes or
        len(x["text"])>1600 or len(x["context_note"])>500 or
        x["language"]!="ru" or x["style"]!="neutral" or
        x["audiences"]!=["all_ai_bots"] or x["context"] not in CONTEXTS or
        x["read_only"] is not True or not isinstance(x["avoid"],str) or not x["avoid"].strip() or
        PRIVATE.search(x["text"]) or PRIVATE.search(x["context_note"])):
     raise ValueError("unsafe or duplicate reply")
    ids.add(x["id"]);texts.add(key);notes.add(note);out.append(x)
   self.by_intent[ident]=tuple(out)
  if len(texts)!=(c["prior"]+12)*c["intents"] or set(self.by_intent)!=set(canonical):
   raise ValueError("total inventory mismatch")
  self.checkpoint=expected;self.stage_path=c["stage"]
  self.cache_identity=(manifest["knowledge_version"],registered[c["source"]],blob_sha(previous_bytes),blob_sha(_read(root,c["stage"])))
 def select(self,intent_id,*,approved_reply_ids,audience,context,addressed=False,local_permission=False,recent_ids=()):
  if (addressed is not True or local_permission is not True or audience!="all_ai_bots" or
      context not in CONTEXTS or not isinstance(approved_reply_ids,frozenset) or
      not isinstance(recent_ids,tuple) or not all(isinstance(x,str) for x in recent_ids)):
   return None
  for x in self.by_intent.get(intent_id,()):
   if x["id"] in approved_reply_ids and x["id"] not in recent_ids and x["context"]==context:
    return StagedSelection(id=x["id"],text=x["text"],intent_id=intent_id,context_note=x["context_note"],stage_path=self.stage_path)
  return None
def validate_both(root=ROOT):
 a,b=Stage("T311",root),Stage("T312",root)
 texts=[norm(x["text"]) for model in (a,b) for v in model.by_intent.values() for x in v]
 notes=[norm(x["context_note"]) for model in (a,b) for v in model.by_intent.values() for x in v]
 if len(texts)!=138 or len(set(texts))!=138 or len(set(notes))!=138:raise ValueError("cross-group repetition")
 return a,b
if __name__=="__main__":
 a,b=validate_both();print("PASS 66+72=138 read-only replies; not consumer registered")
