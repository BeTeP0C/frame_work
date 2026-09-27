"""Класс проекта и функции работы с коллекцией проектов."""


class Project:
    """Проект, в рамках которого ведутся дизайн-макеты."""

    def __init__(
        self,
        project_id: int,
        name: str,
        description: str,
    ) -> None:
        """Создать объект проекта."""
        self.id = project_id
        self.name = name
        self.description = description

    def __str__(self) -> str:
        """Вернуть строковое представление проекта."""
        return f"{self.name} — {self.description}"


def find_project(
    projects: list[Project],
    project_id: int,
) -> Project | None:
    """Найти проект по идентификатору."""
    for project in projects:
        if project.id == project_id:
            return project
    return None
