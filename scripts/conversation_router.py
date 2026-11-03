"""Offline conservative chat-response router for approved RU/EN knowledge.

This is a deterministic example consumer, not an LLM and not a moderation engine.
No network access, automated sanctions, GitHub writes or user-data storage.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from choose_expression import pick_phrase, load_phrasebook
from interpret_pragmatics import interpret, load as load_pragmatics, norm
from conservative_typo import ConservativeTypoMatcher, Example, SAFE_KINDS, EXCLUDED_IDS

ROOT = Path(__file__).resolve().parents[1]
AUDIENCES = {"all_ai_bots", "chat_moderators", "community_bots"}
LANGUAGES = {"ru", "en"}
TONES = {"neutral", "warm", "casual"}

def verified(root: Path, path: str, manifest: dict) -> dict:
    matches = [x["sha256"] for x in manifest["packs"] if x["path"] == path]
    if len(matches) != 1:
        raise ValueError("Missing or duplicate manifest entry: " + path)
    raw = (root / path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != matches[0]:
        raise ValueError("SHA mismatch: " + path)
    return json.loads(raw.decode("utf-8"))

class ConversationRouter:
    def __init__(self, root: Path = ROOT):
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        # Every source is authenticated by the same local manifest.
        triggers = verified(root, "packs/ru/dialogue_triggers.json", manifest)
        social = verified(root, "packs/ru/social_dialogues.json", manifest)
        english = verified(root, "packs/ru/english_dialogues.json", manifest)
        self.phrases = verified(root, "packs/ru/expression_choices.json", manifest)
        self.pragmatics = verified(root, "packs/ru/pragmatic_contrasts.json", manifest)
        if triggers.get("schema_version") != 1:
            raise ValueError("Unsupported routing schema")
        self.cases = {}
        self.originals = {}
        for case in social["cases"] + english["cases"]:
            if case["id"] in self.cases:
                raise ValueError("Duplicate dialogue case ID")
            self.cases[case["id"]] = case
            language = case.get("language", "ru")
            key = (language, norm(case["input"]))
            if key in self.originals:
                raise ValueError("Duplicate original utterance")
            self.originals[key] = case["id"]
        self.triggers = {}
        self.pair_languages = {}
        for pair in self.pragmatics["pairs"]:
            self.pair_languages.setdefault(norm(pair["expression"]), set()).add(pair["language"])
        for entry in triggers["triggers"]:
            key = (entry["language"], norm(entry["input"]))
            if key in self.triggers or key in self.originals:
                raise ValueError("Duplicate utterance: " + str(key))
            if entry["target_case_id"] not in self.cases:
                raise ValueError("Unknown target case")
            self.triggers[key] = entry
        self.triggers_count = len(self.triggers)
        # Typo-only fallback for benign approved cases. Never approximate
        # permissions, rule statements, profanity, humor or silence requests.
        candidates = []
        for (language, expression), case_id in self.originals.items():
            case = self.cases[case_id]
            if case.get("kind") in SAFE_KINDS and case_id not in EXCLUDED_IDS:
                candidates.append(Example(language, expression, case_id))
        for (language, expression), entry in self.triggers.items():
            case_id = entry["target_case_id"]
            case = self.cases[case_id]
            if (case.get("kind") in SAFE_KINDS and case_id not in EXCLUDED_IDS
                    and not entry["requires_strong_opt_in"]
                    and not entry["requires_dark_opt_in"]
                    and not entry["requires_silence"]):
                candidates.append(Example(language, expression, case_id))
        self.typo_matcher = ConservativeTypoMatcher(candidates)


    @staticmethod
    def _present(text: str, recent: tuple[str, ...]) -> bool:
        return norm(text) in {norm(value) for value in recent}

    def reply(self, message: str, *, language: str = "ru",
              audience: str = "all_ai_bots", addressed: bool = False,
              context: str = "", tone: str = "neutral",
              dark_opt_in: bool = False, strong_opt_in: bool = False,
              sensitive: bool = False, recent: tuple[str, ...] = (),
              allow_typos: bool = True) -> dict:
        if language not in LANGUAGES or audience not in AUDIENCES or tone not in TONES:
            raise ValueError("Unsupported locale, audience or tone")
        if not addressed:
            return {"status": "not_addressed", "text": None}
        key = norm(message)
        if not key:
            return {"status": "empty", "text": None}
        # Explicit language choice must not accidentally route to the opposite-language example.
        if key in self.pair_languages and language not in self.pair_languages[key]:
            return {"status": "wrong_language", "text": None}
        # Ambiguous expressions must not fall through into a cheerful template.
        p = interpret(self.pragmatics, message, context, audience)
        if p["status"] == "needs_context" or p["status"] == "ambiguous_expression":
            return {"status": "needs_context", "text": None}
        if p["status"] == "example_match":
            if p["decision"] == "human_review":
                return {"status": "review_required", "text": None}
            text = p["response"]
            if self._present(text, recent):
                return {"status": "repeat_suppressed", "text": None}
            return {"status": "ok", "text": text, "source_id": p["pair_id"], "route": "pragmatics"}
        trigger = self.triggers.get((language, key))
        case_id = trigger["target_case_id"] if trigger else self.originals.get((language, key))
        typo_routed = False
        if not case_id and allow_typos:
            approximate = self.typo_matcher.match(message, language)
            if approximate["status"] == "ambiguous":
                return {"status": "needs_clarification", "text": None}
            if approximate["status"] == "match":
                case_id = approximate["case_id"]
                trigger = self.triggers.get((language, approximate["source"]))
                typo_routed = True
        if not case_id:
            return {"status": "unknown_input", "text": None}
        case = self.cases[case_id]
        if not ("all_ai_bots" in case["audiences"] or audience in case["audiences"]):
            return {"status": "scope_denied", "text": None}
        # Local public cases do not authorize sanctions and cannot grant permissions.
        if trigger and trigger["requires_silence"] or case_id == "talk_stop_when_asked":
            return {"status": "silence_requested", "text": None}
        needs_dark = bool(trigger and trigger["requires_dark_opt_in"]) or case.get("kind") == "dark_humor" or case_id in {"talk_dark_deadline", "talk_dark_bureaucracy", "talk_dark_alarmclock"}
        needs_strong = bool(trigger and trigger["requires_strong_opt_in"]) or case_id in {"talk_consensual_strong_tone", "en_profanity_requested"}
        if sensitive and (needs_dark or needs_strong or case.get("kind") in {"humor", "profanity"}):
            return {"status": "sensitive_suppressed", "text": None}
        if needs_dark and not dark_opt_in:
            return {"status": "requires_dark_opt_in", "text": None}
        if needs_strong and not strong_opt_in:
            return {"status": "requires_strong_opt_in", "text": None}
        if trigger and trigger["fallback_expression_id"] and tone != "neutral":
            alternative = pick_phrase(
                self.phrases, scenario=trigger["fallback_expression_id"],
                language=language, tone=tone, dark_opt_in=dark_opt_in,
                strong_opt_in=strong_opt_in, sensitive=sensitive,
                recent_phrases=recent
            )
            if alternative["status"] == "ok":
                return {"status": "ok", "text": alternative["text"],
                        "source_id": trigger["fallback_expression_id"], "route": "tone"}
        text = case["response"]
        if self._present(text, recent):
            if trigger and trigger["fallback_expression_id"]:
                alternative = pick_phrase(
                    self.phrases, scenario=trigger["fallback_expression_id"],
                    language=language, tone=tone, dark_opt_in=dark_opt_in,
                    strong_opt_in=strong_opt_in, sensitive=sensitive,
                    recent_phrases=recent
                )
                if alternative["status"] == "ok":
                    return {"status": "ok", "text": alternative["text"],
                            "source_id": trigger["fallback_expression_id"], "route": "alternative"}
            return {"status": "repeat_suppressed", "text": None}
        return {"status": "ok", "text": text, "source_id": case_id,
                "route": "typo" if typo_routed else ("trigger" if trigger else "original")}

def main() -> None:
    parser = argparse.ArgumentParser(description="Safe local RU/EN response router")
    parser.add_argument("--message", required=True)
    parser.add_argument("--context", default="")
    parser.add_argument("--language", choices=sorted(LANGUAGES), default="ru")
    parser.add_argument("--audience", choices=sorted(AUDIENCES), default="all_ai_bots")
    parser.add_argument("--tone", choices=sorted(TONES), default="neutral")
    parser.add_argument("--addressed", action="store_true")
    parser.add_argument("--dark-opt-in", action="store_true")
    parser.add_argument("--strong-opt-in", action="store_true")
    parser.add_argument("--sensitive", action="store_true")
    parser.add_argument("--no-typos", action="store_true")
    args = parser.parse_args()
    result = ConversationRouter().reply(
        args.message, language=args.language, audience=args.audience,
        context=args.context, tone=args.tone, addressed=args.addressed,
        dark_opt_in=args.dark_opt_in, strong_opt_in=args.strong_opt_in,
        sensitive=args.sensitive, allow_typos=not args.no_typos
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
