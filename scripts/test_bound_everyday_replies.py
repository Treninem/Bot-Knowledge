"""Guard the reviewed RU/EN everyday-topic bindings and refusal examples."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))


def norm(value):
    return " ".join(re.findall(r"[^\W_]+", value.casefold().replace("ё", "е")))


def load(path):
    raw = (ROOT / path).read_bytes()
    entry = next(x for x in manifest["packs"] if x["path"] == path)
    assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
    return json.loads(raw.decode("utf-8"))


ru = load("packs/ru/reply_catalog.json")
en = load("packs/ru/reply_catalog_en.json")
assert (ru["language"], en["language"]) == ("ru", "en")
assert ru["pack_version"] and en["pack_version"]
assert en["catalog"]["adapter"] == "reply_catalog.v1"
groups = [next(g for s in ru["sets"] if s["id"] == "what_discuss" for g in s["groups"] if g["id"] == "daily"),
          en["sets"][0]["groups"][0]]
all_replies = set()
for group, positive, negative in zip(
    groups,
    ("Давай поговорим о повседневных мелочах", "Let's talk about everyday things"),
    ("Не хочу говорить о повседневном", "I don't want to discuss everyday life"),
):
    binding = group["binding"]
    assert norm(positive) in {norm(x) for x in binding["aliases"]}
    assert norm(negative) in {norm(x) for x in binding["avoid_cues"]}
    assert norm(negative) not in {norm(x) for x in binding["aliases"]}
    assert binding["contexts"] == ["direct", "private", "group_addressed"]
    assert binding["requires_humor"] is False and binding["requires"] == []
    assert len(group["replies"]) >= 4
    for answer in group["replies"]:
        key = norm(answer)
        assert key not in all_replies
        all_replies.add(key)

print("RU/EN reviewed bindings, negative cues, SHA and distinct replies verified")
