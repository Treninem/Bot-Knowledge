"""Regression tests for privacy guardrails. All identifiers are synthetic."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from prepare_knowledge_candidate import validate, SUSPICIOUS

def example() -> dict:
    return {
        "candidate_id": "synthetic_phrase_context_one",
        "statement": "Не считать цитату наказуемой без анализа контекста и утверждённого правила.",
        "when": ["сообщение цитирует чужую реплику для обсуждения"],
        "avoid": ["участник сам направляет оскорбление собеседнику"],
        "audiences": ["chat_moderators"],
        "origin": "synthetic",
        "reviewed": True,
    }

def rejected(obj: dict) -> None:
    try:
        validate(obj)
    except (TypeError, ValueError):
        return
    raise AssertionError("Unsafe candidate was accepted: " + repr(obj["candidate_id"]))

def main() -> None:
    assert validate(example())["origin"] == "synthetic"
    bad = example()
    bad["statement"] += " " + "https://" + "example.invalid" + "/private"
    rejected(bad)
    bad = example()
    bad["statement"] += " " + "sample" + "@" + "example.invalid"
    rejected(bad)
    bad = example()
    bad["statement"] += " " + "1234567890123456"
    rejected(bad)
    bad = example()
    bad["statement"] += " " + "api_key" + "=" + "syntheticvalue"
    rejected(bad)
    bad = example()
    bad["statement"] += " " + "password" + ": " + "syntheticvalue"
    rejected(bad)
    bad = example()
    bad["reviewed"] = False
    rejected(bad)
    bad = example()
    bad["audiences"] = ["all_ai_bots", "unknown_role"]
    rejected(bad)
    bad = example()
    bad["raw_message"] = "synthetic test content"
    rejected(bad)
    bad = example()
    bad["origin"] = "raw_chat"
    rejected(bad)
    good = example()
    good["statement"] += " Пример со сроком в 2026 году допустим."
    assert validate(good)
    tests = [("https://" + "example.invalid", True),
             ("person" + "@" + "example.invalid", True),
             ("123456789012345", True),
             ("token" + "=" + "dummy", True),
             ("1234", False), ("отрицание и цитата", False)]
    for sample, expected in tests:
        assert any(p.search(sample) for p in SUSPICIOUS) == expected, sample
    for i in range(1, 11):
        assert validate(example())
        print(f"CANDIDATE_PRIVACY_PASS {i}/10")
    print("CANDIDATE_PRIVACY_10_ROUNDS_OK")

if __name__ == "__main__":
    main()
