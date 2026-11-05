"""T122: all previously present structured intents gained one verified reply."""
import hashlib, json
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question
ROOT=Path(__file__).resolve().parents[1]
PATH="packs/ru/structured_information_qa.json"
def main():
    raw=(ROOT/PATH).read_bytes()
    manifest=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    expected=next(x["sha256"] for x in manifest["packs"] if x["path"]==PATH)
    assert hashlib.sha256(raw).hexdigest()==expected
    assert len(raw)<2*1024*1024
    p=json.loads(raw)
    assert validate_qa_pack(p)==114
    assert all(5<=len(r["variants"])<=8 for r in p["records"])
    values=[s for r in p["records"] for s in [r["answer"],*r["variants"]]]
    assert len(values)>=684 and len(values)==len({normalize_question(s) for s in values})
    assert all(r["audiences"]==["all_ai_bots"] for r in p["records"])
    assert all(r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True} for r in p["records"])
    print("T122 PASS: 114 original additions; 114 existing intents at >=6/100")
if __name__=="__main__": main()
