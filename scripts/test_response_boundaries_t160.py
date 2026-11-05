"""T160: new universal response-boundary QA, SHA, exact/near duplicates and scope."""
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
 assert all(len(r["variants"])==5 for r in rows)
 assert all(r["audiences"]==["all_ai_bots"] and set(r["contexts"])=={"direct","private","group_addressed"} for r in rows)
 assert all(r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True} for r in rows)
 assert all(r["source"].endswith("/AGENTS.md") for r in rows)
 replies=[s for r in rows for s in [r["answer"],*r["variants"]]]
 assert len(replies)==186 and len({norm(s) for s in replies})==186
 assert not any(re.search(r"(?i)(ghp_|sk-|bot_token|chat_id|user_id|bearer\\s+)",s) for s in replies)
 assert all(normalize_question(r["question"]) for r in rows)
 print("T160 PASS: 31 new intents, 186 distinct RU replies, manifest SHA, scopes")
if __name__=="__main__":main()
