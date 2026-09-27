"""Класс автора макетов и функции работы с коллекцией авторов."""

ROLE_NAMES = {
    "lead": "ведущий дизайнер",
    "designer": "дизайнер",
    "viewer": "наблюдатель",
}
EDITOR_ROLES = ("lead", "designer")


class Author:
    """Автор, который работает с макетами проектов."""

    def __init__(
        self,
        author_id: int,
        name: str,
        role: str,
        projects: list[int],
    ) -> None:
        """Создать объект автора."""
        self.id = author_id
        self.name = name
        self.role = role
        self.projects = projects

    @property
    def role_title(self) -> str:
        """Название роли автора на русском языке."""
        return ROLE_NAMES.get(self.role, self.role)

    def can_upload_to(self, project_id: int) -> bool:
        """Проверить, может ли автор загружать версии в проект."""
        if project_id not in self.projects:
            return False
        return self.role in EDITOR_ROLES

    def __str__(self) -> str:
        """Вернуть строковое представление автора."""
        return f"{self.name} ({self.role_title})"


def find_author(authors: list[Author], name: str) -> Author | None:
    """Найти автора по имени без учета регистра."""
    wanted = name.strip().lower()
    for author in authors:
        if author.name.lower() == wanted:
            return author
    return None


def find_author_by_id(
    authors: list[Author],
    author_id: int,
) -> Author | None:
    """Найти автора по идентификатору."""
    for author in authors:
        if author.id == author_id:
            return author
    return None
