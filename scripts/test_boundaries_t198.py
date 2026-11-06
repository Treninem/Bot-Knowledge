"""T198: 93 genuinely context-bound RU utterances across 31 existing boundary intents.

Staging only. A consumer must independently approve the exact ID and context.
"""
import json
import re
import unicodedata
from pathlib import Path
from scripts.staged_context_selector import StagedContextSelector

ROOT = Path(__file__).resolve().parents[1]
PATH = "staging/ru/boundaries_t167_context_pool.json"
SECRET = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bearer\s+|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")

def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().replace("ё", "е")
    return " ".join("".join(" " if unicodedata.category(ch)[0] in ("P", "S") else ch
                            for ch in value).split())

def main():
    stage = json.loads((ROOT / PATH).read_text("utf-8"))
    cp = stage["checkpoint"]
    assert stage["consumer_registered"] is False
    assert stage["audiences"] == ["all_ai_bots"]
    assert cp["updated_in"] == "T203" and cp["latest_added"] == 62
    assert cp["added_candidates"] == 1271
    assert cp["registered_count"] == 279
    assert cp["per_intent_staged"] == 41 and cp["per_intent_total"] == 50
    assert cp["remaining_per_intent"] == 50 and cp["remaining_total"] == 1550
    assert cp["partial_intents"] == len(stage["entries"]) == 31
    assert cp["finished_100"] == 0
    selector = StagedContextSelector(ROOT, PATH)
    ids, normalized, newest = set(), set(), []
    for entry in stage["entries"]:
        assert entry["registered_reply_count"] == 9
        assert entry["staged_reply_count"] == len(entry["replies"]) == 41
        recent = [r for r in entry["replies"] if "_t198_" in r["id"]]
        assert [r["id"] for r in recent] == [
            entry["intent_id"] + "_t198_01",
            entry["intent_id"] + "_t198_02",
            entry["intent_id"] + "_t198_03",
        ], entry["intent_id"]
        notes, tokens = set(), []
        for r in entry["replies"]:
            assert r["id"] not in ids
            ids.add(r["id"])
            assert r["language"] == "ru" and r["style"] == "neutral"
            assert r["audiences"] == ["all_ai_bots"] and r["read_only"] is True
            assert r["context"] in ("direct", "private", "group_addressed")
            assert r["context_note"].strip() and r["avoid"].strip()
            assert not SECRET.search(r["text"])
            answer = norm(r["text"])
            note = norm(r["context_note"])
            assert answer and answer not in normalized
            assert note and note not in notes, entry["intent_id"]
            normalized.add(answer)
            notes.add(note)
            tk = set(answer.split())
            for prev in tokens:
                sim = len(prev & tk) / (len(prev | tk) or 1)
                assert sim < .78, (entry["intent_id"], sim)
            tokens.append(tk)
        for r in recent:
            approved = frozenset({r["id"]})
            kwargs = dict(intent_id=entry["intent_id"], approved_reply_ids=approved,
                          audience="all_ai_bots", context=r["context"],
                          addressed=True, local_permission=True)
            assert selector.select(**kwargs).text == r["text"]
            assert selector.select(**{**kwargs, "approved_reply_ids": frozenset()}) is None
            assert selector.select(**{**kwargs, "addressed": False}) is None
            assert selector.select(**{**kwargs, "local_permission": False}) is None
            assert selector.select(**{**kwargs, "audience": "impuls"}) is None
            assert selector.select(**{**kwargs, "context": (
                {"direct", "private", "group_addressed"} - {r["context"]}
            ).pop()}) is None
            newest.append(norm(r["text"]))
    assert len(ids) == len(normalized) == 1271
    assert len(newest) == len(set(newest)) == 93

    # Cross-check only newly authored T198 answers with every registered QA
    # package, not just the nearby source QA pack.
    manifest = json.loads((ROOT / "manifest.json").read_text("utf-8"))
    for p in manifest["packs"]:
        if not p["path"].endswith("_qa.json"):
            continue
        data = json.loads((ROOT / p["path"]).read_text("utf-8"))
        original = {norm(t) for row in data["records"]
                    for t in [row["answer"], *row.get("variants", [])]}
        assert not original.intersection(newest), p["path"]
    print("T198 OK: +93 new scoped RU responses, 31 intents now 48/100; consent and SHA safety")

if __name__ == "__main__":
    main()
