"""T123: the 114 preserved structural questions have seven different staged answers each."""
import hashlib,json
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question
ROOT=Path(__file__).resolve().parents[1]
PATH="packs/ru/structured_information_qa.json"
def main():
    raw=(ROOT/PATH).read_bytes()
    manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(x["sha256"] for x in manifest["packs"] if x["path"]==PATH)
    p=json.loads(raw)
    assert validate_qa_pack(p)==114
    assert all(6<=len(r["variants"])<=8 for r in p["records"])
    replies=[v for r in p["records"] for v in [r["answer"], *r["variants"]]]
    assert len(replies)>=798 and len(replies)==len({normalize_question(r) for r in replies})
    assert all(r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True} for r in p["records"])
    print("T123 PASS: 114 new staged replies; 114 intents at >=7/100")
if __name__=="__main__": main()
