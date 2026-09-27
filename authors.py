"""Функции работы с авторами макетов."""

ROLE_NAMES = {
    "lead": "ведущий дизайнер",
    "designer": "дизайнер",
    "viewer": "наблюдатель",
}


def find_author(authors: list[dict], name: str) -> dict | None:
    """Найти автора по имени без учета регистра."""
    wanted = name.strip().lower()
    for author in authors:
        if author["name"].lower() == wanted:
            return author
    return None


def get_role_name(role: str) -> str:
    """Вернуть название роли автора на русском языке."""
    return ROLE_NAMES.get(role, role)


def format_author(author: dict) -> str:
    """Сформировать подпись автора: «Имя (роль)»."""
    return f"{author['name']} ({get_role_name(author['role'])})"
