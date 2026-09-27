"""Функции работы с дизайн-макетами."""

from utils import get_next_id


def add_mockup(mockups: list[dict], project_id: int, name: str) -> dict:
    """Добавить макет в проект и вернуть его данные."""
    mockup = {
        "id": get_next_id(mockups),
        "project_id": project_id,
        "name": name,
    }
    mockups.append(mockup)
    return mockup


def find_mockup(mockups: list[dict], mockup_id: int) -> dict | None:
    """Найти макет по идентификатору."""
    for mockup in mockups:
        if mockup["id"] == mockup_id:
            return mockup
    return None


def search_mockups(mockups: list[dict], query: str) -> list[dict]:
    """Найти макеты по подстроке названия."""
    text = query.strip().lower()
    return [mockup for mockup in mockups if text in mockup["name"].lower()]


def filter_mockups_by_project(
    mockups: list[dict],
    project_id: int,
) -> list[dict]:
    """Отобрать макеты одного проекта с помощью генератора."""
    return list(
        mockup for mockup in mockups if mockup["project_id"] == project_id
    )


def sort_mockups_by_name(mockups: list[dict]) -> list[dict]:
    """Отсортировать макеты по названию (ключ задан lambda-функцией)."""
    return sorted(mockups, key=lambda mockup: mockup["name"].lower())
