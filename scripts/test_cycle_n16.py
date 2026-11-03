"""N16: approved original social replies, audiences, SHA, search, and duplicate protections."""
import hashlib
import json
import re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import normalize_question
ROOT=Path(__file__).resolve().parents[1]

def main():
    path='packs/ru/social_dialogues.json'
    raw=(ROOT/path).read_bytes()
    manifest=json.loads((ROOT/'manifest.json').read_text('utf-8'))
    assert len(raw)<2*1024*1024
    assert hashlib.sha256(raw).hexdigest()==next(x['sha256'] for x in manifest['packs'] if x['path']==path)
    rows=json.loads(raw)['cases']
    selected=[r for r in rows if r['id'].startswith('talk_n16_')]
    assert len(selected)==59,len(selected)
    assert len({r['id'] for r in rows})==len(rows)
    assert len({normalize_question(r['input']) for r in rows})==len(rows)
    assert len({normalize_question(r['response']) for r in rows})==len(rows)
    assert {r['kind'] for r in selected}=={'conversation','congratulations','support','humor','profanity','creative'}
    lookup=KnowledgeSearch()
    for r in selected:
        assert r['audiences']==['all_ai_bots']
        assert all(isinstance(r[k],str) and r[k].strip() for k in ('context','input','response','avoid'))
        assert not re.search(r'(?i)https?://|@\\w+|\\b\\d{10,}\\b',json.dumps(r,ensure_ascii=False))
        assert any(hit[0]==r['id'] for hit in lookup.search(r['input'],audience='all_ai_bots',limit=20)),r['id']
    print('N16_SOCIAL_OK added=59 total='+str(len(rows)))
if __name__=='__main__':main()
