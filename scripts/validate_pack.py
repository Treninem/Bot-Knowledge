from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_KEYS = {
    "user_id", "chat_id", "telegram_id", "username", "phone", "email",
    "token", "cookie", "password", "secret", "first_name", "last_name",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def walk_keys(value, path="root"):
    if isinstance(value, dict):
        for key, item in value.items():
            yield path, str(key).lower()
            yield from walk_keys(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk_keys(item, f"{path}[{index}]")


def main() -> int:
    errors: list[str] = []
    manifest_path = ROOT / "manifest.json"
    manifest = read_json(manifest_path)

    if manifest.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if manifest.get("language") != "ru":
        errors.append("language must be ru")

    packs = manifest.get("packs")
    if not isinstance(packs, list) or not packs:
        errors.append("manifest.packs must be a non-empty list")
        packs = []

    for item in packs:
        if not isinstance(item, dict):
            errors.append("manifest pack entry must be an object")
            continue
        relative = str(item.get("path", ""))
        if not relative.startswith("packs/ru/") or ".." in Path(relative).parts:
            errors.append(f"unsafe pack path: {relative}")
            continue
        path = ROOT / relative
        if not path.exists():
            errors.append(f"missing pack: {relative}")
            continue
        payload = path.read_bytes()
        actual = hashlib.sha256(payload).hexdigest()
        expected = str(item.get("sha256", ""))
        if actual != expected:
            errors.append(f"sha256 mismatch: {relative}: expected {expected}, got {actual}")
        try:
            data = json.loads(payload.decode("utf-8"))
        except Exception as exc:
            errors.append(f"invalid JSON: {relative}: {exc}")
            continue
        for location, key in walk_keys(data):
            if key in FORBIDDEN_KEYS:
                errors.append(f"forbidden personal/secret key {key!r} in {relative} at {location}")

    intents_path = ROOT / "packs/ru/intents.json"
    if intents_path.exists():
        data = read_json(intents_path)
        intents = data.get("intents")
        if not isinstance(intents, list) or not intents:
            errors.append("intents.json must contain non-empty intents list")
        else:
            ids = []
            for item in intents:
                if not isinstance(item, dict):
                    errors.append("each intent must be an object")
                    continue
                intent_id = str(item.get("id", "")).strip()
                if not intent_id:
                    errors.append("intent without id")
                    continue
                ids.append(intent_id)
                examples = item.get("examples")
                if not isinstance(examples, list) or not examples:
                    errors.append(f"intent {intent_id} has no examples")
            if len(ids) != len(set(ids)):
                errors.append("duplicate intent ids")

    skills_path = ROOT / "packs/ru/skills.json"
    if skills_path.exists():
        payload = skills_path.read_bytes()
        if len(payload) > 128 * 1024:
            errors.append("skills pack exceeds 128 KiB")
        data = read_json(skills_path)
        policy = data.get("usage_policy", {})
        if (data.get("schema_version") != 1
                or data.get("language") != "ru"
                or not isinstance(policy, dict)
                or policy.get("user_data_allowed") is not False
                or policy.get("automatic_sanctions_allowed") is not False
                or policy.get("initiative_requires_local_authorization") is not True):
            errors.append("skills policy must forbid personal data, automatic sanctions and unauthorized initiative")
        skills = data.get("skills")
        if not isinstance(skills, list) or not skills:
            errors.append("skills pack must contain a nonempty list")
        else:
            seen = set()
            for skill in skills:
                if not isinstance(skill, dict):
                    errors.append("invalid skills entry")
                    continue
                skill_id = skill.get("id")
                if not isinstance(skill_id, str) or not skill_id.isascii() or not skill_id.replace("_", "").isalnum():
                    errors.append("invalid skill id")
                if skill_id in seen:
                    errors.append("duplicate skill id")
                seen.add(skill_id)
                if skill.get("kind") not in {"social", "bot_help", "moderation_language"}:
                    errors.append("unsupported skill kind")
                for field in ("when", "avoid", "examples"):
                    items = skill.get(field)
                    if not isinstance(items, list) or len(items) > 12 or any(
                        not isinstance(item, str) or not 1 <= len(item) <= 300 for item in items
                    ):
                        errors.append(f"invalid skill field {field}")
                if "action" in skill or "auto_apply" in skill:
                    errors.append("skill must not contain executable/action fields")
                audiences = skill.get("audiences")
                if (not isinstance(audiences, list) or not audiences
                        or len(audiences) > 5 or any(
                            item not in {"all_ai_bots", "chat_moderators", "community_bots"}
                            for item in audiences
                        )):
                    errors.append("invalid skill audience selection")
                if skill.get("kind") == "moderation_language" and "all_ai_bots" in (audiences or []):
                    errors.append("chat-specific moderation must not be treated as general AuroraFox knowledge")
                if skill.get("kind") == "bot_help" and "all_ai_bots" in (audiences or []):
                    errors.append("bot-specific help must not be treated as general AuroraFox knowledge")


    context_path = ROOT / "packs/ru/context_cases.json"
    if context_path.exists():
        data = read_json(context_path)
        if data.get("schema_version") != 1 or data.get("language") != "ru":
            errors.append("invalid context case pack metadata")
        cases = data.get("cases")
        if not isinstance(cases, list) or not cases or len(cases) > 1000:
            errors.append("invalid context cases list")
        else:
            ids, seen_inputs = set(), set()
            allowed = {"answer", "clarify", "abstain", "human_review", "refuse_claim"}
            for case in cases:
                if not isinstance(case, dict):
                    errors.append("context case must be an object")
                    continue
                case_id, decision = case.get("id"), case.get("decision")
                if not isinstance(case_id, str) or not case_id.isascii() or not case_id.replace("_","").isalnum() or case_id in ids:
                    errors.append("invalid or duplicate context case id")
                ids.add(case_id)
                if decision not in allowed:
                    errors.append(f"invalid context decision: {case_id}")
                source = case.get("input")
                if not isinstance(source, str) or not 4 <= len(source) <= 300:
                    errors.append(f"invalid context input: {case_id}")
                else:
                    key = " ".join(source.casefold().split())
                    if key in seen_inputs:
                        errors.append(f"repeated context input: {case_id}")
                    seen_inputs.add(key)
                for field in ("context", "expected_behavior", "forbidden_behavior"):
                    value = case.get(field)
                    if not isinstance(value, str) or not 4 <= len(value) <= 300:
                        errors.append(f"invalid context {field}: {case_id}")
                audiences = case.get("audiences")
                if not isinstance(audiences,list) or not audiences or not set(audiences) <= {"all_ai_bots","chat_moderators","community_bots"}:
                    errors.append(f"invalid context audiences: {case_id}")
                if case.get("category") in {"moderation_semantics", "permissions"} and "all_ai_bots" in (audiences or []):
                    errors.append(f"cross-product permission leak in {case_id}")
                if "action" in case or "auto_apply" in case:
                    errors.append(f"executable field forbidden in {case_id}")

    # New bilingual reference examples are executable test vectors, not powers to act.
    referent_path=ROOT/"packs/ru/referent_resolution.json"
    if referent_path.exists():
        referents=read_json(referent_path)
        needed={"synthetic_examples_only":True,"personal_data_allowed":False,
                "automatic_actions_allowed":False,"automatic_sanctions_allowed":False,
                "caller_supplies_context":True,"explicit_address_required":True}
        if referents.get("schema_version")!=1 or referents.get("language")!="multilingual" or referents.get("usage_policy")!=needed:
            errors.append("unsafe referent schema/policy")
        cases=referents.get("cases")
        if not isinstance(cases,list) or len(cases)!=50:
            errors.append("referent pack must have 50 validated cases")
        else:
            seen_ids,seen_inputs=set(),set()
            allowed={"resolved","needs_clarification","no_match","not_direct_request",
                     "confirm_required","negated_instruction","no_context","not_addressed"}
            for case in cases:
                cid,inp=case.get("id"),case.get("input")
                if not isinstance(cid,str) or not cid.isascii() or not cid.replace("_","").isalnum() or cid in seen_ids:
                    errors.append("duplicate or invalid referent ID")
                seen_ids.add(cid)
                if not isinstance(inp,str) or not 4<=len(inp)<=300:
                    errors.append("invalid referent input")
                    continue
                import re
                key=" ".join(re.findall(r"[a-zа-яё0-9]+",inp.casefold().replace("ё","е")))
                if key in seen_inputs:
                    errors.append("duplicate normalized referent phrase")
                seen_inputs.add(key)
                if case.get("language") not in {"ru","en"} or case.get("expected_status") not in allowed or case.get("audiences")!=["all_ai_bots"] or case.get("addressed") is not True:
                    errors.append("invalid referent language, audience or status")
                options=case.get("candidates")
                if not isinstance(options,list) or len(options)>12:
                    errors.append("invalid candidate set")
                    continue
                ids,labels=set(),set()
                for opt in options:
                    if not isinstance(opt,dict) or set(opt)!={"id","label","gender"}:
                        errors.append("invalid candidate shape")
                        continue
                    if opt["id"] in ids or not isinstance(opt["label"],str) or opt["label"].casefold() in labels or opt["gender"] not in {"m","f","n","u"}:
                        errors.append("duplicate or invalid candidate label")
                    ids.add(opt["id"]); labels.add(opt["label"].casefold())
                expected=case.get("expected_ids")
                if not isinstance(expected,list) or len(expected)!=len(set(expected)) or not set(expected)<=ids:
                    errors.append("invalid expected candidate ids")
                    continue
                if bool(expected)!=(case["expected_status"] in {"resolved","confirm_required"}):
                    errors.append("unresolved or successful case with contradictory expected IDs")


    from validate_paraphrases import validate_paraphrase_pack
    errors.extend(validate_paraphrase_pack(ROOT))

    from validate_word_nuances import validate_word_nuances_pack
    errors.extend(validate_word_nuances_pack(ROOT))

    if errors:
        print("Bot-Knowledge validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Bot-Knowledge validation: OK ({manifest.get('knowledge_version')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
