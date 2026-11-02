"""Offline regression tests; --repository additionally verifies every real pack."""
from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
import unittest
from difflib import SequenceMatcher
from pathlib import Path

from greeting_catalog import GreetingCatalog, GREETINGS, PACK, ROOT, normalized

BASE_REPLIES = ('Привет. Я на связи. Что нужно разобрать?',
                'Привет. Слушаю — можем решить вопрос по чату или просто поговорить.')


def near_key(text):
    return re.sub(r'^(?:привет|здравствуй)\s*', '', normalized(text)).strip()


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)


def repository_audit(root=ROOT):
    """Never report PASS when a manifest-listed source is missing."""
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    catalogue = json.loads((root / PACK).read_text(encoding='utf-8'))
    novel = catalogue['reactions']['greeting'][2:]
    new_keys = {normalized(s) for s in novel}
    other_strings = []
    paths = [p['path'] for p in manifest['packs']]
    assert len(paths) == len(set(paths)), 'Duplicate manifest paths'
    checked = 0
    for info in manifest['packs']:
        rel = info['path']
        assert rel.startswith('packs/ru/') and '..' not in Path(rel).parts
        raw = (root / rel).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == info['sha256'], rel
        payload = json.loads(raw)
        checked += 1
        if rel != PACK:
            other_strings.extend(strings(payload))
    collisions = new_keys.intersection(normalized(s) for s in other_strings)
    assert not collisions, f'Cross-pack exact duplicates: {sorted(collisions)}'
    near = []
    for answer in novel:
        key = near_key(answer)
        for old in other_strings:
            other = near_key(old)
            if min(len(key), len(other)) < 18:
                continue
            if min(len(key), len(other)) / max(len(key), len(other)) < .9:
                continue
            if SequenceMatcher(None, key, other, autojunk=False).ratio() >= .9:
                near.append((answer, old))
    assert not near, f'Cross-pack near duplicates require review: {near[:5]}'
    print(f'Repository audit: {checked}/{len(paths)} SHA/JSON PASS; 98 new replies; no exact/near collisions')


class GreetingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'packs/ru').mkdir(parents=True)
        self.raw = (ROOT / PACK).read_bytes()
        (self.root / PACK).write_bytes(self.raw)
        self.manifest = {'schema_version': 1, 'language': 'ru', 'knowledge_version': 'fixture',
                         'packs': [{'path': PACK, 'sha256': hashlib.sha256(self.raw).hexdigest()}]}
        self.save_manifest()
        self.catalog = GreetingCatalog(self.root)
        self.data = json.loads(self.raw)

    def save_manifest(self):
        (self.root / 'manifest.json').write_text(json.dumps(self.manifest), encoding='utf-8')

    def ask(self, message='привет', **kw):
        options = {'addressed': True, 'local_permission': True}
        options.update(kw)
        return self.catalog.reply(message, **options)

    def test_100_distinct_and_98_added(self):
        replies = self.data['reactions']['greeting']
        self.assertEqual(len(replies), 100)
        self.assertEqual(tuple(replies[:2]), BASE_REPLIES)
        self.assertEqual(len({normalized(x) for x in replies}), 100)

    def test_no_cosmetic_near_duplicates(self):
        answers = self.data['reactions']['greeting']
        for i, left in enumerate(answers):
            for right in answers[i+1:]:
                a, b = near_key(left), near_key(right)
                if min(len(a), len(b)) >= 18:
                    self.assertLess(SequenceMatcher(None, a, b, autojunk=False).ratio(), .86,
                                    (left, right))

    def test_no_personal_or_executable_fields(self):
        forbidden = {'user_id','chat_id','telegram_id','username','phone','email','token',
                     'cookie','password','secret','action','auto_apply'}
        def check(value):
            if isinstance(value, dict):
                self.assertFalse(forbidden.intersection(value))
                for child in value.values(): check(child)
            elif isinstance(value, list):
                for child in value: check(child)
        check(self.data)
        for text in self.data['reactions']['greeting']:
            self.assertFalse(re.search(r'https?://|@\w|\b\d{6,}\b', text))

    def test_all_7_existing_input_examples(self):
        for message in GREETINGS:
            with self.subTest(message=message): self.assertEqual(self.ask(message)['status'], 'ok')

    def test_case_spaces_punctuation(self):
        for text in (' ПРИВЕТ!!! ', 'Импульс, привет.', 'добрый   день!'):
            self.assertEqual(self.ask(text)['status'], 'ok')

    def test_questions_quotes_negation_not_greetings(self):
        for message in ('привет как настроить чат', 'привет, помоги с правилами', 'привет?',
                        'не привет', 'он сказал привет', '«привет»', '> привет',
                        'привет\nкак включить настройку', 'привет https://example.org',
                        'приветствие', 'привет\x00', 'привет\u200b', 'hello'):
            with self.subTest(message=message): self.assertEqual(self.ask(message)['status'], 'no_match')

    def test_explicit_address(self):
        self.assertEqual(self.ask(addressed=False)['status'], 'not_addressed')

    def test_permission_not_inferred(self):
        self.assertEqual(self.ask(local_permission=False)['status'], 'not_authorized')
        self.assertEqual(self.catalog.reply('привет')['status'], 'not_addressed')

    def test_sensitive_context_suppressed(self):
        for group in self.data['greeting_catalog']['groups']:
            self.assertEqual(self.ask(group=group, sensitive=True)['status'], 'sensitive_suppressed')

    def test_silence_and_greeting_preference(self):
        self.assertEqual(self.ask(silence_requested=True)['status'], 'silence_requested')
        self.assertEqual(self.ask(greeting_allowed=False)['status'], 'silence_requested')

    def test_language(self):
        self.assertEqual(self.ask(language='en')['status'], 'wrong_language')

    def test_scope_and_bad_parameters(self):
        for args in ({'audience':'administrator'}, {'group':'unknown'}, {'addressed':'yes'},
                     {'recent':'привет'}, {'recent':['a']*129}):
            with self.assertRaises(ValueError): self.ask(**args)

    def test_100_replies_reachable_and_repeats_suppressed(self):
        reached = set()
        for group in self.data['greeting_catalog']['groups']:
            recent=[]
            for _ in range(10):
                answer=self.ask(group=group, recent=recent)
                self.assertEqual(answer['status'], 'ok')
                self.assertNotIn(answer['text'], recent)
                reached.add(answer['source_id']); recent.append(answer['text'])
            self.assertEqual(self.ask(group=group, recent=recent)['status'], 'repeat_suppressed')
        self.assertEqual(len(reached),100)

    def test_normalized_repeat(self):
        first=self.ask()['text']
        self.assertNotEqual(self.ask(recent=[first.upper().replace('.', '!')])['text'],first)

    def test_no_global_session_memory(self):
        first=self.ask()
        self.ask(recent=[first['text']])
        self.assertEqual(self.ask(), first)

    def test_old_snapshot_and_sha_invalidation(self):
        changed=json.loads(self.raw)
        changed['reactions']['greeting'][0]='Здравствуй. Это синтетическая проверка замены снимка.'
        raw=json.dumps(changed,ensure_ascii=False).encode()
        (self.root/PACK).write_bytes(raw)
        with self.assertRaises(ValueError): GreetingCatalog(self.root)
        self.assertEqual(self.ask()['text'],BASE_REPLIES[0])
        self.manifest['packs'][0]['sha256']=hashlib.sha256(raw).hexdigest()
        self.manifest['knowledge_version']='fixture.next';self.save_manifest()
        new=GreetingCatalog(self.root)
        self.assertNotEqual(new.snapshot_key,self.catalog.snapshot_key)
        self.assertNotEqual(new.reply('привет',addressed=True,local_permission=True)['text'],BASE_REPLIES[0])

    def test_missing_duplicate_manifest_entry(self):
        self.manifest['packs']*=2; self.save_manifest()
        with self.assertRaises(ValueError): GreetingCatalog(self.root)
        self.manifest['packs']=[]; self.save_manifest()
        with self.assertRaises(ValueError): GreetingCatalog(self.root)

    def test_invalid_groups_rejected_after_valid_hash(self):
        changed=json.loads(self.raw)
        changed['greeting_catalog']['groups']['neutral'][0]=True
        raw=json.dumps(changed,ensure_ascii=False).encode();(self.root/PACK).write_bytes(raw)
        self.manifest['packs'][0]['sha256']=hashlib.sha256(raw).hexdigest();self.save_manifest()
        with self.assertRaises(ValueError): GreetingCatalog(self.root)

    def test_legacy_array_and_other_reactions_unchanged(self):
        self.assertTrue(all(isinstance(s,str) for s in self.data['reactions']['greeting']))
        self.assertEqual(self.data['reactions']['thanks'],['Пожалуйста.','Рад, что пригодилось.'])
        self.assertEqual(self.data['reactions']['farewell'],['До встречи.','Хорошо, до связи.'])
        self.assertEqual(self.data['reactions']['clarify_previous'],
                         ['Скажу проще: {previous_summary}', 'Переформулирую без лишних слов: {previous_summary}'])

    def test_repository_audit_fails_on_missing_pack(self):
        self.manifest['packs'].append({'path':'packs/ru/missing.json','sha256':'0'*64});self.save_manifest()
        with self.assertRaises(FileNotFoundError): repository_audit(self.root)


if __name__ == '__main__':
    full = '--repository' in sys.argv
    if full: sys.argv.remove('--repository')
    result=unittest.main(exit=False)
    if not result.result.wasSuccessful(): raise SystemExit(1)
    if full: repository_audit()
