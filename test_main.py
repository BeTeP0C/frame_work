from main import (
    check_author_access,
    check_file_format,
    format_version_label,
    get_next_version_number,
    get_upload_error,
    parse_file_size,
)


def test_designer_in_project_has_access():
    assert check_author_access("designer", True)


def test_viewer_has_no_access():
    assert not check_author_access("viewer", True)


def test_not_member_has_no_access():
    assert not check_author_access("lead", False)


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
