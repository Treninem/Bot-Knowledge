"""T158 registered practical recovery QA: exact SHA, scopes and uniqueness."""
import hashlib, json, re, unicodedata
from pathlib import Path
from scripts.validate_qa_v1 import validate_qa_pack
ROOT=Path(__file__).resolve().parents[1]
PATH="packs/ru/practical_recovery_qa.json"
def norm(s):
    s=unicodedata.normalize("NFKC",s).casefold().replace("ё","е")
    return " ".join("".join(" " if unicodedata.category(c)[0] in ("P","S") else c for c in s).split())
def main():
    raw=(ROOT/PATH).read_bytes()
    pack=json.loads(raw)
    mf=json.loads((ROOT/"manifest.json").read_text("utf-8"))
    assert hashlib.sha256(raw).hexdigest()==next(v["sha256"] for v in mf["packs"] if v["path"]==PATH)
    assert validate_qa_pack(pack)==24
    rows=pack["records"]
    assert len({r["id"] for r in rows})==24
    assert all(r["id"].startswith("bk_recovery_") and len(r["variants"])==4 for r in rows)
    assert all(r["audiences"]==["all_ai_bots"] and set(r["contexts"])=={"direct","private","group_addressed"} for r in rows)
    assert all(r["constraints"]=={"read_only":True,"requires_direct_address":True,"no_personal_data":True} for r in rows)
    ans=[a for r in rows for a in [r["answer"],*r["variants"]]]
    assert len(ans)==120 and len({norm(a) for a in ans})==120
    assert not any(re.search(r"(?i)(ghp_|sk-|bot_token|chat_id|user_id|bearer\\s+)",a) for a in ans)
    print("T158 PASS: 24 questions, 120 RU replies, SHA, scopes, uniqueness")
if __name__=="__main__":main()
