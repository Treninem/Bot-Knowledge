"""Local conservative RU/EN reference selection over caller-supplied context.

Only returns opaque candidate IDs. Never acts, moderates, accesses other chats,
persists user data, changes permissions or contacts any server.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORD = {
 "ru": {**dict.fromkeys(("первый","первую","первого","первом","первым"),0),
        **dict.fromkeys(("второй","вторую","второго","втором","вторым"),1),
        **dict.fromkeys(("третий","третью","третьего","третьем","третьим"),2),
        **dict.fromkeys(("четвертый","четвертую","четвертого","четвертом"),3),
        **dict.fromkeys(("последний","последнего","последнюю"),-1)},
 "en":{"first":0,"second":1,"third":2,"fourth":3,"last":-1,
       "1st":0,"2nd":1,"3rd":2,"4th":3}
}
VERBS={
 "ru":{"покажи","покажите","исправь","исправьте","открой","откройте","пришли","пришлите",
       "сравни","сравните","выбери","выберите","переведи","переведите","перепиши",
       "перепишите","измени","измените","удали","удалите","отправь","отправьте"},
 "en":{"show","edit","open","send","compare","choose","pick","select",
       "rewrite","translate","change","update","delete","remove","make"}
}
ALL={"ru":{"все","всех","каждый"},"en":{"all","every","everything"}}
BOTH={"ru":{"оба","обе"},"en":{"both"}}
DESTRUCTIVE={"удали","удалите","сотри","уничтожь","delete","remove","erase","destroy"}
PREFACE={"ru":("в тексте","в цитате","он сказал","она сказала","в сообщении"),
         "en":("they wrote","he said","she said","the quote","the message says")}
GENDER={"m","f","n","u"}

def norm(value: str) -> str:
    if not isinstance(value,str):
        raise ValueError("Text expected")
    return " ".join(re.findall(r"[a-zа-яё0-9]+",
        unicodedata.normalize("NFKC",value).casefold().replace("ё","е")))

def validate_candidates(candidates: list[dict]) -> None:
    if not isinstance(candidates,list) or len(candidates)>12:
        raise ValueError("At most 12 candidates allowed")
    ids,labels=set(),set()
    for c in candidates:
        if not isinstance(c,dict) or set(c)!={"id","label","gender"}:
            raise ValueError("Invalid candidate fields")
        i,key=c["id"],norm(c["label"])
        if (not isinstance(i,str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,31}",i)
                or i in ids or not key or len(key)>100 or key in labels or c["gender"] not in GENDER):
            raise ValueError("Invalid or duplicate candidate")
        ids.add(i)
        labels.add(key)

def load_examples(root: Path=ROOT) -> list[dict]:
    manifest=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    rel="packs/ru/referent_resolution.json"
    entries=[p["sha256"] for p in manifest["packs"] if p["path"]==rel]
    if len(entries)!=1:
        raise ValueError("Missing or duplicate manifest entry")
    raw=(root/rel).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=entries[0]:
        raise ValueError("SHA-256 mismatch")
    data=json.loads(raw.decode("utf-8"))
    if data.get("schema_version")!=1 or data.get("language")!="multilingual":
        raise ValueError("Unsupported reference schema")
    return data["cases"]

def _scan(phrase: str, candidates: list[dict], language: str) -> tuple[set[int],bool,bool]:
    tokens=set(phrase.split())
    selected=set()
    out_of_range=False
    for word in tokens:
        if word not in ORD[language]:
            continue
        rank=ORD[language][word]
        index=len(candidates)-1 if rank==-1 else rank
        if 0<=index<len(candidates):
            selected.add(index)
        else:
            out_of_range=True
    for i,c in enumerate(candidates):
        label=norm(c["label"])
        forms={label}
        if language=="ru":
            parts=label.split()
            last=parts[-1]
            # Limited noun-case equivalence for explicit, caller-provided labels.
            # Full-word forms only: never match arbitrary substrings or unknown words.
            if len(last)>=4 and last.endswith("а"):
                forms.update(" ".join(parts[:-1]+[last[:-1]+end])
                             for end in ("у","е","ы","ой"))
            elif len(last)>=4 and last.endswith("я"):
                forms.update(" ".join(parts[:-1]+[last[:-1]+end])
                             for end in ("ю","и","е","ей"))
        if any((" "+form+" ") in (" "+phrase+" ") for form in forms):
            selected.add(i)
    if selected or out_of_range:
        return selected,out_of_range,False
    if language=="ru":
        masc="его" in tokens
        fem="ее" in tokens
        if masc!=fem and all(c["gender"]!="u" for c in candidates):
            wanted={"m","n"} if masc else {"f"}
            return {i for i,c in enumerate(candidates) if c["gender"] in wanted},False,True
        pronoun=bool(tokens.intersection({"это","этот","ту","тот","той","их","его","ее","другой","другую"}))
    else:
        pronoun=bool(tokens.intersection({"it","this","that","them","those","other"}))
    if pronoun and len(candidates)==1:
        return {0},False,True
    return set(),False,pronoun

def resolve(message: str,candidates: list[dict],*,language: str="ru",
            addressed: bool=False,require_confirmation: bool=False) -> dict:
    if language not in ORD:
        raise ValueError("Unsupported language")
    validate_candidates(candidates)
    if not addressed:
        return {"status":"not_addressed","ids":[]}
    if not candidates:
        return {"status":"no_context","ids":[]}
    if not isinstance(message,str) or len(message)>500:
        raise ValueError("Invalid input length")
    phrase=norm(message)
    if not phrase:
        return {"status":"unrecognized","ids":[]}
    if any(phrase.startswith(p+" ") or phrase==p for p in PREFACE[language]):
        return {"status":"not_direct_request","ids":[]}
    words=set(phrase.split())
    if language=="ru":
        negated=re.search(r"(?:^| )(?:не|никогда не) (?:удаляй|удалите|отправляй|изменяй|исправляй|выбирай|открывай)(?: |$)",phrase)
    else:
        negated=re.search(r"(?:^| )(?:do not|don t|never) (?:delete|remove|edit|send|open|choose|select|update)(?: |$)",phrase)
    if negated:
        return {"status":"negated_instruction","ids":[]}
    pattern=(r"(?:^| )не (.+?) а (.+)$" if language=="ru" else
             r"(?:^| )not (.+?) (?:but|instead) (.+)$")
    correction=re.search(pattern,phrase)
    if correction:
        rejected,r_bad,_=_scan(correction.group(1),candidates,language)
        accepted,a_bad,_=_scan(correction.group(2),candidates,language)
        if r_bad or a_bad or len(rejected)!=1 or len(accepted)!=1 or rejected==accepted:
            return {"status":"needs_clarification","ids":[]}
        choice=sorted(accepted)
    elif words.intersection(ALL[language]):
        except_match=re.search(r"(?:^| )(?:кроме|except) (.+)$",phrase)
        if except_match:
            unwanted,bad,_=_scan(except_match.group(1),candidates,language)
            if bad or len(unwanted)!=1 or len(candidates)<2:
                return {"status":"needs_clarification","ids":[]}
            choice=[i for i in range(len(candidates)) if i not in unwanted]
        else:
            choice=list(range(len(candidates)))
    elif words.intersection(BOTH[language]):
        if len(candidates)!=2:
            return {"status":"needs_clarification","ids":[]}
        choice=[0,1]
    else:
        if not words.intersection(VERBS[language]):
            negative=phrase.startswith(("не ","нет ")) if language=="ru" else phrase.startswith(("not ","no "))
            return {"status":"needs_clarification" if negative else "not_direct_request","ids":[]}
        selected,bad,reference=_scan(phrase,candidates,language)
        if bad:
            return {"status":"no_match","ids":[]}
        if not selected:
            return {"status":"needs_clarification" if reference else "unrecognized","ids":[]}
        if len(selected)>1:
            compare=bool(words.intersection({"сравни","сравните"})) if language=="ru" else "compare" in words
            together="и" in words if language=="ru" else "and" in words
            if not (compare and together and len(selected)==2):
                return {"status":"needs_clarification","ids":[]}
        choice=sorted(selected)
    identifiers=[candidates[i]["id"] for i in choice]
    if require_confirmation or words.intersection(DESTRUCTIVE):
        return {"status":"confirm_required","ids":identifiers}
    return {"status":"resolved","ids":identifiers}

def main() -> None:
    parser=argparse.ArgumentParser(description="Reference selection only; does not act")
    parser.add_argument("--message",required=True)
    parser.add_argument("--language",choices=("ru","en"),default="ru")
    parser.add_argument("--candidates-json",required=True)
    parser.add_argument("--addressed",action="store_true")
    parser.add_argument("--require-confirmation",action="store_true")
    args=parser.parse_args()
    result=resolve(args.message,json.loads(args.candidates_json),
                   language=args.language,addressed=args.addressed,
                   require_confirmation=args.require_confirmation)
    print(json.dumps(result,ensure_ascii=False))

if __name__=="__main__":
    main()
