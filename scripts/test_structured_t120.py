"""T120: preserve 65 T118 intents and extend 25 existing T88 intents."""
import hashlib, json
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question
ROOT=Path(__file__).resolve().parents[1]
def main():
    raw=(ROOT/"packs/ru/structured_information_qa.json").read_bytes()
    m=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(p["sha256"] for p in m["packs"] if p["path"]=="packs/ru/structured_information_qa.json")
    p=json.loads(raw)
    assert validate_qa_pack(p)==114
    replies=[v for r in p["records"] for v in [r["answer"],*r["variants"]]]
    assert len(replies)==len({normalize_question(v) for v in replies})==522
    assert sum(len(r["variants"])==4 for r in p["records"])==90
    assert sum(len(r["variants"])==2 for r in p["records"])==24
    assert all(len(r["variants"])==4 for r in p["records"] if r["id"].startswith("struct_t88_"))
    print("T120 PASS: 522 replies total; T118 +130, T120 +50")
if __name__=="__main__":main()
