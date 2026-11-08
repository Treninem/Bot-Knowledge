"""SHA-pinned opt-in replies to addressed standalone thanks/farewell only."""
from __future__ import annotations
import hashlib, json, re, unicodedata
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PACK = "packs/ru/dialogue.json"
def norm(s):
    return " ".join(re.findall(r"[\w]+",unicodedata.normalize("NFKC",s).casefold().replace("ё","е")))
class ContextualReactions:
    def __init__(self, root=ROOT):
        root=Path(root)
        manifest=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
        found=[x for x in manifest.get("packs",[]) if x.get("path")==PACK]
        if manifest.get("schema_version")!=1 or len(found)!=1: raise ValueError("manifest")
        raw=(root/PACK).read_bytes()
        digest=hashlib.sha256(raw).hexdigest()
        if digest!=found[0]["sha256"]: raise ValueError("SHA")
        data=json.loads(raw.decode("utf-8")); meta=data.get("contextual_reactions",{})
        policy={"synthetic_examples_only":True,"automatic_sanctions_allowed":False,
                "personal_data_allowed":False,"requires_explicit_address":True,"requires_local_permission":True}
        if data.get("schema_version")!=1 or data.get("language")!="ru" or meta.get("schema_version")!=1 or meta.get("language")!="ru" or meta.get("audiences")!=["all_ai_bots"] or any(meta.get(k) is not v for k,v in policy.items()): raise ValueError("policy")
        groups=meta.get("intents",{})
        if set(groups)!={"thanks","farewell"}: raise ValueError("intents")
        seen={norm(t) for intent in groups for t in data["reactions"][intent]};self._data={}
        for intent,item in groups.items():
            contexts=item.get("contexts",{});inputs=item.get("accepted_inputs",[])
            if item.get("default_context")!="neutral" or not isinstance(contexts,dict) or not 4<=len(contexts)<=24 or "neutral" not in contexts or len(inputs)!=4: raise ValueError("contexts")
            notes=item.get("context_conditions",{})
            if not isinstance(notes,dict) or set(notes)!=set(contexts) or any(not isinstance(note,str) or not 10<=len(note)<=240 for note in notes.values()): raise ValueError("context conditions")
            cleaned={}
            for name,values in contexts.items():
                if not isinstance(name,str) or not name.isascii() or len(values)!=4: raise ValueError("group")
                for text in values:
                    if not isinstance(text,str) or not 5<=len(text)<=300 or norm(text) in seen: raise ValueError("duplicate")
                    seen.add(norm(text))
                cleaned[name]=tuple(values)
            self._data[intent]=(frozenset(norm(x) for x in inputs),cleaned)
        self.snapshot_key=(manifest["knowledge_version"],digest)
    def reply(self,message,*,intent,addressed=False,local_permission=False,context="neutral",
              audience="all_ai_bots",language="ru",sensitive=False,silence_requested=False,recent=()):
        if not isinstance(message,str) or len(message)>1000: raise ValueError("message")
        if any(type(v) is not bool for v in (addressed,local_permission,sensitive,silence_requested)): raise ValueError("flags")
        if not isinstance(recent,(tuple,list)) or len(recent)>128 or any(not isinstance(x,str) or len(x)>1000 for x in recent): raise ValueError("recent")
        if intent not in self._data or audience!="all_ai_bots": raise ValueError("audience/intent")
        inputs,groups=self._data[intent]
        if context not in groups: raise ValueError("unknown context")
        def decline(reason): return {"status":reason,"text":None}
        if not addressed: return decline("not_addressed")
        if not local_permission: return decline("not_authorized")
        if sensitive or silence_requested: return decline("suppressed")
        if language!="ru": return decline("wrong_language")
        val=unicodedata.normalize("NFKC",message).casefold().strip()
        if not re.fullmatch(r"[а-яё ,.!\s]+",val) or norm(val) not in inputs: return decline("no_match")
        seen={norm(x) for x in recent}
        for i,variant in enumerate(groups[context]):
            if norm(variant) not in seen:
                return {"status":"ok","text":variant,"source_pack":PACK,"source_id":f"{intent}_{context}_{i+1:02}","context":context,"snapshot_key":self.snapshot_key}
        return decline("repeat_suppressed")
