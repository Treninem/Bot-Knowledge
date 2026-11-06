"""Opt-in second layer above T241 multi-pack staging delta; no consumer changes.

Requires a byte-exact previously validated T241 stage and exact approved reply IDs.
A fresh source, wrong context or stale stage is rejected, not silently accepted.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import re
import unicodedata
from scripts.staged_context_delta import StagedContextDelta
from scripts.staged_context_selector import StagedContextSelector, StagedSelection

OVERLAY="staging/ru/context_overlay_t271.json"
BASE="staging/ru/context_delta_t241.json"
GUARDS={"read_only": True, "requires_direct_address": True, "no_personal_data": True}
CONTEXTS={"direct", "private", "group_addressed"}
PARENTS={
    "recovery":("staging/ru/recovery_t168_context_pool.json",24,72,73),
    "choice":("staging/ru/choice_t166_context_pool.json",30,70,71),
    "boundaries":("staging/ru/boundaries_t167_context_pool.json",31,69,70),
}
SECRET=re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bot_token|chat_id|user_id|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")

def norm(s):
    s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in {"P","S"} else c for c in s).split())

def blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def overlap(a,b):
    aa,bb=set(norm(a).split()),set(norm(b).split())
    return len(aa & bb)/max(1,len(aa | bb))

class ContextOverlayT271:
    def __init__(self, root:Path, path:str=OVERLAY):
        if path!=OVERLAY: raise ValueError("untrusted overlay")
        root=Path(root).resolve(strict=True)
        self.parent=StagedContextDelta(root,BASE)  # validates three registered sources and prior delta
        base_bytes=(root/BASE).read_bytes()
        data=json.loads((root/path).read_text("utf-8"))
        registry=json.loads((root/"manifest.json").read_text("utf-8"))
        if (data.get("schema_version")!=1 or data.get("stage_type")!="supplemental_context_delta_overlay"
            or data.get("consumer_registered") is not False or data.get("language")!="ru"
            or data.get("audiences")!=["all_ai_bots"] or data.get("constraints")!=GUARDS
            or data.get("parent_delta_path")!=BASE or data.get("parent_delta_blob_sha")!=blob(base_bytes)
            or path in {p["path"] for p in registry["packs"]}):
            raise ValueError("untrusted delta provenance or context")
        prior=json.loads(base_bytes)
        prior_by_id={e["intent_id"]:e for e in prior["entries"]}
        canonical={}
        texts=set()
        ids=set()
        prior_count=0
        for group,(stage_path,expected_n,before,after) in PARENTS.items():
            StagedContextSelector(root,stage_path)
            stage=json.loads((root/stage_path).read_text("utf-8"))
            src=json.loads((root/stage["source_pack"]).read_text("utf-8"))
            if len(src["records"])!=expected_n: raise ValueError("source count changed")
            for rec in src["records"]:
                ident=rec["id"]
                par=next((e for e in stage["entries"] if e["intent_id"]==ident),None)
                old=prior_by_id.get(ident)
                if ident in canonical or par is None or old is None or old["source_stage"]!=stage_path:
                    raise ValueError("missing parent canonical intent")
                previously=1+len(rec.get("variants",[]))+len(par["replies"])+len(old["replies"])
                if previously!=before: raise ValueError("stale previous per-intent count")
                canonical[ident]=(rec,stage_path,old,par,before)
                for t in [rec["answer"],*rec.get("variants",[]),*(x["text"] for x in par["replies"]),*(x["text"] for x in old["replies"])]:
                    texts.add(norm(t))
                for a in [*par["replies"],*old["replies"]]:
                    ids.add(a["id"])
                prior_count+=len(old["replies"])
        self._new={}
        for ent in data.get("entries",[]):
            ident=ent.get("intent_id")
            if ident not in canonical or ident in self._new: raise ValueError("unknown/duplicate intent")
            rec,stage_path,old,par,before=canonical[ident]
            if ent.get("question")!=rec["question"] or ent.get("source_stage")!=stage_path or ent.get("expected_total_before")!=before:
                raise ValueError("stale source reference")
            replies=ent.get("replies")
            if not isinstance(replies,list) or len(replies)!=1: raise ValueError("invalid count per canonical intent")
            historical=[rec["answer"],*rec.get("variants",[]),*(x["text"] for x in par["replies"]),*(x["text"] for x in old["replies"])]
            for reply in replies:
                ident2,txt=reply.get("id"),reply.get("text")
                if (ident2!=ident+"_t271_01" or ident2 in ids or not isinstance(txt,str)
                    or not 1<=len(txt)<=1600 or SECRET.search(txt)
                    or reply.get("language")!="ru" or reply.get("style")!="neutral"
                    or reply.get("audiences")!=["all_ai_bots"] or reply.get("read_only") is not True
                    or reply.get("context") not in CONTEXTS
                    or not isinstance(reply.get("context_note"),str) or not norm(reply["context_note"])
                    or not isinstance(reply.get("avoid"),str) or not reply["avoid"].strip()
                    or not norm(txt) or norm(txt) in texts):
                    raise ValueError("unsafe/duplicate reply")
                if max((overlap(txt,x) for x in historical),default=0)>=.78:
                    raise ValueError("near-duplicate within intent")
                ids.add(ident2)
                texts.add(norm(txt))
            self._new[ident]=tuple(replies)
        cp=data.get("checkpoint",{})
        if (len(canonical)!=85 or len(self._new)!=85
            or cp.get("processed_intents")!=85 or cp.get("parent_staged_count")!=prior_count
            or cp.get("added_in_current")!=sum(len(v) for v in self._new.values())
            or cp.get("total_staged_with_parent")!=prior_count+85
            or cp.get("remaining_total")!=sum(100-(v[4]+len(self._new[k])) for k,v in canonical.items())
            or cp.get("partial_intents")!=85 or cp.get("finished_100")!=0 or cp.get("rejected")!=0):
            raise ValueError("inconsistent checkpoint")
        self.checkpoint=cp
        self.cache_identity=(registry["knowledge_version"],blob(base_bytes),blob((root/path).read_bytes()))

    def select(self,intent_id:str,*,approved_reply_ids:frozenset[str],audience:str,context:str,
               addressed:bool=False,local_permission:bool=False,recent_ids:tuple[str,...]=()):
        if (not addressed or not local_permission or audience!="all_ai_bots"
            or context not in CONTEXTS or not isinstance(approved_reply_ids,frozenset)
            or not approved_reply_ids or not isinstance(recent_ids,tuple)):
            return None
        for v in self._new.get(intent_id,()):
            if v["id"] in approved_reply_ids and v["id"] not in recent_ids and v["context"]==context:
                return StagedSelection(id=v["id"],text=v["text"],intent_id=intent_id,
                    context_note=v["context_note"],stage_path=OVERLAY)
        return None
