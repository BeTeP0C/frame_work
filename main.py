"""Система учета версий дизайн-макетов.

Точка запуска приложения: меню пользователя и работа с объектами
предметной области.
"""

import storage
import utils
from models import Author, Mockup, Project, Version
from models.authors import find_author
from models.mockups import (
    count_mockups_by_project,
    find_mockup,
    search_mockups,
    sort_mockups_by_name,
)
from models.versions import (
    add_version,
    archive_version,
    get_current_version_number,
    get_mockup_versions,
    get_version_stats,
    rollback_to_version,
)

MENU = """
=== Система учета версий дизайн-макетов ===
1. Показать макеты
2. Найти макет по названию
3. История версий макета
4. Загрузить новую версию
5. Архивировать версию
6. Откатить макет к старой версии
7. Статистика по макету
8. Показать авторов
9. Справка по классам и функциям проекта
0. Выход
"""


def show_mockup_line(mockup: Mockup, versions: list[Version]) -> None:
    """Вывести одну строку списка макетов."""
    number = get_current_version_number(versions, mockup)
    print(f"{mockup.id}. {mockup} — v{number}")


def show_mockups(
    projects: list[Project],
    mockups: list[Mockup],
    versions: list[Version],
) -> None:
    """Вывести все макеты с номерами актуальных версий."""
    print("\nМакеты:")
    for mockup in sort_mockups_by_name(mockups):
        show_mockup_line(mockup, versions)
    print("\nМакетов в проектах:")
    counters = count_mockups_by_project(projects, mockups)
    for project_name, count in counters.items():
        print(f"  {project_name}: {count}")


def find_mockups_by_query(
    mockups: list[Mockup],
    versions: list[Version],
) -> None:
    """Найти макеты по подстроке названия."""
    found = search_mockups(mockups, utils.input_text("Часть названия: "))
    if not found:
        print("Макеты не найдены")
        return
    print("\nНайдено:")
    for mockup in found:
        show_mockup_line(mockup, versions)


def ask_mockup(mockups: list[Mockup]) -> Mockup | None:
    """Запросить у пользователя макет по идентификатору."""
    mockup = find_mockup(mockups, utils.input_int("Идентификатор макета: "))
    if mockup is None:
        print("Макет не найден")
    return mockup


def ask_author(authors: list[Author]) -> Author | None:
    """Запросить у пользователя автора по имени."""
    author = find_author(authors, utils.input_text("Автор: "))
    if author is None:
        print("Такой автор не найден")
    return author


def show_history(mockups: list[Mockup], versions: list[Version]) -> None:
    """Вывести историю версий выбранного макета."""
    mockup = ask_mockup(mockups)
    if mockup is None:
        return
    history = get_mockup_versions(versions, mockup)
    if not history:
        print("У макета пока нет версий")
        return
    print(f"\nИстория макета «{mockup.name}»:")
    for version in history:
        mark = " [архив]" if version.is_archived else ""
        print(f"  {version.id}. {version.describe()}{mark}")
        print(f"     {version.comment}")


def upload_version(
    mockups: list[Mockup],
    versions: list[Version],
    authors: list[Author],
) -> None:
    """Загрузить новую версию макета."""
    mockup = ask_mockup(mockups)
    if mockup is None:
        return
    author = ask_author(authors)
    if author is None:
        return
    file_path = utils.input_text("Файл макета: ")
    size_text = utils.input_text("Размер файла, МБ: ")
    comment = utils.input_text("Комментарий: ")
    try:
        version = add_version(
            versions, mockup, author, file_path, size_text, comment
        )
    except ValueError as error:
        print(f"Загрузка отклонена: {error}")
        return
    storage.save_versions(versions)
    print(f"Новая версия сохранена: {version.label}")
    print(f"Автор: {author}")


def archive_mockup_version(versions: list[Version]) -> None:
    """Убрать версию в архив по идентификатору."""
    version_id = utils.input_int("Идентификатор версии: ")
    if archive_version(versions, version_id):
        storage.save_versions(versions)
        print("Версия убрана в архив")
    else:
        print("Версия не найдена")


def rollback_mockup(
    mockups: list[Mockup],
    versions: list[Version],
    authors: list[Author],
) -> None:
    """Откатить макет к одной из старых версий."""
    mockup = ask_mockup(mockups)
    if mockup is None:
        return
    author = ask_author(authors)
    if author is None:
        return
    number = utils.input_int("Номер версии для отката: ")
    try:
        version = rollback_to_version(versions, mockup, number, author)
    except ValueError as error:
        print(f"Откат невозможен: {error}")
        return
    storage.save_versions(versions)
    print(f"Создана версия v{version.number} по образцу v{number}")


def show_stats(mockups: list[Mockup], versions: list[Version]) -> None:
    """Вывести статистику по версиям макета."""
    mockup = ask_mockup(mockups)
    if mockup is None:
        return
    stats = get_version_stats(versions, mockup)
    print(f"\nСтатистика макета «{mockup.name}»:")
    print(f"  версий: {stats['count']}")
    print(f"  из них в архиве: {stats['archived']}")
    print(f"  авторов: {stats['authors']}")
    print(f"  общий размер файлов: {stats['total_size_mb']} МБ")
    print(f"  последний автор: {stats['last_author']}")


def show_authors(authors: list[Author]) -> None:
    """Вывести список авторов и их роли."""
    print("\nАвторы:")
    for author in authors:
        print(f"  {author.id}. {author}, проекты: {author.projects}")


def show_help() -> None:
    """Вывести описание классов и функций проекта."""
    from models import versions as versions_module
    from models import mockups as mockups_module

    for target in (Project, Mockup, Author, Version):
        print(f"\nКласс {target.__name__}: {target.__doc__}")
        for name, doc in utils.describe_class(target):
            print(f"  {name} — {doc}")
    for module in (mockups_module, versions_module, storage):
        print(f"\nМодуль {module.__name__}:")
        for name, doc in utils.describe_functions(module):
            print(f"  {name} — {doc}")


def main() -> None:
    """Запустить приложение: загрузка данных и цикл меню."""
    projects = storage.load_projects()
    authors = storage.load_authors()
    mockups = storage.load_mockups(projects)
    versions = storage.load_versions(mockups, authors)

    while True:
        print(MENU)
        choice = utils.input_int("Выберите действие: ")
        if choice == 0:
            storage.save_versions(versions)
            print("Работа завершена")
            break
        elif choice == 1:
            show_mockups(projects, mockups, versions)
        elif choice == 2:
            find_mockups_by_query(mockups, versions)
        elif choice == 3:
            show_history(mockups, versions)
        elif choice == 4:
            upload_version(mockups, versions, authors)
        elif choice == 5:
            archive_mockup_version(versions)
        elif choice == 6:
            rollback_mockup(mockups, versions, authors)
        elif choice == 7:
            show_stats(mockups, versions)
        elif choice == 8:
            show_authors(authors)
        elif choice == 9:
            show_help()
        else:
            print("Нет такого пункта меню")


if __name__ == "__main__":
    main()
