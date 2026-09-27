"""Функции работы с проектами."""


def find_project(projects: list[dict], project_id: int) -> dict | None:
    """Найти проект по идентификатору."""
    for project in projects:
        if project["id"] == project_id:
            return project
    return None


def get_project_name(projects: list[dict], project_id: int) -> str:
    """Вернуть название проекта или прочерк, если проект не найден."""
    project = find_project(projects, project_id)
    if project is None:
        return "—"
    return project["name"]


def count_mockups_by_project(
    projects: list[dict],
    mockups: list[dict],
) -> dict[str, int]:
    """Посчитать количество макетов в каждом проекте."""
    counters = {project["name"]: 0 for project in projects}
    for mockup in mockups:
        name = get_project_name(projects, mockup["project_id"])
        if name in counters:
            counters[name] += 1
    return counters
