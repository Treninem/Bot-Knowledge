"""Opt-in, offline selector for the SHA-verified greeting catalogue.

The caller supplies permissions, context flags and session-local recent replies.
This module neither changes chat settings nor stores messages or calls a network.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = 'packs/ru/dialogue.json'
AUDIENCES = frozenset({'all_ai_bots', 'community_bots', 'chat_moderators'})
# Deliberately exact; never reduce a substantive question to its greeting prefix.
GREETINGS = frozenset({'привет', 'здравствуй', 'добрый день', 'добрый вечер',
                       'ку', 'хай', 'импульс привет'})


def normalized(text: str) -> str:
    return ' '.join(re.findall(r'[\w]+', unicodedata.normalize('NFKC', text)
                              .casefold().replace('ё', 'е'), flags=re.UNICODE))


class GreetingCatalog:
    """Immutable snapshot. Construct a replacement only after a verified update."""

    def __init__(self, root: Path = ROOT):
        root = Path(root)
        manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
        if manifest.get('schema_version') != 1 or manifest.get('language') != 'ru':
            raise ValueError('Unsupported manifest')
        matches = [p for p in manifest['packs'] if p.get('path') == PACK]
        if len(matches) != 1:
            raise ValueError('Missing or duplicate dialogue entry')
        raw = (root / PACK).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != matches[0].get('sha256'):
            raise ValueError('SHA mismatch: ' + PACK)
        data = json.loads(raw.decode('utf-8'))
        meta = data.get('greeting_catalog', {})
        policy = {'synthetic_examples_only': True, 'automatic_sanctions_allowed': False,
                  'personal_data_allowed': False, 'requires_explicit_address': True,
                  'requires_local_permission': True}
        if (data.get('schema_version') != 1 or data.get('language') != 'ru'
                or meta.get('schema_version') != 1 or meta.get('intent') != 'greeting'
                or meta.get('audiences') != ['all_ai_bots']
                or any(meta.get(k) is not v for k, v in policy.items())):
            raise ValueError('Invalid greeting metadata or policy')
        replies = data.get('reactions', {}).get('greeting')
        if (not isinstance(replies, list) or not 2 <= len(replies) <= 1000
                or any(not isinstance(s, str) or not 2 <= len(s) <= 300 for s in replies)
                or len({normalized(s) for s in replies}) != len(replies)):
            raise ValueError('Invalid or duplicate greetings')
        groups = meta.get('groups')
        if not isinstance(groups, dict) or not groups:
            raise ValueError('Missing groups')
        flattened = []
        for name, positions in groups.items():
            if (not isinstance(name, str) or not name.isascii()
                    or not name.replace('_', '').isalnum() or not isinstance(positions, list)
                    or not positions or any(type(i) is not int or not 0 <= i < len(replies)
                                           for i in positions)):
                raise ValueError('Invalid group')
            flattened.extend(positions)
        if sorted(flattened) != list(range(len(replies))):
            raise ValueError('Groups must partition greetings exactly once')
        default_group = meta.get('default_group')
        if default_group not in groups:
            raise ValueError('Invalid default group')
        self._replies = tuple(replies)
        self._groups = {name: tuple(indices) for name, indices in groups.items()}
        self._default = default_group
        self.snapshot_key = (manifest['knowledge_version'], digest)

    def reply(self, message: str, *, addressed: bool = False,
              local_permission: bool = False, language: str = 'ru',
              audience: str = 'all_ai_bots', group: str | None = None,
              sensitive: bool = False, silence_requested: bool = False,
              greeting_allowed: bool = True, recent: tuple[str, ...] = ()) -> dict:
        """Return one allowed reply or an explicit refusal; do not infer context.

        Non-default groups require an explicit caller choice based on known
        context. A recent-history list belongs to one conversation only.
        """
        if not isinstance(message, str) or len(message) > 1000:
            raise ValueError('Invalid message')
        flags = (addressed, local_permission, sensitive, silence_requested, greeting_allowed)
        if any(type(value) is not bool for value in flags):
            raise ValueError('Context flags must be booleans')
        if not isinstance(recent, (tuple, list)) or len(recent) > 128 or any(
                not isinstance(s, str) or len(s) > 1000 for s in recent):
            raise ValueError('Invalid recent replies')
        if audience not in AUDIENCES:
            raise ValueError('Unknown audience')
        group = self._default if group is None else group
        if group not in self._groups:
            raise ValueError('Unknown group')
        def decline(status: str) -> dict:
            return {'status': status, 'text': None}
        if not addressed:
            return decline('not_addressed')
        if not local_permission:
            return decline('not_authorized')
        if silence_requested or not greeting_allowed:
            return decline('silence_requested')
        if sensitive:
            return decline('sensitive_suppressed')
        if language != 'ru':
            return decline('wrong_language')
        value = unicodedata.normalize('NFKC', message).casefold().strip()
        # Quotes, question marks, mentions, URLs and extra words do not match.
        if not re.fullmatch(r'[а-яё ,.!\s]+', value):
            return decline('no_match')
        value = ' '.join(value.rstrip(' .!').replace(',', ' ').split())
        if value not in GREETINGS:
            return decline('no_match')
        seen = {normalized(s) for s in recent}
        for index in self._groups[group]:
            text = self._replies[index]
            if normalized(text) not in seen:
                return {'status': 'ok', 'text': text, 'source_id': f'greeting_{index + 1:03}',
                        'source_pack': PACK, 'group': group, 'snapshot_key': self.snapshot_key}
        return decline('repeat_suppressed')
