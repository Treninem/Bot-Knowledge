"""N14: scope, SHA, distinct questions and indexed retrieval for new universal QA."""
import hashlib
import json
import re
from pathlib import Path
from scripts.search_knowledge import KnowledgeSearch
from scripts.validate_qa_v1 import validate_qa_pack, normalize_question
ROOT=Path(__file__).resolve().parents[1]

def main():
    manifest=json.loads((ROOT/'manifest.json').read_text('utf-8'))
    path='packs/ru/dialogue_help_qa.json'
    raw=(ROOT/path).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==next(e['sha256'] for e in manifest['packs'] if e['path']==path)
    assert len(raw)<1024*1024
    qa=json.loads(raw)
    assert validate_qa_pack(qa)==len(qa['records'])
    new=[r for r in qa['records'] if r['id'].startswith('dlg_n14_')]
    assert len(new)==30,len(new)
    assert len({r['id'] for r in qa['records']})==len(qa['records'])
    all_answers=[s for r in qa['records'] for s in [r['answer'],*r['variants']]]
    assert len({normalize_question(s) for s in all_answers})==len(all_answers)
    search=KnowledgeSearch()
    checked=0
    for row in new:
        assert row['audiences']==['all_ai_bots'] and row['language']=='ru'
        assert row['contexts']==['direct','private','group_addressed']
        assert len(row['aliases'])==len(row['variants'])==2
        assert row['source']=='https://github.com/Treninem/Bot-Knowledge/blob/72fbbf7c6be69ded07ef8b6c9b86c96c944a7c04/docs/REQUIREMENTS_21.md'
        assert not re.search(r'(?i)https?://|@\\w+|\\b\\d{10,}\\b', ' '.join([row['question'],row['answer'],*row['aliases'],*row['variants']]))
        for phrase in [row['question'],*row['aliases']]:
            hits=search.search(phrase,audience='all_ai_bots',limit=20)
            assert any(h[0]==row['id'] for h in hits),(row['id'],phrase)
            checked+=1
    print('N14_OK questions=30 response_texts=90 indexed_queries='+str(checked))

if __name__=='__main__':main()
