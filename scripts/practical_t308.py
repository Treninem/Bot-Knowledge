"""T308: additional recovery guidance. Read-only and opt-in; not consumer activation."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from scripts.practical_t306 import PracticalT306, ROOT, SOURCE, STAGE as PREVIOUS, GUARDS, CONTEXTS, PRIVATE, norm, blob_sha
from scripts.staged_context_selector import StagedSelection
STAGE = "staging/ru/practical_t308_context_pool.json"
class PracticalT308:
    def __init__(self, root:Path=ROOT):
        root=Path(root).resolve(strict=True)
        previous=PracticalT306(root)
        path=root/STAGE
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("unsafe path")
        stage=json.loads(path.read_text("utf-8"))
        manifest=json.loads((root/"manifest.json").read_text("utf-8"))
        hashes={x["path"]:x["sha256"] for x in manifest["packs"]}
        parent_bytes=(root/SOURCE).read_bytes()
        previous_bytes=(root/PREVIOUS).read_bytes()
        checkpoint={"stage_id":"T308","processed_intents":24,"baseline_registered":216,
                    "baseline_staged":96,"added_candidates":72,"finished_100":0,
                    "partial_intents":24,"remaining_total":2016,"rejected":0}
        if (STAGE in hashes or stage.get("schema_version") != 1
            or stage.get("stage_type") != "supplemental_contextual_reply_pool"
            or stage.get("consumer_registered") is not False
            or stage.get("language") != "ru" or stage.get("audiences") != ["all_ai_bots"]
            or stage.get("constraints") != GUARDS or stage.get("source_pack") != SOURCE
            or stage.get("source_pack_manifest_sha256") != hashes.get(SOURCE)
            or hashlib.sha256(parent_bytes).hexdigest() != hashes.get(SOURCE)
            or stage.get("source_pack_blob_sha") != blob_sha(parent_bytes)
            or stage.get("previous_stage") != PREVIOUS
            or stage.get("previous_stage_blob_sha") != blob_sha(previous_bytes)
            or stage.get("checkpoint") != checkpoint):
            raise ValueError("source hash or checkpoint mismatch")
        originals={x["id"]:x for x in json.loads(parent_bytes)["records"]}
        old=json.loads(previous_bytes)
        used_ids,used_texts,used_notes=set(),set(),set()
        for x in originals.values():
            used_texts.update(norm(z) for z in [x["answer"],*x["variants"]])
        for entry in old["entries"]:
            for x in entry["replies"]:
                used_ids.add(x["id"])
                used_texts.add(norm(x["text"]))
                used_notes.add(norm(x["context_note"]))
        self.by_intent={}
        for e in stage.get("entries", []):
            ident=e.get("intent_id")
            if (ident not in originals or ident in self.by_intent
                or e.get("question") != originals[ident]["question"]
                or e.get("baseline_registered") != 9 or e.get("previous_staged") != 4
                or e.get("new_staged") != 3 or not isinstance(e.get("replies"),list)
                or len(e["replies"]) != 3):
                raise ValueError("intent inventory differs")
            checked=[]
            for i,x in enumerate(e["replies"],1):
                key=x.get("id"); s=x.get("text"); note=x.get("context_note")
                if (key != f"{ident}_t308_{i:02d}" or key in used_ids
                    or not isinstance(s,str) or not 1 <= len(s) <= 1600
                    or not isinstance(note,str) or not 1 <= len(note) <= 500
                    or norm(s) in used_texts or norm(note) in used_notes
                    or PRIVATE.search(s) or PRIVATE.search(note)
                    or x.get("language") != "ru" or x.get("style") != "neutral"
                    or x.get("audiences") != ["all_ai_bots"] or x.get("context") not in CONTEXTS
                    or x.get("read_only") is not True
                    or not isinstance(x.get("avoid"),str) or not x["avoid"].strip()):
                    raise ValueError(f"unsafe or repeated reply: {key}")
                used_ids.add(key);used_texts.add(norm(s));used_notes.add(norm(note))
                checked.append(x)
            self.by_intent[ident]=tuple(checked)
        if set(self.by_intent) != set(originals) or len(used_ids)!=168 or len(used_texts)!=384:
            raise ValueError("incomplete group")
        self.checkpoint=checkpoint
        self.cache_identity=(manifest["knowledge_version"],hashes[SOURCE],blob_sha(previous_bytes),blob_sha(path.read_bytes()))
        self.parent=previous
    def select(self,intent_id: str,*,approved_reply_ids:frozenset[str],audience:str,context:str,
               addressed:bool=False,local_permission:bool=False,recent_ids:tuple[str,...]=()):
        if (not addressed or not local_permission or audience!="all_ai_bots"
            or context not in CONTEXTS or not isinstance(approved_reply_ids,frozenset)
            or not approved_reply_ids or not isinstance(recent_ids,tuple)):
            return None
        for x in self.by_intent.get(intent_id,()):
            if x["id"] in approved_reply_ids and x["context"]==context and x["id"] not in recent_ids:
                return StagedSelection(id=x["id"],text=x["text"],intent_id=intent_id,
                                       context_note=x["context_note"],stage_path=STAGE)
        return None
