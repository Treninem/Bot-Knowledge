"""Execute 50 RU/EN reference cases and negative safety probes."""
from __future__ import annotations
import sys
import tempfile
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from resolve_referents import resolve,load_examples,norm

def main() -> None:
    cases=load_examples()
    assert len(cases)==50
    assert sum(c["language"]=="ru" for c in cases)==25
    assert sum(c["language"]=="en" for c in cases)==25
    assert len({c["id"] for c in cases})==50
    assert len({norm(c["input"]) for c in cases})==50
    for c in cases:
        result=resolve(c["input"],c["candidates"],language=c["language"],addressed=c["addressed"])
        assert result=={"status":c["expected_status"],"ids":c["expected_ids"]},(c["id"],result)
        assert resolve(c["input"],c["candidates"],language=c["language"],addressed=False)=={"status":"not_addressed","ids":[]}
    ru=[{"id":"a","label":"вариант альфа","gender":"m"},{"id":"b","label":"вариант бета","gender":"m"}]
    en=[{"id":"a","label":"draft alpha","gender":"u"},{"id":"b","label":"draft beta","gender":"u"}]
    assert resolve("Покажи второго",ru,addressed=True)["ids"]==["b"]
    assert resolve("Send 2nd",en,language="en",addressed=True)["ids"]==["b"]
    assert resolve("Нет, не первый, а второй",ru,addressed=True)["ids"]==["b"]
    assert resolve("Not the first but the second",en,language="en",addressed=True)["ids"]==["b"]
    assert resolve("Compare the first and the second",en,language="en",addressed=True)["ids"]==["a","b"]
    assert resolve("Сравни первый и второй",ru,addressed=True)["ids"]==["a","b"]
    assert resolve("Don't delete the first",en,language="en",addressed=True)["status"]=="negated_instruction"
    assert resolve("Не отправляй первый",ru,addressed=True)["status"]=="negated_instruction"
    assert resolve("Show the first",en,language="en",addressed=True,require_confirmation=True)["status"]=="confirm_required"
    assert resolve("Открой первый и второй",ru,addressed=True)["status"]=="needs_clarification"
    assert resolve("Show both",en+[{"id":"c","label":"draft gamma","gender":"u"}],language="en",addressed=True)["status"]=="needs_clarification"
    for invalid in (
      [{"id":"a","label":"план","gender":"m"},{"id":"a","label":"смета","gender":"f"}],
      [{"id":"a","label":"план","gender":"m"},{"id":"b","label":"ПЛАН","gender":"m"}],
      [{"id":"a","label":"план","gender":"invalid"}],
      [{"id":"../../bad","label":"план","gender":"m"}],
      [{"id":"z","label":"","gender":"m"}],
    ):
        try:
            resolve("Выбери первый",invalid,addressed=True)
            raise AssertionError("Bad candidate was accepted")
        except ValueError:
            pass
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory)
        (root/"packs/ru").mkdir(parents=True)
        (root/"manifest.json").write_bytes((ROOT/"manifest.json").read_bytes())
        (root/"packs/ru/referent_resolution.json").write_bytes((ROOT/"packs/ru/referent_resolution.json").read_bytes()+b" ")
        try:
            load_examples(root)
            raise AssertionError("Tampered SHA passed")
        except ValueError as exc:
            assert "SHA-256" in str(exc)
    start=time.perf_counter()
    for n in range(1,11):
        for c in cases:
            r=resolve(c["input"],c["candidates"],language=c["language"],addressed=c["addressed"])
            assert (r["status"],r["ids"])==(c["expected_status"],c["expected_ids"])
        print(f"REFERENT_PASS {n}/10 cases=50")
    for _ in range(1000):
        resolve("Покажи второй",ru,addressed=True)
    print(f"REFERENT_RESOLUTION_OK cases=50 elapsed_and_1000_ms={(time.perf_counter()-start)*1000:.2f}")

if __name__=="__main__":
    main()
