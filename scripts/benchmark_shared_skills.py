"""Measure cold GitHub downloads vs warm local in-memory skill reads.

GitHub is a distribution source, not a per-message database. A slow network
does not fail the local lookup test or imply BotHost is slow/fast.
Run: python scripts/benchmark_shared_skills.py [--offline]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import time
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MAX_MANIFEST_BYTES = 64 * 1024
MAX_PACK_BYTES = 128 * 1024


def load_local() -> tuple[dict, dict]:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    records = {entry["path"]: entry["sha256"] for entry in manifest["packs"]}
    payload = (ROOT / "packs/ru/skills.json").read_bytes()
    assert len(payload) <= MAX_PACK_BYTES, "skills pack too large"
    assert hashlib.sha256(payload).hexdigest() == records["packs/ru/skills.json"], (
        "manifest digest does not match skills package"
    )
    return manifest, json.loads(payload)


def warm_read_benchmark(pack: dict, n: int = 1000) -> dict:
    skills = {skill["id"]: skill for skill in pack["skills"]}
    assert len(skills) == len(pack["skills"]) and len(skills) >= 5
    measurements = []
    for i in range(n):
        started = time.perf_counter_ns()
        choice = skills["support_grief"] if i % 2 else skills["choose_silence"]
        assert choice["id"] in {"support_grief", "choose_silence"}
        measurements.append((time.perf_counter_ns() - started) / 1_000_000)
    measurements.sort()
    return {
        "lookups": n,
        "p50_ms": round(measurements[n // 2], 4),
        "p95_ms": round(measurements[int(n * 0.95)], 4),
        "p99_ms": round(measurements[int(n * 0.99)], 4),
        "max_ms": round(measurements[-1], 4),
    }


def download_limited(url: str, max_bytes: int, timeout: float = 4.0) -> bytes:
    request = Request(url, headers={"User-Agent": "Bot-Knowledge-Benchmark/1.0"})
    with urlopen(request, timeout=timeout) as response:
        content = response.read(max_bytes + 1)
        if len(content) > max_bytes:
            raise ValueError("remote pack exceeds size limit")
        return content


def check_remote(ref: str, local_manifest: dict) -> dict:
    base = f"https://raw.githubusercontent.com/Treninem/Bot-Knowledge/{ref}"
    start = time.perf_counter()
    manifest = json.loads(download_limited(base + "/manifest.json", MAX_MANIFEST_BYTES))
    digest = next(x["sha256"] for x in manifest["packs"]
                  if x["path"] == "packs/ru/skills.json")
    payload = download_limited(base + "/packs/ru/skills.json", MAX_PACK_BYTES)
    assert hashlib.sha256(payload).hexdigest() == digest
    remote_pack = json.loads(payload)
    assert len(remote_pack["skills"]) >= 5
    # A branch under test must match its checked-out manifest.
    assert digest == next(x["sha256"] for x in local_manifest["packs"]
                          if x["path"] == "packs/ru/skills.json")
    return {"cold_http_seconds": round(time.perf_counter() - start, 3),
            "bytes": len(payload), "sha256_verified": True,
            "skill_count": len(remote_pack["skills"])}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--ref", default=os.getenv("GITHUB_HEAD_REF") or "main")
    args = parser.parse_args()
    manifest, pack = load_local()
    assert pack["usage_policy"]["automatic_sanctions_allowed"] is False
    assert pack["usage_policy"]["user_data_allowed"] is False
    local = warm_read_benchmark(pack)
    print("SHARED_KNOWLEDGE_LOCAL_OK", json.dumps(local, ensure_ascii=False), flush=True)
    # Testing local data access <= 3 seconds is meaningful for consumers.
    assert local["max_ms"] < 1000, "unexpectedly slow in-memory lookup"
    if not args.offline:
        try:
            remote = check_remote(args.ref, manifest)
        except Exception as exc:
            print("SHARED_KNOWLEDGE_REMOTE_UNVERIFIED",
                  type(exc).__name__ + ": " + str(exc)[:120], flush=True)
        else:
            print("SHARED_KNOWLEDGE_REMOTE_OK",
                  json.dumps(remote, ensure_ascii=False), flush=True)
            if remote["cold_http_seconds"] > 3.0:
                print("SHARED_KNOWLEDGE_NETWORK_SLOW_USE_CACHE", flush=True)
    print("SHARED_KNOWLEDGE_TEST_FINISHED", flush=True)


if __name__ == "__main__":
    main()
