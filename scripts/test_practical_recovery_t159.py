"""T159: 24 practical intents × 9 scoped replies; exact manifest SHA and no repetition."""
import hashlib,json,re,unicodedata
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack
ROOT=Path(__file__).resolve().parents[1]
REL="packs/ru/practical_recovery_qa.json"
def norm(s):
 s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
 return " ".join("".join(" " if unicodedata.category(c)[0] in ("P","S") else c for c in s).split())
def main():
 raw=(ROOT/REL).read_bytes()
 data=json.loads(raw)
 manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
 assert hashlib.sha256(raw).hexdigest()==next(x["sha256"] for x in manifest["packs"] if x["path"]==REL)
 assert validate_qa_pack(data)==24
 records=data["records"]
 assert len({r["id"] for r in records})==24
 assert all(len(r["variants"])==8 for r in records)
 replies=[t for r in records for t in [r["answer"],*r["variants"]]]
 assert len(replies)==216 and len({norm(t) for t in replies})==216
 assert all(r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True} for r in records)
 assert all(r["audiences"]==["all_ai_bots"] and set(r["contexts"])=={"direct","private","group_addressed"} for r in records)
 assert not any(re.search(r"(?i)(ghp_|sk-|bot_token|chat_id|user_id|bearer\\s+)",t) for t in replies)
 print("T159 PASS: 24 intents × 9 = 216 answers, SHA, privacy, context")
if __name__=="__main__":main()
