"""T125 additive dialogue answers, original IDs and scope (offline)."""
import hashlib,json
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack,normalize_question
ROOT=Path(__file__).resolve().parents[1]
def main():
 raw=(ROOT/"packs/ru/dialogue_help_qa.json").read_bytes()
 m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
 assert hashlib.sha256(raw).hexdigest()==next(z["sha256"] for z in m["packs"] if z["path"]=="packs/ru/dialogue_help_qa.json")
 p=json.loads(raw);assert validate_qa_pack(p)==790
 assert p["records"][0]["id"]=="dlg_greet_no_rules" and len(p["records"][0]["variants"])==8
 assert all(len(r["variants"])>=4 for r in p["records"][1:30])
 assert len({r["id"] for r in p["records"]})==790
 seen=set()
 for r in p["records"]:
  assert all((r.get("constraints") or p["catalog"]["constraints"])[k] for k in ("read_only","requires_direct_address","no_personal_data"))
  for s in [r["answer"],*r["variants"]]:
   key=normalize_question(s);assert key not in seen,("duplicate",r["id"]);seen.add(key)
 print("T125 PASS: 30 existing intents, +64 replies, greeting 9/100, SHA/uniqueness")
if __name__=="__main__":main()
