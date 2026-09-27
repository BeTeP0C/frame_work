"""Функции работы с версиями дизайн-макетов."""

import os.path
from datetime import date

from utils import get_next_id

MAX_FILE_SIZE_MB = 50.0
SUPPORTED_FORMATS = (".fig", ".psd", ".sketch")
EDITOR_ROLES = ("lead", "designer")


def check_author_access(author: dict, project_id: int) -> bool:
    """Проверить, может ли автор загружать версии в проект."""
    if project_id not in author["projects"]:
        return False
    return author["role"] in EDITOR_ROLES


def check_file_format(file_path: str) -> bool:
    """Проверить, что файл макета имеет поддерживаемый формат."""
    file_name = os.path.basename(file_path).lower()
    return file_name.endswith(SUPPORTED_FORMATS)


def parse_file_size(size_text: str) -> float:
    """Преобразовать размер файла из строки («12,5») в мегабайты."""
    return float(size_text.strip().replace(",", "."))


def get_upload_error(
    has_access: bool,
    is_format_ok: bool,
    size_mb: float,
) -> str:
    """Вернуть причину отказа в загрузке или пустую строку."""
    if not has_access:
        return "У автора нет прав на загрузку версий в этот проект"
    elif not is_format_ok:
        return "Неподдерживаемый формат файла (нужен .fig, .psd или .sketch)"
    elif size_mb <= 0:
        return "Файл пустой"
    elif size_mb > MAX_FILE_SIZE_MB:
        return f"Файл слишком большой (максимум {MAX_FILE_SIZE_MB} МБ)"
    else:
        return ""


def get_next_version_number(current_version: int) -> int:
    """Вычислить номер новой версии макета."""
    return current_version + 1


def format_version_label(
    project_name: str,
    mockup_name: str,
    version_number: int,
) -> str:
    """Сформировать название версии: «Проект / Макет / vN»."""
    return f"{project_name} / {mockup_name} / v{version_number}"


def get_mockup_versions(versions: list[dict], mockup_id: int) -> list[dict]:
    """Вернуть версии макета, упорядоченные по номеру."""
    found = [
        version for version in versions if version["mockup_id"] == mockup_id
    ]
    return sorted(found, key=lambda version: version["number"])


def get_current_version_number(versions: list[dict], mockup_id: int) -> int:
    """Вернуть номер актуальной версии макета (0, если версий нет)."""
    mockup_versions = get_mockup_versions(versions, mockup_id)
    if not mockup_versions:
        return 0
    return mockup_versions[-1]["number"]


def find_version(
    versions: list[dict],
    mockup_id: int,
    number: int,
) -> dict | None:
    """Найти версию макета по ее номеру."""
    for version in get_mockup_versions(versions, mockup_id):
        if version["number"] == number:
            return version
    return None


def iter_versions_by_author(versions: list[dict], author_name: str):
    """Перебрать версии указанного автора (функция-генератор)."""
    for version in versions:
        if version["author"] == author_name:
            yield version


def add_version(
    versions: list[dict],
    mockup: dict,
    author: dict,
    file_path: str,
    size_text: str,
    comment: str,
) -> dict:
    """Создать новую версию макета после всех проверок.

    Выбрасывает ValueError, если данные некорректны или автор
    не имеет права загружать версии.
    """
    try:
        size_mb = parse_file_size(size_text)
    except ValueError:
        raise ValueError("Размер файла указан неверно")
    error = get_upload_error(
        check_author_access(author, mockup["project_id"]),
        check_file_format(file_path),
        size_mb,
    )
    if error:
        raise ValueError(error)
    current = get_current_version_number(versions, mockup["id"])
    version = {
        "id": get_next_id(versions),
        "mockup_id": mockup["id"],
        "number": get_next_version_number(current),
        "file_name": os.path.basename(file_path),
        "size_mb": size_mb,
        "author": author["name"],
        "created_at": date.today().isoformat(),
        "comment": comment,
    }
    versions.append(version)
    return version


def delete_version(versions: list[dict], version_id: int) -> bool:
    """Удалить версию по идентификатору."""
    for index, version in enumerate(versions):
        if version["id"] == version_id:
            del versions[index]
            return True
    return False


def rollback_to_version(
    versions: list[dict],
    mockup_id: int,
    number: int,
) -> dict:
    """Вернуть макет к старой версии, создав ее копию.

    Выбрасывает ValueError, если версии с таким номером нет.
    """
    source = find_version(versions, mockup_id, number)
    if source is None:
        raise ValueError(f"Версии v{number} у этого макета нет")
    current = get_current_version_number(versions, mockup_id)
    version = dict(source)
    version["id"] = get_next_id(versions)
    version["number"] = get_next_version_number(current)
    version["created_at"] = date.today().isoformat()
    version["comment"] = f"Откат к версии v{number}"
    versions.append(version)
    return version


def get_version_stats(versions: list[dict], mockup_id: int) -> dict:
    """Собрать статистику по версиям макета."""
    mockup_versions = get_mockup_versions(versions, mockup_id)
    authors = {version["author"] for version in mockup_versions}
    total_size = 0.0
    for version in mockup_versions:
        total_size += version["size_mb"]
    if mockup_versions:
        last_author = mockup_versions[-1]["author"]
    else:
        last_author = "—"
    return {
        "count": len(mockup_versions),
        "authors": len(authors),
        "total_size_mb": round(total_size, 1),
        "last_author": last_author,
    }
