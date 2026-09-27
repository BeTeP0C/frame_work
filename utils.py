"""Вспомогательные функции: ввод данных и работа с объектами."""

import inspect
from types import ModuleType


def get_next_id(records: list) -> int:
    """Вернуть следующий свободный идентификатор записи."""
    if not records:
        return 1
    return max(record.id for record in records) + 1


def input_text(prompt: str) -> str:
    """Запросить непустую строку, повторяя запрос при пустом вводе."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Значение не может быть пустым")


def input_int(prompt: str) -> int:
    """Запросить целое число, повторяя запрос при ошибке ввода."""
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Нужно ввести целое число")


def describe_functions(module: ModuleType) -> list[tuple[str, str]]:
    """Собрать имена и краткие описания функций модуля.

    Используется интроспекция: функции модуля и их документирующие
    строки читаются во время выполнения программы.
    """
    described = []
    for name, function in inspect.getmembers(module, inspect.isfunction):
        if function.__module__ != module.__name__:
            continue
        doc = inspect.getdoc(function) or ""
        described.append((name, doc.splitlines()[0] if doc else ""))
    return described


def describe_class(target: type) -> list[tuple[str, str]]:
    """Собрать имена и краткие описания методов класса.

    Используется интроспекция: методы класса и их документирующие
    строки читаются во время выполнения программы.
    """
    described = []
    for name, member in inspect.getmembers(target):
        if name.startswith("_") and name != "__str__":
            continue
        if not (inspect.isfunction(member) or isinstance(member, property)):
            continue
        doc = inspect.getdoc(member) or ""
        described.append((name, doc.splitlines()[0] if doc else ""))
    return described
