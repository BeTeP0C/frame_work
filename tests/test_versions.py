import pytest

from models import Author, Mockup, Project, RollbackVersion, Version
from models.versions import (
    add_version,
    archive_version,
    get_active_versions,
    get_current_version_number,
    get_mockup_versions,
    get_upload_error,
    get_version_stats,
    iter_versions_by_author,
    rollback_to_version,
)

BANK = Project(1, "Мобильный банк", "Приложение для iOS и Android")
SHOP = Project(2, "Сайт доставки", "Промо-страница и личный кабинет")
MOCKUP = Mockup(1, BANK, "Экран авторизации")
DESIGNER = Author(1, "Анна Смирнова", "designer", [1])
VIEWER = Author(2, "Мария Коваль", "viewer", [1])


def test_designer_can_upload_to_own_project():
    assert DESIGNER.can_upload_to(1)


def test_viewer_cannot_upload():
    assert not VIEWER.can_upload_to(1)


def test_author_cannot_upload_to_foreign_project():
    assert not DESIGNER.can_upload_to(2)


def test_author_role_title():
    assert DESIGNER.role_title == "дизайнер"


def test_author_str():
    assert str(DESIGNER) == "Анна Смирнова (дизайнер)"


def test_supported_file_format():
    assert Version.is_supported_format("uploads/Login_Screen.FIG")


def test_unsupported_file_format():
    assert not Version.is_supported_format("uploads/login_screen.png")


def test_parse_size_with_comma():
    assert Version.parse_size(" 12,5 ") == 12.5


def test_upload_allowed():
    assert get_upload_error(DESIGNER, MOCKUP, "login.fig", 12.5) == ""


def test_upload_rejected_for_big_file():
    error = get_upload_error(DESIGNER, MOCKUP, "login.fig", 50.1)
    assert "слишком большой" in error


def test_add_version_numbers_versions_in_order():
    versions = []
    add_version(versions, MOCKUP, DESIGNER, "login.fig", "10", "Первая")
    second = add_version(
        versions, MOCKUP, DESIGNER, "login.fig", "11", "Вторая"
    )
    assert second.number == 2
    assert get_current_version_number(versions, MOCKUP) == 2


def test_add_version_links_objects():
    versions = []
    version = add_version(
        versions, MOCKUP, DESIGNER, "login.fig", "10", "Первая"
    )
    assert version.mockup is MOCKUP
    assert version.author is DESIGNER
    assert version.mockup.project is BANK


def test_add_version_rejects_wrong_format():
    versions = []
    with pytest.raises(ValueError):
        add_version(versions, MOCKUP, DESIGNER, "login.png", "10", "Тест")
    assert versions == []


def test_add_version_rejects_viewer():
    versions = []
    with pytest.raises(ValueError):
        add_version(versions, MOCKUP, VIEWER, "login.fig", "10", "Тест")


def test_version_label_and_str():
    versions = []
    version = add_version(
        versions, MOCKUP, DESIGNER, "login.fig", "10", "Первая"
    )
    assert version.label == "Мобильный банк / Экран авторизации / v1"
    assert "актуальная" in str(version)


def test_archive_keeps_version_in_history():
    versions = []
    version = add_version(
        versions, MOCKUP, DESIGNER, "login.fig", "10", "Первая"
    )
    assert archive_version(versions, version.id)
    assert version.is_archived
    assert len(get_mockup_versions(versions, MOCKUP)) == 1
    assert get_active_versions(versions, MOCKUP) == []


def test_archived_flag_is_read_only():
    version = Version(
        1, MOCKUP, 1, "login.fig", 10.0, DESIGNER, "2026-09-01", "Первая"
    )
    with pytest.raises(AttributeError):
        version.is_archived = True


def test_rollback_creates_rollback_version():
    versions = []
    add_version(versions, MOCKUP, DESIGNER, "login.fig", "10", "Первая")
    add_version(versions, MOCKUP, DESIGNER, "login.fig", "11", "Вторая")
    restored = rollback_to_version(versions, MOCKUP, 1, DESIGNER)
    assert isinstance(restored, RollbackVersion)
    assert restored.number == 3
    assert restored.size_mb == 10.0
    assert restored.comment == "Откат к версии v1"


def test_rollback_version_describes_source():
    versions = []
    add_version(versions, MOCKUP, DESIGNER, "login.fig", "10", "Первая")
    restored = rollback_to_version(versions, MOCKUP, 1, DESIGNER)
    assert "откат к v1" in restored.describe()


def test_rollback_to_missing_version():
    with pytest.raises(ValueError):
        rollback_to_version([], MOCKUP, 5, DESIGNER)


def test_version_stats():
    versions = []
    add_version(versions, MOCKUP, DESIGNER, "login.fig", "10", "Первая")
    version = add_version(
        versions, MOCKUP, DESIGNER, "login.fig", "12,5", "Вторая"
    )
    version.archive()
    stats = get_version_stats(versions, MOCKUP)
    assert stats["count"] == 2
    assert stats["archived"] == 1
    assert stats["authors"] == 1
    assert stats["total_size_mb"] == 22.5


def test_iter_versions_by_author():
    versions = []
    add_version(versions, MOCKUP, DESIGNER, "login.fig", "10", "Первая")
    found = list(iter_versions_by_author(versions, DESIGNER))
    assert len(found) == 1
