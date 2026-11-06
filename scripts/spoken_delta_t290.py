"""T290: source-pinned, opt-in continuation of 24 conversation intents (96 new replies)."""
import hashlib
import json
from pathlib import Path
from scripts.spoken_delta_t289 import SpokenDeltaT289, DELTA as PARENT
from scripts.spoken_delta_t287 import HISTORY
from scripts.spoken_delta_overlay import SOURCE, GUARDS, CONTEXTS, SECRET, norm, jaccard, blob_sha
from scripts.staged_context_selector import StagedSelection

DELTA = "staging/ru/spoken_pragmatics_t290_delta.json"
GRANDPARENT = "staging/ru/spoken_pragmatics_t287_delta.json"

class SpokenDeltaT290:
    def __init__(self, root: Path, path: str = DELTA):
        if path != DELTA:
            raise ValueError("unreviewed stage path")
        root = Path(root).resolve(strict=True)
        self.parent = SpokenDeltaT289(root)
        parent_bytes = (root / PARENT).read_bytes()
        stage = json.loads((root / DELTA).read_bytes())
        raw = (root / DELTA).read_bytes()
        manifest = json.loads((root / "manifest.json").read_text("utf-8"))
        registered = {p["path"]: p["sha256"] for p in manifest["packs"]}
        if (stage.get("schema_version") != 1
                or stage.get("delta_type") != "supplemental_contextual_reply_delta"
                or stage.get("consumer_registered") is not False
                or stage.get("language") != "ru"
                or stage.get("audiences") != ["all_ai_bots"]
                or stage.get("constraints") != GUARDS
                or stage.get("parent_delta_path") != PARENT
                or stage.get("parent_delta_blob_sha") != blob_sha(parent_bytes)
                or stage.get("source_pack") != SOURCE
                or stage.get("source_pack_manifest_sha256") != registered[SOURCE]
                or hashlib.sha256((root / SOURCE).read_bytes()).hexdigest() != registered[SOURCE]
                or DELTA in registered):
            raise ValueError("untrusted staged source or broken parent")
        canonical = {r["id"]:r for r in json.loads((root / SOURCE).read_text("utf-8"))["records"]}
        if len(canonical) != 24:
            raise ValueError("registered inventory changed")
        known={i:[r["answer"], *r["variants"]] for i,r in canonical.items()}
        notes={i:set() for i in canonical}
        all_text=set()
        used_ids=set()
        for filename in (*HISTORY, GRANDPARENT, PARENT):
            rows=json.loads((root / filename).read_text("utf-8"))["entries"]
            if len(rows)!=24 or {x["intent_id"] for x in rows}!=set(canonical):
                raise ValueError("historical intent inventory changed")
            for e in rows:
                for reply in e["replies"]:
                    if reply["id"] in used_ids:
                        raise ValueError("historical duplicate id")
                    used_ids.add(reply["id"])
                    known[e["intent_id"]].append(reply["text"])
                    notes[e["intent_id"]].add(norm(reply["context_note"]))
        for values in known.values():
            if len(values)!=92:
                raise ValueError("incorrect prior unique count")
            for txt in values:
                key=norm(txt)
                if not key or key in all_text:
                    raise ValueError("historical duplicate text")
                all_text.add(key)
        self._rows={}
        for row in stage.get("entries",[]):
            intent=row.get("intent_id")
            if (intent not in canonical or intent in self._rows
                    or row.get("question")!=canonical[intent]["question"]
                    or row.get("registered_reply_count")!=9
                    or row.get("parent_staged_reply_count")!=83
                    or not isinstance(row.get("replies"),list)
                    or len(row["replies"])!=4):
                raise ValueError("unexpected ID, question or increment")
            responses=[]
            for index,reply in enumerate(row["replies"],1):
                rid,txt,note=reply.get("id"),reply.get("text"),reply.get("context_note")
                if (rid!=f"{intent}_t290_{index:02d}" or rid in used_ids
                        or not isinstance(txt,str) or not 1 <= len(txt) <=1600
                        or SECRET.search(txt) or not norm(txt) or norm(txt) in all_text
                        or not isinstance(note,str) or not norm(note) or norm(note) in notes[intent]
                        or reply.get("language")!="ru" or reply.get("style")!="neutral"
                        or reply.get("audiences")!=["all_ai_bots"]
                        or reply.get("read_only") is not True
                        or reply.get("context") not in CONTEXTS
                        or not isinstance(reply.get("avoid"),str) or not reply["avoid"].strip()
                        or max((jaccard(txt,old) for old in known[intent]),default=0) >= .78):
                    raise ValueError(f"unsafe or repeated staged reply: {intent} #{index}")
                used_ids.add(rid)
                all_text.add(norm(txt))
                known[intent].append(txt)
                notes[intent].add(norm(note))
                responses.append(reply)
            self._rows[intent]=tuple(responses)
        cp=stage.get("checkpoint",{})
        expected=dict(stage_id="T290",processed_intents=24,registered_count=216,
            parent_staged_count=1992,added_in_current=96,total_staged_with_parent=2088,
            previous_per_intent=92,now_per_intent=96,remaining_per_intent=4,
            remaining_total=96,partial_intents=24,finished_100=0,rejected=0)
        if len(self._rows)!=24 or any(cp.get(k)!=v for k,v in expected.items()):
            raise ValueError("bad checkpoint")
        self.checkpoint=cp
        self.cache_identity=(manifest["knowledge_version"],blob_sha(parent_bytes),blob_sha(raw))

    def select(self,intent_id: str, *,approved_reply_ids: frozenset[str],
               audience: str,context: str,addressed: bool=False,
               local_permission: bool=False,recent_ids:tuple[str,...]=())->StagedSelection|None:
        if (audience!="all_ai_bots" or not addressed or not local_permission
                or context not in CONTEXTS or not isinstance(approved_reply_ids,frozenset)
                or not approved_reply_ids or not isinstance(recent_ids,tuple)):
            return None
        for reply in self._rows.get(intent_id,()):
            if (reply["id"] in approved_reply_ids and reply["id"] not in recent_ids
                    and reply["context"]==context):
                return StagedSelection(id=reply["id"],text=reply["text"],
                    intent_id=intent_id,context_note=reply["context_note"],stage_path=DELTA)
        return None
