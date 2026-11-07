"""T329/T330: provenance-locked, read-only scoped contextual continuations."""
import hashlib
import json
from pathlib import Path
from scripts.colloquial_t305 import ROOT, norm, blob_sha, PRIVATE
from scripts.context_t327_t328 import Stage as Previous
from scripts.context_t323_t324 import _keys
from scripts.context_t309_t310 import _read, GUARDS, CONTEXTS, FIELDS
from scripts.staged_context_selector import StagedSelection

STAGES = {
    "T329": {
        "source": "packs/ru/colloquial_ru_pragmatics_qa.json",
        "earlier": tuple("staging/ru/colloquial_t%d_context_pool.json" % n for n in (305,307,309,311,313,315,317,319,321,323,325)),
        "previous": "staging/ru/colloquial_t327_context_pool.json",
        "stage": "staging/ru/colloquial_t327_context_pool.json",
        "parent": "T327", "intents": 22, "prior": 33,
    },
    "T330": {
        "source": "packs/ru/practical_recovery_qa.json",
        "earlier": ("staging/ru/practical_t306_salvage.json",) + tuple("staging/ru/practical_t%d_context_pool.json" % n for n in (308,310,312,314,316,318,320,322,324,326)),
        "previous": "staging/ru/practical_t328_context_pool.json",
        "stage": "staging/ru/practical_t328_context_pool.json",
        "parent": "T328", "intents": 24, "prior": 32,
    },
}

class Stage:
    def __init__(self, label, root=ROOT):
        if label not in STAGES:
            raise ValueError("unreviewed stage")
        c = STAGES[label]
        root = Path(root).resolve(strict=True)
        Previous(c["parent"], root)
        manifest = json.loads(_read(root, "manifest.json"))
        registered = {x["path"]: x["sha256"] for x in manifest["packs"]}
        source_bytes, previous_bytes = _read(root, c["source"]), _read(root, c["previous"])
        stage = json.loads(_read(root, c["stage"]))
        original = json.loads(source_bytes)["records"]
        canonical = {row["id"]: row for row in original}
        total = c["intents"]; prior = c["prior"]
        checkpoint = {"stage_id": label, "processed_intents": total,
            "baseline_registered": total*9, "baseline_staged": total*prior,
            "added_candidates": total*2, "finished_100": 0,
            "partial_intents": total, "remaining_total": total*(100-9-prior-4), "rejected": 0}
        if (len(canonical)!=total or len(original)!=total or
            c["stage"] in registered or
            registered.get(c["source"])!=hashlib.sha256(source_bytes).hexdigest() or
            stage.get("source_pack")!=c["source"] or
            stage.get("source_pack_manifest_sha256")!=registered[c["source"]] or
            stage.get("source_pack_blob_sha")!=blob_sha(source_bytes) or
            stage.get("previous_stage")!=c["previous"] or
            stage.get("previous_stage_blob_sha")!=blob_sha(previous_bytes) or
            stage.get("schema_version")!=1 or
            stage.get("stage_type")!="supplemental_contextual_reply_pool" or
            stage.get("consumer_registered") is not False or
            stage.get("language")!="ru" or stage.get("audiences")!=["all_ai_bots"] or
            stage.get("constraints")!=GUARDS or stage.get("checkpoint")!=checkpoint):
            raise ValueError("unreviewed source or parent")
        ids, texts, notes = _keys(root, c, original)
        rows = stage.get("entries")
        if not isinstance(rows, list) or len(rows)!=total:
            raise ValueError("incorrect canonical coverage")
        self.by_intent={}
        for row in rows:
            ident, replies = row.get("intent_id"), row.get("replies")
            if (ident not in canonical or ident in self.by_intent or
                row.get("question")!=canonical[ident]["question"] or
                row.get("baseline_registered")!=9 or
                row.get("previous_staged")!=prior or row.get("new_staged")!=2 or
                not isinstance(replies, list) or len(replies)!=2):
                raise ValueError("incorrect canonical count")
            approved=[]
            for n,item in enumerate(replies,1):
                if not isinstance(item, dict) or set(item)!=FIELDS:
                    raise ValueError("unexpected fields")
                phrase, note = item.get("text"), item.get("context_note")
                if not isinstance(phrase, str) or not isinstance(note, str):
                    raise ValueError("non-text candidate")
                text_key, note_key, rid = norm(phrase), norm(note), item.get("id")
                if (rid!=f"{ident}_{label.lower()}_{n:02d}" or rid in ids or
                    text_key in texts or note_key in notes or
                    not text_key or not note_key or len(phrase)>1600 or len(note)>500 or
                    PRIVATE.search(phrase) or PRIVATE.search(note) or
                    item.get("language")!="ru" or item.get("style")!="neutral" or
                    item.get("audiences")!=["all_ai_bots"] or
                    item.get("context") not in CONTEXTS or
                    item.get("avoid")!="Только при подтверждённой адресации, намерении, аудитории, контексте и разрешении; не совершать действий и не выдавать предположение за факт." or
                    item.get("read_only") is not True):
                    raise ValueError("unsafe/repeated/unscoped response: "+str(rid))
                ids.add(rid); texts.add(text_key); notes.add(note_key)
                approved.append(item)
            self.by_intent[ident]=tuple(approved)
        if (set(self.by_intent)!=set(canonical) or
            len(ids)!=total*(prior+2) or
            len(texts)!=total*(9+prior+2)):
            raise ValueError("verified inventory mismatch")
        self.label=label
        self.stage_path=c["stage"]
        self.checkpoint=checkpoint
        self.cache_identity=(manifest["knowledge_version"],registered[c["source"]],blob_sha(previous_bytes),blob_sha(_read(root,c["stage"])))

    def select(self, intent_id, *, approved_reply_ids, audience, context,
               addressed=False, local_permission=False, recent_ids=()):
        if (addressed is not True or local_permission is not True or
            audience!="all_ai_bots" or context not in CONTEXTS or
            not isinstance(approved_reply_ids, frozenset) or not approved_reply_ids or
            not isinstance(recent_ids, tuple) or not all(isinstance(x,str) for x in recent_ids)):
            return None
        for item in self.by_intent.get(intent_id,()):
            if item["id"] in approved_reply_ids and item["id"] not in recent_ids and item["context"]==context:
                return StagedSelection(id=item["id"],text=item["text"],intent_id=intent_id,context_note=item["context_note"],stage_path=self.stage_path)
        return None

def validate_both(root=ROOT):
    a,b=Stage("T329",root),Stage("T330",root)
    texts=[norm(x["text"]) for stage in (a,b) for replies in stage.by_intent.values() for x in replies]
    notes=[norm(x["context_note"]) for stage in (a,b) for replies in stage.by_intent.values() for x in replies]
    if len(texts)!=92 or len(set(texts))!=184 or len(set(notes))!=184:
        raise ValueError("cross-stage normalized duplicates")
    return a,b

if __name__=="__main__":
    validate_both()
    print("PASS T329=44, T330=48 new synthetic opt-in, read-only answers")
