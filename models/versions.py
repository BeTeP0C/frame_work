"""Классы версий макета и функции работы с коллекцией версий."""

import os.path
from datetime import date

from utils import get_next_id

from .authors import Author
from .mockups import Mockup

MAX_FILE_SIZE_MB = 50.0
SUPPORTED_FORMATS = (".fig", ".psd", ".sketch")


class Version:
    """Версия дизайн-макета, загруженная автором."""

    def __init__(
        self,
        version_id: int,
        mockup: Mockup,
        number: int,
        file_name: str,
        size_mb: float,
        author: Author,
        created_at: str,
        comment: str,
    ) -> None:
        """Создать объект версии макета."""
        self.id = version_id
        self.mockup = mockup
        self.number = number
        self.file_name = file_name
        self.size_mb = size_mb
        self.author = author
        self.created_at = created_at
        self.comment = comment
        self._is_archived = False

    @property
    def is_archived(self) -> bool:
        """Признак того, что версия убрана в архив."""
        return self._is_archived

    @property
    def label(self) -> str:
        """Название версии: «Проект / Макет / vN»."""
        return f"{self.mockup} / v{self.number}"

    def archive(self) -> None:
        """Убрать версию в архив, не удаляя ее из истории."""
        self._is_archived = True

    def restore(self) -> None:
        """Вернуть версию из архива."""
        self._is_archived = False

    def describe(self) -> str:
        """Вернуть описание версии для истории макета."""
        return (
            f"v{self.number} — {self.created_at}, {self.author.name}, "
            f"{self.size_mb} МБ"
        )

    @staticmethod
    def is_supported_format(file_path: str) -> bool:
        """Проверить, что файл макета имеет поддерживаемый формат."""
        file_name = os.path.basename(file_path).lower()
        return file_name.endswith(SUPPORTED_FORMATS)

    @staticmethod
    def parse_size(size_text: str) -> float:
        """Преобразовать размер файла из строки («12,5») в мегабайты."""
        return float(size_text.strip().replace(",", "."))

    def __str__(self) -> str:
        """Вернуть строковое представление версии."""
        state = "архив" if self._is_archived else "актуальная"
        return f"{self.label} ({state})"


class RollbackVersion(Version):
    """Версия, созданная откатом макета к одной из старых версий."""

    def __init__(
        self,
        version_id: int,
        mockup: Mockup,
        number: int,
        file_name: str,
        size_mb: float,
        author: Author,
        created_at: str,
        source_number: int,
    ) -> None:
        """Создать версию-откат на основе старой версии макета."""
        super().__init__(
            version_id,
            mockup,
            number,
            file_name,
            size_mb,
            author,
            created_at,
            f"Откат к версии v{source_number}",
        )
        self.source_number = source_number

    def describe(self) -> str:
        """Вернуть описание версии с указанием источника отката."""
        return f"{super().describe()}, откат к v{self.source_number}"


def get_mockup_versions(
    versions: list[Version],
    mockup: Mockup,
) -> list[Version]:
    """Вернуть все версии макета, упорядоченные по номеру."""
    found = [
        version for version in versions if version.mockup.id == mockup.id
    ]
    return sorted(found, key=lambda version: version.number)


def get_active_versions(
    versions: list[Version],
    mockup: Mockup,
) -> list[Version]:
    """Вернуть версии макета, не убранные в архив."""
    return [
        version
        for version in get_mockup_versions(versions, mockup)
        if not version.is_archived
    ]


def get_current_version_number(
    versions: list[Version],
    mockup: Mockup,
) -> int:
    """Вернуть номер актуальной версии макета (0, если версий нет)."""
    active = get_active_versions(versions, mockup)
    if not active:
        return 0
    return active[-1].number


def find_version(
    versions: list[Version],
    mockup: Mockup,
    number: int,
) -> Version | None:
    """Найти версию макета по ее номеру."""
    for version in get_mockup_versions(versions, mockup):
        if version.number == number:
            return version
    return None


def find_version_by_id(
    versions: list[Version],
    version_id: int,
) -> Version | None:
    """Найти версию по идентификатору."""
    for version in versions:
        if version.id == version_id:
            return version
    return None


def iter_versions_by_author(versions: list[Version], author: Author):
    """Перебрать версии указанного автора (функция-генератор)."""
    for version in versions:
        if version.author.id == author.id:
            yield version


def get_upload_error(
    author: Author,
    mockup: Mockup,
    file_path: str,
    size_mb: float,
) -> str:
    """Вернуть причину отказа в загрузке или пустую строку."""
    if not author.can_upload_to(mockup.project.id):
        return "У автора нет прав на загрузку версий в этот проект"
    elif not Version.is_supported_format(file_path):
        return "Неподдерживаемый формат файла (нужен .fig, .psd или .sketch)"
    elif size_mb <= 0:
        return "Файл пустой"
    elif size_mb > MAX_FILE_SIZE_MB:
        return f"Файл слишком большой (максимум {MAX_FILE_SIZE_MB} МБ)"
    else:
        return ""


def add_version(
    versions: list[Version],
    mockup: Mockup,
    author: Author,
    file_path: str,
    size_text: str,
    comment: str,
) -> Version:
    """Создать новую версию макета после всех проверок.

    Выбрасывает ValueError, если данные некорректны или автор
    не имеет права загружать версии в проект макета.
    """
    try:
        size_mb = Version.parse_size(size_text)
    except ValueError:
        raise ValueError("Размер файла указан неверно")
    error = get_upload_error(author, mockup, file_path, size_mb)
    if error:
        raise ValueError(error)
    version = Version(
        get_next_id(versions),
        mockup,
        get_current_version_number(versions, mockup) + 1,
        os.path.basename(file_path),
        size_mb,
        author,
        date.today().isoformat(),
        comment,
    )
    versions.append(version)
    return version


def archive_version(versions: list[Version], version_id: int) -> bool:
    """Убрать версию в архив по идентификатору."""
    version = find_version_by_id(versions, version_id)
    if version is None:
        return False
    version.archive()
    return True


def rollback_to_version(
    versions: list[Version],
    mockup: Mockup,
    number: int,
    author: Author,
) -> RollbackVersion:
    """Вернуть макет к старой версии, создав версию-откат.

    Выбрасывает ValueError, если версии с таким номером нет.
    """
    source = find_version(versions, mockup, number)
    if source is None:
        raise ValueError(f"Версии v{number} у этого макета нет")
    version = RollbackVersion(
        get_next_id(versions),
        mockup,
        get_current_version_number(versions, mockup) + 1,
        source.file_name,
        source.size_mb,
        author,
        date.today().isoformat(),
        number,
    )
    versions.append(version)
    return version


def get_version_stats(versions: list[Version], mockup: Mockup) -> dict:
    """Собрать статистику по версиям макета."""
    mockup_versions = get_mockup_versions(versions, mockup)
    authors = {version.author.name for version in mockup_versions}
    total_size = 0.0
    for version in mockup_versions:
        total_size += version.size_mb
    if mockup_versions:
        last_author = mockup_versions[-1].author.name
    else:
        last_author = "—"
    return {
        "count": len(mockup_versions),
        "archived": len(mockup_versions) - len(
            get_active_versions(versions, mockup)
        ),
        "authors": len(authors),
        "total_size_mb": round(total_size, 1),
        "last_author": last_author,
    }
