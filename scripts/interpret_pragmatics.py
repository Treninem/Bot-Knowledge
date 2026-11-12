"""Conservative contrastive lookup for exact expressions and explicit context cues.

This small deterministic matcher is not an LLM and does not infer arbitrary intent.
No network, moderation action, user profiles or third-party dependencies.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIENCES = {"all_ai_bots", "chat_moderators", "community_bots"}

def norm(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return " ".join(re.findall(r"[a-zа-яё0-9]+", normalized))

def load(root: Path = ROOT) -> dict:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    rel = "packs/ru/pragmatic_contrasts.json"
    sha = [p["sha256"] for p in manifest["packs"] if p["path"] == rel]
    if len(sha) != 1:
        raise ValueError("Missing or duplicate contrast pack entry")
    data = (root / rel).read_bytes()
    if hashlib.sha256(data).hexdigest() != sha[0]:
        raise ValueError("Contrast SHA mismatch")
    book = json.loads(data.decode("utf-8"))
    if book.get("schema_version") != 1:
        raise ValueError("Unsupported schema")
    return book

def interpret(book: dict, utterance: str, context: str = "",
              audience: str = "all_ai_bots") -> dict:
    if audience not in AUDIENCES:
        raise ValueError("Unsupported audience")
    target = norm(utterance)
    if not target:
        return {"status": "unrecognized", "response": None}
    matches = [p for p in book["pairs"] if norm(p["expression"]) == target
               and ("all_ai_bots" in p["audiences"] or audience in p["audiences"])]
    if not matches:
        return {"status": "unrecognized", "response": None}
    if len(matches) != 1:
        return {"status": "ambiguous_expression", "response": None}
    pair = matches[0]
    context_terms = " " + norm(context) + " "
    matched = [[norm(cue) for cue in reading["cues"] if (" " + norm(cue) + " ") in context_terms] for reading in pair["readings"]]
    # Discount weaker overlapping cues: "audit log" inside "no reliable audit log".
    scores = [sum(not any(cue != other and (" " + cue + " ") in (" " + other + " ") for j, others in enumerate(matched) if j != i for other in others) for cue in hits) for i, hits in enumerate(matched)]
    # Two *different* cues are required; if opposing evidence appears, abstain.
    if max(scores) < 2 or sum(x > 0 for x in scores) > 1:
        return {"status": "needs_context", "pair_id": pair["id"], "response": None,
                "possible_interpretations": [r["meaning"] for r in pair["readings"]]}
    winner = pair["readings"][scores.index(max(scores))]
    return {"status": "example_match", "pair_id": pair["id"], "tag": winner["tag"],
            "meaning": winner["meaning"], "decision": winner["decision"],
            "response": winner["suggested_response"],
            "notice": "Examples only; caller must independently verify local policy and context."}

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--utterance", required=True)
    parser.add_argument("--context", default="")
    parser.add_argument("--audience", choices=sorted(AUDIENCES), default="all_ai_bots")
    args = parser.parse_args()
    print(json.dumps(interpret(load(), args.utterance, args.context, args.audience),
                     ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
