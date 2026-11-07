"""T371/T372: immutable ancestry, distinct context, explicit read-only selection."""
import hashlib
import json
from pathlib import Path
from scripts.colloquial_t305 import ROOT, norm, blob_sha, PRIVATE
from scripts.context_t369_t370 import Stage as Previous, STAGES as PREV
from scripts.context_t323_t324 import _keys
from scripts.context_t309_t310 import _read, GUARDS, CONTEXTS, FIELDS
from scripts.staged_context_selector import StagedSelection

STAGES = {
 "T371": {"source": PREV["T369"]["source"], "earlier": (*PREV["T369"]["earlier"], PREV["T369"]["previous"]),
          "previous": PREV["T369"]["stage"], "stage": "staging/ru/colloquial_t371_context_pool.json",
          "parent":"T369", "intents":22, "prior":77},
 "T372": {"source": PREV["T370"]["source"], "earlier": (*PREV["T370"]["earlier"], PREV["T370"]["previous"]),
          "previous": PREV["T370"]["stage"], "stage": "staging/ru/practical_t372_context_pool.json",
          "parent":"T370", "intents":24, "prior":76},
}
class Stage:
    def __init__(self,label,root=ROOT):
        if label not in STAGES:
            raise ValueError("unreviewed stage")
        cfg=STAGES[label]
        root=Path(root).resolve(strict=True)
        Previous(cfg["parent"],root)
        manifest=json.loads(_read(root,"manifest.json"))
        registered={x["path"]:x["sha256"] for x in manifest["packs"]}
        source,old=_read(root,cfg["source"]),_read(root,cfg["previous"])
        stage=json.loads(_read(root,cfg["stage"]))
        original=json.loads(source)["records"]
        canonical={x["id"]:x for x in original}
        n,prior=cfg["intents"],cfg["prior"]
        expected={"stage_id":label,"processed_intents":n,"baseline_registered":n*9,
                  "baseline_staged":n*prior,"added_candidates":n*2,"finished_100":0,
                  "partial_intents":n,"remaining_total":n*(100-9-prior-2),"rejected":0}
        if (len(original)!=n or len(canonical)!=n or cfg["stage"] in registered or
            registered.get(cfg["source"])!=hashlib.sha256(source).hexdigest() or
            stage.get("source_pack")!=cfg["source"] or
            stage.get("source_pack_manifest_sha256")!=registered[cfg["source"]] or
            stage.get("source_pack_blob_sha")!=blob_sha(source) or
            stage.get("previous_stage")!=cfg["previous"] or
            stage.get("previous_stage_blob_sha")!=blob_sha(old) or
            stage.get("schema_version")!=1 or
            stage.get("stage_type")!="supplemental_contextual_reply_pool" or
            stage.get("consumer_registered") is not False or
            stage.get("language")!="ru" or
            stage.get("audiences")!=["all_ai_bots"] or
            stage.get("constraints")!=GUARDS or
            stage.get("checkpoint")!=expected):
            raise ValueError("source, scope or parent mismatch")
        ids,texts,notes=_keys(root,cfg,original)
        entries=stage.get("entries")
        if not isinstance(entries,list) or len(entries)!=n:
            raise ValueError("partial coverage")
        self.by_intent={}
        for entry in entries:
            ident=entry.get("intent_id")
            replies=entry.get("replies")
            if (ident not in canonical or ident in self.by_intent or
                entry.get("question")!=canonical[ident]["question"] or
                entry.get("baseline_registered")!=9 or
                entry.get("previous_staged")!=prior or
                entry.get("new_staged")!=2 or
                not isinstance(replies,list) or len(replies)!=2):
                raise ValueError("wrong per-intent coverage")
            approved=[]
            for idx,item in enumerate(replies,1):
                if not isinstance(item,dict) or set(item)!=FIELDS:
                    raise ValueError("unreviewed reply fields")
                phrase,note=item.get("text"),item.get("context_note")
                if not isinstance(phrase,str) or not isinstance(note,str):
                    raise ValueError("nontext")
                key,contextkey=norm(phrase),norm(note)
                if (item.get("id")!=f"{ident}_{label.lower()}_{idx:02d}" or
                    item["id"] in ids or key in texts or contextkey in notes or
                    not key or not contextkey or len(phrase)>1600 or len(note)>500 or
                    PRIVATE.search(phrase) or PRIVATE.search(note) or
                    item.get("language")!="ru" or item.get("style")!="neutral" or
                    item.get("audiences")!=["all_ai_bots"] or
                    item.get("context") not in CONTEXTS or
                    item.get("avoid")!="Только при подтверждённой адресации, намерении, аудитории, контексте и разрешении; не совершать действий и не выдавать предположение за факт." or
                    item.get("read_only") is not True):
                    raise ValueError("unsafe/duplicate answer: "+str(item.get("id")))
                ids.add(item["id"]);texts.add(key);notes.add(contextkey)
                approved.append(item)
            self.by_intent[ident]=tuple(approved)
        if set(self.by_intent)!=set(canonical) or len(ids)!=n*(prior+2) or len(texts)!=n*(9+prior+2):
            raise ValueError("bad cumulative counts")
        self.label=label
        self.stage_path=cfg["stage"]
        self.checkpoint=expected
        self.cache_identity=(manifest["knowledge_version"],registered[cfg["source"]],blob_sha(old),blob_sha(_read(root,cfg["stage"])))
    def select(self,intent_id,*,approved_reply_ids,audience,context,addressed=False,local_permission=False,recent_ids=()):
        if (addressed is not True or local_permission is not True or
            audience!="all_ai_bots" or context not in CONTEXTS or
            not isinstance(approved_reply_ids,frozenset) or not approved_reply_ids or
            not isinstance(recent_ids,tuple) or not all(isinstance(x,str) for x in recent_ids)):
            return None
        for x in self.by_intent.get(intent_id,()):
            if x["id"] in approved_reply_ids and x["id"] not in recent_ids and x["context"]==context:
                return StagedSelection(id=x["id"],text=x["text"],intent_id=intent_id,context_note=x["context_note"],stage_path=self.stage_path)
        return None

def validate_both(root=ROOT):
    a,b=Stage("T371",root),Stage("T372",root)
    texts=[norm(x["text"]) for s in (a,b) for rows in s.by_intent.values() for x in rows]
    notes=[norm(x["context_note"]) for s in (a,b) for rows in s.by_intent.values() for x in rows]
    if len(texts)!=92 or len(set(texts))!=92 or len(set(notes))!=92:
        raise ValueError("cross-stage duplicate")
    return a,b

if __name__=="__main__":
    validate_both()
    print("PASS T371=44 T372=48 synthetic gated read-only replies")
