"""Загрузка и сохранение данных проекта в JSON-файлах."""

import json
import os

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
