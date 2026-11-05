"""T121 final coverage checkpoint — still only Draft PR data."""
import hashlib, json
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question
ROOT=Path(__file__).resolve().parents[1]
def main():
    raw=(ROOT/"packs/ru/structured_information_qa.json").read_bytes()
    m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(x["sha256"] for x in m["packs"] if x["path"]=="packs/ru/structured_information_qa.json")
    p=json.loads(raw)
    assert validate_qa_pack(p)==114
    assert all(4 <= len(r["variants"]) <= 8 for r in p["records"])
    answers=[s for r in p["records"] for s in [r["answer"],*r["variants"]]]
    assert len(answers)==len({normalize_question(s) for s in answers}) and len(answers)>=570
    assert all(r["audiences"]==["all_ai_bots"] and r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True} for r in p["records"])
    print("T121 PASS: at least +228 staged answers across 114 intents")
if __name__=="__main__":main()
