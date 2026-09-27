import pytest

from versions import (
    add_version,
    check_author_access,
    check_file_format,
    delete_version,
    format_version_label,
    get_current_version_number,
    get_next_version_number,
    get_upload_error,
    get_version_stats,
    iter_versions_by_author,
    parse_file_size,
    rollback_to_version,
)

DESIGNER = {"name": "Анна Смирнова", "role": "designer", "projects": [1]}
VIEWER = {"name": "Мария Коваль", "role": "viewer", "projects": [1]}
MOCKUP = {"id": 1, "project_id": 1, "name": "Экран авторизации"}


def test_designer_in_project_has_access():
    assert check_author_access(DESIGNER, 1)


def test_viewer_has_no_access():
    assert not check_author_access(VIEWER, 1)


def test_author_outside_project_has_no_access():
    assert not check_author_access(DESIGNER, 2)


def test_supported_file_format():
    assert check_file_format("uploads/Login_Screen.FIG")


def test_unsupported_file_format():
    assert not check_file_format("uploads/login_screen.png")


def test_parse_file_size_with_comma():
    assert parse_file_size(" 12,5 ") == 12.5


def test_upload_allowed():
    assert get_upload_error(True, True, 12.5) == ""


def test_upload_rejected_for_big_file():
    assert "слишком большой" in get_upload_error(True, True, 50.1)


def test_next_version_number():
    assert get_next_version_number(3) == 4


def test_format_version_label():
    label = format_version_label("Мобильный банк", "Экран авторизации", 4)
    assert label == "Мобильный банк / Экран авторизации / v4"


def test_add_version_numbers_versions_in_order():
    versions = []
    add_version(versions, MOCKUP, DESIGNER, "login.fig", "10", "Первая")
    second = add_version(
        versions, MOCKUP, DESIGNER, "login.fig", "11", "Вторая"
    )
    assert second["number"] == 2
    assert get_current_version_number(versions, MOCKUP["id"]) == 2


def test_add_version_rejects_wrong_format():
    versions = []
    with pytest.raises(ValueError):
        add_version(versions, MOCKUP, DESIGNER, "login.png", "10", "Тест")
    assert versions == []


def test_add_version_rejects_viewer():
    versions = []
    with pytest.raises(ValueError):
        add_version(versions, MOCKUP, VIEWER, "login.fig", "10", "Тест")


def test_delete_version():
    versions = []
    version = add_version(
        versions, MOCKUP, DESIGNER, "login.fig", "10", "Первая"
    )
    assert delete_version(versions, version["id"])
    assert versions == []


def test_rollback_creates_new_version():
    versions = []
    add_version(versions, MOCKUP, DESIGNER, "login.fig", "10", "Первая")
    add_version(versions, MOCKUP, DESIGNER, "login.fig", "11", "Вторая")
    restored = rollback_to_version(versions, MOCKUP["id"], 1)
    assert restored["number"] == 3
    assert restored["size_mb"] == 10.0


def test_rollback_to_missing_version():
    with pytest.raises(ValueError):
        rollback_to_version([], MOCKUP["id"], 5)


def test_version_stats():
    versions = []
    add_version(versions, MOCKUP, DESIGNER, "login.fig", "10", "Первая")
    add_version(versions, MOCKUP, DESIGNER, "login.fig", "12,5", "Вторая")
    stats = get_version_stats(versions, MOCKUP["id"])
    assert stats["count"] == 2
    assert stats["authors"] == 1
    assert stats["total_size_mb"] == 22.5


def test_iter_versions_by_author():
    versions = []
    add_version(versions, MOCKUP, DESIGNER, "login.fig", "10", "Первая")
    found = list(iter_versions_by_author(versions, DESIGNER["name"]))
    assert len(found) == 1
