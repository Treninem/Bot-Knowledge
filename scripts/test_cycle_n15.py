"""N15: English dialogue case integrity and context-specific search."""
import hashlib
import json
import re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question
ROOT=Path(__file__).resolve().parents[1]

def main():
    manifest=json.loads((ROOT/'manifest.json').read_text('utf-8'))
    p='packs/ru/english_dialogues.json'
    raw=(ROOT/p).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==next(e['sha256'] for e in manifest['packs'] if e['path']==p)
    assert len(raw)<2*1024*1024
    cases=json.loads(raw)['cases']
    new=[r for r in cases if r['id'].startswith('en_n15_')]
    assert len(new)==40,len(new)
    assert len({r['id'] for r in cases})==len(cases)
    assert len({normalize_question(r['input']) for r in cases})==len(cases)
    assert len({normalize_question(r['response']) for r in cases})==len(cases)
    index=KnowledgeSearch()
    for r in new:
        assert r['audiences']==['all_ai_bots'] and r['language']=='en'
        assert r['meaning_ru'].strip() and r['avoid'].strip()
        assert r['kind'] in {'conversation','slang','sarcasm','support','context','rules','deception','creative'}
        assert not re.search(r'(?i)https?://|@\\w+|\\b\\d{10,}\\b',json.dumps(r,ensure_ascii=False))
        assert any(h[0]==r['id'] for h in index.search(r['input'],audience='all_ai_bots',limit=20)),r['id']
    print('N15_EN_OK accepted=40 total='+str(len(cases)))
if __name__=='__main__':main()
