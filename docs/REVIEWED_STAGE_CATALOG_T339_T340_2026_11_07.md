# Проверенный read-only каталог 2 046 staged-ответов (T339/T340)

Заменяет прежний индекс T337/T338 после слияния проверенного T339/T340 PR #383. Читает все закреплённые стадии, исходные SHA-256 и цепочки родительских Git blob; 46 существующих канонических намерений, 946+44 = 990 разговорных и 1008+48 = 1056 практических staged-ответов. Всего 2 046 staged и отдельно 414 зарегистрированных. Никаких новых текстов и автоматической consumer-интеграции.

Локальная выдача требует подтверждённый intent, exact approved reply ID, аудиторию all_ai_bots, правильный private/direct/group_addressed контекст, явную адресацию и permission. Ограничены списки approved и recent; сетевых вызовов, записи состояния, санкций нет. Cache identity зависит от версии manifest и всех байтов стадий.

Проверки: python -m unittest scripts.test_reviewed_stage_catalog -q; python scripts/validate_pack.py. Живые боты и кэши не изменяются. Ответы staging не регистрируются в manifest. Сначала подтвердить merge/CI #383, затем exact-head этого PR, merge и фактический post-main CI.
