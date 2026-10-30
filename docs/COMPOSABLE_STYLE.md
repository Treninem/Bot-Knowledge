# Композиционные RU/EN просьбы о стиле — 2026.10.30.16

После точных 80 запросов из `scoped_style_requests.json` новый `composable_style.json`
даёт **20 явно ограниченных смысловых директив** (10 измерений × 2 значения)
и **8 контекстных префиксов** (RU/EN × один ответ/текущая беседа × 2).
Отдельно сохранены 80 оригинальных полных RU/EN примеров. Набор правил способен
разобрать 160 комбинаций, в том числе 80 не входящих в этот список точных примеров.
Это ограниченная грамматика, а не понимание произвольных сообщений.

`scripts/composable_style.py` читает только локально утверждённый SHA-256 пакет,
требует `addressed=True`, отвергает кавычки, code spans, цитаты, смешанные
и неизвестные команды. Совпадать обязано **всё** сообщение, не его фрагмент.
`quoted=True` блокирует даже точную подготовленную фразу. Вызывающий consumer
отвечает за определение адресации/цитирования, изоляцию сессий, локальные ограничения,
срок действия и очистку памяти.

```python
from composable_style import ComposableStyle
from dialogue_preferences import PreferenceSession, load_preferences
session = PreferenceSession(load_preferences(), composer=ComposableStyle())
status = session.observe_composed(
    "В своём ближайшем ответе, обойдись без шуток.",
    language="ru", addressed=True)
assert status["status"] == "updated" and status["scope"] == "one_reply"
assert session.consume_for_reply()["humor"] == "disabled"
assert session.snapshot()["humor"] is None
session.clear()
```

Никакого автоматического согласия на мат, мрачный юмор и санкции.
`snapshot(sensitive=True)` по-прежнему отключает юмор/мат даже при opt-in.
Неизвестный составной запрос вызывает `unknown_input`, а не скрытую правку.

Проверки: `python scripts/validate_composable_style.py`,
`python scripts/test_composable_style.py`, `python scripts/validate_pack.py`.
Число 160 означает перебор разрешённых грамматик, а не 160 независимых навыков.
ImPULS/AuroraFox должны подтвердить интеграцию отдельно; публикация здесь её не включает.
