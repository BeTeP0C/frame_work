"""Загрузка и сохранение данных проекта в JSON-файлах.

Модуль преобразует данные JSON в объекты классов предметной области
и выполняет обратное преобразование перед сохранением.
"""

import json
import os

from models import Author, Mockup, Project, RollbackVersion, Version
from models.authors import find_author_by_id
from models.mockups import find_mockup
from models.projects import find_project

DATA_DIR = "data"
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.json")
MOCKUPS_FILE = os.path.join(DATA_DIR, "mockups.json")
VERSIONS_FILE = os.path.join(DATA_DIR, "versions.json")
AUTHORS_FILE = os.path.join(DATA_DIR, "authors.json")


def load_records(file_name: str) -> list[dict]:
    """Загрузить список записей из JSON-файла.

    Если файл отсутствует или поврежден, возвращается пустой список,
    а программа продолжает работу.
    """
    try:
        with open(file_name, encoding="utf-8") as data_file:
            return json.load(data_file)
    except FileNotFoundError:
        print(f"Файл {file_name} не найден, начинаем с пустого списка")
        return []
    except json.JSONDecodeError:
        print(f"Файл {file_name} поврежден, начинаем с пустого списка")
        return []


def save_records(file_name: str, records: list[dict]) -> None:
    """Сохранить список записей в JSON-файл."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(file_name, "w", encoding="utf-8") as data_file:
        json.dump(records, data_file, ensure_ascii=False, indent=2)


def load_projects(file_name: str = PROJECTS_FILE) -> list[Project]:
    """Загрузить проекты и создать объекты Project."""
    return [
        Project(data["id"], data["name"], data["description"])
        for data in load_records(file_name)
    ]


def save_projects(
    projects: list[Project],
    file_name: str = PROJECTS_FILE,
) -> None:
    """Сохранить объекты Project в JSON-файл."""
    save_records(
        file_name,
        [
            {
                "id": project.id,
                "name": project.name,
                "description": project.description,
            }
            for project in projects
        ],
    )


def load_authors(file_name: str = AUTHORS_FILE) -> list[Author]:
    """Загрузить авторов и создать объекты Author."""
    return [
        Author(data["id"], data["name"], data["role"], data["projects"])
        for data in load_records(file_name)
    ]


def save_authors(
    authors: list[Author],
    file_name: str = AUTHORS_FILE,
) -> None:
    """Сохранить объекты Author в JSON-файл."""
    save_records(
        file_name,
        [
            {
                "id": author.id,
                "name": author.name,
                "role": author.role,
                "projects": author.projects,
            }
            for author in authors
        ],
    )


def load_mockups(
    projects: list[Project],
    file_name: str = MOCKUPS_FILE,
) -> list[Mockup]:
    """Загрузить макеты, связав их с объектами Project."""
    mockups = []
    for data in load_records(file_name):
        project = find_project(projects, data["project_id"])
        if project is None:
            print(f"Макет {data['id']}: проект не найден, пропущен")
            continue
        mockups.append(Mockup(data["id"], project, data["name"]))
    return mockups


def save_mockups(
    mockups: list[Mockup],
    file_name: str = MOCKUPS_FILE,
) -> None:
    """Сохранить объекты Mockup в JSON-файл."""
    save_records(
        file_name,
        [
            {
                "id": mockup.id,
                "project_id": mockup.project.id,
                "name": mockup.name,
            }
            for mockup in mockups
        ],
    )


def load_versions(
    mockups: list[Mockup],
    authors: list[Author],
    file_name: str = VERSIONS_FILE,
) -> list[Version]:
    """Загрузить версии, связав их с объектами Mockup и Author."""
    versions = []
    for data in load_records(file_name):
        mockup = find_mockup(mockups, data["mockup_id"])
        author = find_author_by_id(authors, data["author_id"])
        if mockup is None or author is None:
            print(f"Версия {data['id']}: связанные данные не найдены")
            continue
        if data.get("kind") == "rollback":
            version = RollbackVersion(
                data["id"],
                mockup,
                data["number"],
                data["file_name"],
                data["size_mb"],
                author,
                data["created_at"],
                data["source_number"],
            )
        else:
            version = Version(
                data["id"],
                mockup,
                data["number"],
                data["file_name"],
                data["size_mb"],
                author,
                data["created_at"],
                data["comment"],
            )
        if data.get("is_archived"):
            version.archive()
        versions.append(version)
    return versions


def save_versions(
    versions: list[Version],
    file_name: str = VERSIONS_FILE,
) -> None:
    """Сохранить объекты версий в JSON-файл.

    Ссылки на объекты Mockup и Author заменяются идентификаторами.
    """
    records = []
    for version in versions:
        record = {
            "id": version.id,
            "mockup_id": version.mockup.id,
            "number": version.number,
            "file_name": version.file_name,
            "size_mb": version.size_mb,
            "author_id": version.author.id,
            "created_at": version.created_at,
            "comment": version.comment,
            "is_archived": version.is_archived,
            "kind": "version",
        }
        if isinstance(version, RollbackVersion):
            record["kind"] = "rollback"
            record["source_number"] = version.source_number
        records.append(record)
    save_records(file_name, records)
