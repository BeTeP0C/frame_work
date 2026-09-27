"""Класс дизайн-макета и функции работы с коллекцией макетов."""

from utils import get_next_id

from .projects import Project


class Mockup:
    """Дизайн-макет одного экрана или страницы проекта."""

    def __init__(
        self,
        mockup_id: int,
        project: Project,
        name: str,
    ) -> None:
        """Создать объект макета."""
        self.id = mockup_id
        self.project = project
        self.name = name

    def matches(self, query: str) -> bool:
        """Проверить, встречается ли подстрока в названии макета."""
        return query.strip().lower() in self.name.lower()

    def __str__(self) -> str:
        """Вернуть строковое представление макета."""
        return f"{self.project.name} / {self.name}"


def add_mockup(
    mockups: list[Mockup],
    project: Project,
    name: str,
) -> Mockup:
    """Создать макет в проекте и добавить его в коллекцию."""
    mockup = Mockup(get_next_id(mockups), project, name)
    mockups.append(mockup)
    return mockup


def find_mockup(mockups: list[Mockup], mockup_id: int) -> Mockup | None:
    """Найти макет по идентификатору."""
    for mockup in mockups:
        if mockup.id == mockup_id:
            return mockup
    return None


def search_mockups(mockups: list[Mockup], query: str) -> list[Mockup]:
    """Найти макеты по подстроке названия."""
    return [mockup for mockup in mockups if mockup.matches(query)]


def filter_mockups_by_project(
    mockups: list[Mockup],
    project: Project,
) -> list[Mockup]:
    """Отобрать макеты одного проекта с помощью генератора."""
    return list(
        mockup for mockup in mockups if mockup.project.id == project.id
    )


def sort_mockups_by_name(mockups: list[Mockup]) -> list[Mockup]:
    """Отсортировать макеты по названию (ключ задан lambda-функцией)."""
    return sorted(mockups, key=lambda mockup: mockup.name.lower())


def count_mockups_by_project(
    projects: list[Project],
    mockups: list[Mockup],
) -> dict[str, int]:
    """Посчитать количество макетов в каждом проекте."""
    counters = {project.name: 0 for project in projects}
    for mockup in mockups:
        if mockup.project.name in counters:
            counters[mockup.project.name] += 1
    return counters
