"""Система учета версий дизайн-макетов.

Точка запуска приложения: меню пользователя и вызов функций проекта.
"""

import authors
import mockups
import projects
import storage
import utils
import versions

MENU = """
=== Система учета версий дизайн-макетов ===
1. Показать макеты
2. Найти макет по названию
3. История версий макета
4. Загрузить новую версию
5. Удалить версию
6. Откатить макет к старой версии
7. Статистика по макету
8. Справка по функциям проекта
0. Выход
"""


def show_mockup_line(
    project_list: list[dict],
    version_list: list[dict],
    mockup: dict,
) -> None:
    """Вывести одну строку списка макетов."""
    project_name = projects.get_project_name(
        project_list, mockup["project_id"]
    )
    number = versions.get_current_version_number(version_list, mockup["id"])
    print(f"{mockup['id']}. {project_name} / {mockup['name']} — v{number}")


def show_mockups(
    project_list: list[dict],
    mockup_list: list[dict],
    version_list: list[dict],
) -> None:
    """Вывести все макеты с номерами актуальных версий."""
    print("\nМакеты:")
    for mockup in mockups.sort_mockups_by_name(mockup_list):
        show_mockup_line(project_list, version_list, mockup)
    counters = projects.count_mockups_by_project(project_list, mockup_list)
    print("\nМакетов в проектах:")
    for project_name, count in counters.items():
        print(f"  {project_name}: {count}")


def search_mockups(
    project_list: list[dict],
    mockup_list: list[dict],
    version_list: list[dict],
) -> None:
    """Найти макеты по подстроке названия."""
    query = utils.input_text("Часть названия: ")
    found = mockups.search_mockups(mockup_list, query)
    if not found:
        print("Макеты не найдены")
        return
    print("\nНайдено:")
    for mockup in found:
        show_mockup_line(project_list, version_list, mockup)


def ask_mockup(mockup_list: list[dict]) -> dict | None:
    """Запросить у пользователя макет по идентификатору."""
    mockup_id = utils.input_int("Идентификатор макета: ")
    mockup = mockups.find_mockup(mockup_list, mockup_id)
    if mockup is None:
        print("Макет не найден")
    return mockup


def show_history(mockup_list: list[dict], version_list: list[dict]) -> None:
    """Вывести историю версий выбранного макета."""
    mockup = ask_mockup(mockup_list)
    if mockup is None:
        return
    history = versions.get_mockup_versions(version_list, mockup["id"])
    if not history:
        print("У макета пока нет версий")
        return
    print(f"\nИстория макета «{mockup['name']}»:")
    for version in history:
        print(
            f"  v{version['number']} — {version['created_at']}, "
            f"{version['author']}, {version['size_mb']} МБ"
        )
        print(f"    {version['comment']}")


def upload_version(
    project_list: list[dict],
    mockup_list: list[dict],
    version_list: list[dict],
    author_list: list[dict],
) -> None:
    """Загрузить новую версию макета."""
    mockup = ask_mockup(mockup_list)
    if mockup is None:
        return
    author = authors.find_author(author_list, utils.input_text("Автор: "))
    if author is None:
        print("Такой автор не найден")
        return
    file_path = utils.input_text("Файл макета: ")
    size_text = utils.input_text("Размер файла, МБ: ")
    comment = utils.input_text("Комментарий: ")
    try:
        version = versions.add_version(
            version_list, mockup, author, file_path, size_text, comment
        )
    except ValueError as error:
        print(f"Загрузка отклонена: {error}")
        return
    storage.save_records(storage.VERSIONS_FILE, version_list)
    label = versions.format_version_label(
        projects.get_project_name(project_list, mockup["project_id"]),
        mockup["name"],
        version["number"],
    )
    print(f"Новая версия сохранена: {label}")
    print(f"Автор: {authors.format_author(author)}")


def remove_version(version_list: list[dict]) -> None:
    """Удалить версию по идентификатору."""
    version_id = utils.input_int("Идентификатор версии: ")
    if versions.delete_version(version_list, version_id):
        storage.save_records(storage.VERSIONS_FILE, version_list)
        print("Версия удалена")
    else:
        print("Версия не найдена")


def rollback_mockup(mockup_list: list[dict], version_list: list[dict]) -> None:
    """Откатить макет к одной из старых версий."""
    mockup = ask_mockup(mockup_list)
    if mockup is None:
        return
    number = utils.input_int("Номер версии для отката: ")
    try:
        version = versions.rollback_to_version(
            version_list, mockup["id"], number
        )
    except ValueError as error:
        print(f"Откат невозможен: {error}")
        return
    storage.save_records(storage.VERSIONS_FILE, version_list)
    print(f"Создана версия v{version['number']} по образцу v{number}")


def show_stats(mockup_list: list[dict], version_list: list[dict]) -> None:
    """Вывести статистику по версиям макета."""
    mockup = ask_mockup(mockup_list)
    if mockup is None:
        return
    stats = versions.get_version_stats(version_list, mockup["id"])
    print(f"\nСтатистика макета «{mockup['name']}»:")
    print(f"  версий: {stats['count']}")
    print(f"  авторов: {stats['authors']}")
    print(f"  общий размер файлов: {stats['total_size_mb']} МБ")
    print(f"  последний автор: {stats['last_author']}")


def show_help() -> None:
    """Вывести список функций модулей проекта."""
    for module in (projects, mockups, versions, storage, authors):
        print(f"\nМодуль {module.__name__}.py:")
        for name, doc in utils.describe_functions(module):
            print(f"  {name} — {doc}")


def main() -> None:
    """Запустить приложение: загрузка данных и цикл меню."""
    project_list = storage.load_records(storage.PROJECTS_FILE)
    mockup_list = storage.load_records(storage.MOCKUPS_FILE)
    version_list = storage.load_records(storage.VERSIONS_FILE)
    author_list = storage.load_records(storage.AUTHORS_FILE)

    while True:
        print(MENU)
        choice = utils.input_int("Выберите действие: ")
        if choice == 0:
            print("Работа завершена")
            break
        elif choice == 1:
            show_mockups(project_list, mockup_list, version_list)
        elif choice == 2:
            search_mockups(project_list, mockup_list, version_list)
        elif choice == 3:
            show_history(mockup_list, version_list)
        elif choice == 4:
            upload_version(
                project_list, mockup_list, version_list, author_list
            )
        elif choice == 5:
            remove_version(version_list)
        elif choice == 6:
            rollback_mockup(mockup_list, version_list)
        elif choice == 7:
            show_stats(mockup_list, version_list)
        elif choice == 8:
            show_help()
        else:
            print("Нет такого пункта меню")


if __name__ == "__main__":
    main()
