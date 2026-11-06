"""T197: 62 original context-specific Russian replies for 31 existing boundary intents.

Read-only staged proposals. Selection requires explicit consumer-approved reply ID.
"""
import json
import re
from pathlib import Path
from scripts.test_boundaries_t195 import norm
from scripts.staged_context_selector import StagedContextSelector

ROOT = Path(__file__).resolve().parents[1]
STAGE = "staging/ru/boundaries_t167_context_pool.json"
PRIVATE = re.compile(r"(?i)(ghp_[a-z0-9]{12,}|sk-[a-z0-9]{12,}|bearer\s+|https://t\.me/|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})")


def main():
    data = json.loads((ROOT / STAGE).read_text(encoding="utf-8"))
    assert data["consumer_registered"] is False
    assert data["checkpoint"]["updated_in"] == "T203"
    assert data["checkpoint"]["added_candidates"] == 1271
    assert data["checkpoint"]["latest_added"] == 62
    assert data["checkpoint"]["per_intent_total"] == 50
    assert data["checkpoint"]["remaining_total"] == 1550
    assert len(data["entries"]) == 31

    selector = StagedContextSelector(ROOT, STAGE)
    all_ids, all_texts, newest = set(), set(), []
    for entry in data["entries"]:
        assert entry["registered_reply_count"] == 9
        assert entry["staged_reply_count"] == len(entry["replies"]) == 41
        recent = [r for r in entry["replies"] if "_t197_" in r["id"]]
        assert len(recent) == 2, entry["intent_id"]
        assert [r["id"] for r in recent] == [
            entry["intent_id"] + "_t197_01",
            entry["intent_id"] + "_t197_02",
        ]
        notes, token_sets = set(), []
        for reply in entry["replies"]:
            assert reply["id"] not in all_ids
            all_ids.add(reply["id"])
            assert reply["read_only"] and reply["audiences"] == ["all_ai_bots"]
            assert reply["language"] == "ru" and reply["style"] == "neutral"
            assert reply["context"] in ("direct", "private", "group_addressed")
            assert not PRIVATE.search(reply["text"])
            normalized, note = norm(reply["text"]), norm(reply["context_note"])
            assert normalized not in all_texts and note and note not in notes
            all_texts.add(normalized)
            notes.add(note)
            tokens = set(normalized.split())
            for earlier in token_sets:
                similarity = len(tokens & earlier) / (len(tokens | earlier) or 1)
                assert similarity < .78, (entry["intent_id"], similarity)
            token_sets.append(tokens)
        for reply in recent:
            kwargs = dict(
                intent_id=entry["intent_id"],
                approved_reply_ids=frozenset({reply["id"]}),
                audience="all_ai_bots",
                context=reply["context"],
                addressed=True,
                local_permission=True,
            )
            assert selector.select(**kwargs).text == reply["text"]
            assert selector.select(**{**kwargs, "approved_reply_ids": frozenset()}) is None
            assert selector.select(**{**kwargs, "addressed": False}) is None
            assert selector.select(**{**kwargs, "local_permission": False}) is None
            assert selector.select(**{**kwargs, "audience": "impuls"}) is None
            newest.append(norm(reply["text"]))
    assert len(all_ids) == len(all_texts) == 1271
    assert len(newest) == len(set(newest)) == 62
    print("T197 OK: 62 T197 scoped proposals preserved, 31 intents now at 50/100; no consumer activation")


if __name__ == "__main__":
    main()
