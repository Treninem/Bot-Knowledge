"""Ten independent offline lookups for newly verified ImPULS help."""

from scripts.search_knowledge import KnowledgeSearch


def check(value: bool, detail: str) -> None:
    if not value:
        raise AssertionError(detail)


def main() -> None:
    search = KnowledgeSearch()
    cases = (
        ("Как работает бесплатный розыгрыш?", "free_draw_mechanics"),
        ("Как работает бесплатный розыгрыш Пульсов в ImPULS?", "free_draw_mechanics"),
        ("Как участвовать в розыгрыше Пульсов?", "free_draw_mechanics"),
        ("Что происходит с призом при отмене розыгрыша?", "free_draw_mechanics"),
        ("Как выдать права модератору?", "grant_local_moderator"),
        ("Как назначить модератора в чате?", "grant_local_moderator"),
        ("Как выдать локальную роль модератора?", "grant_local_moderator"),
        ("Почему бот не отвечает?", "group_reply_conditions"),
        ("Когда бот отвечает в чате?", "group_reply_conditions"),
        ("Почему бот молчит в группе?", "group_reply_conditions"),
    )
    for number, (question, expected) in enumerate(cases, 1):
        found = search.search(question, audience="impuls", limit=3)
        check(bool(found) and found[0][0] == expected, f"{number}: {question}: {found}")
        hidden = search.search(question, audience="all_ai_bots", limit=10)
        check(all(row[0] != expected for row in hidden), f"{number}: audience leak")
        print(f"IMPULS_HELP_GAPS_PASS {number}/10")


if __name__ == "__main__":
    main()
