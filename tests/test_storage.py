from models import Author, Mockup, Project, Version
from models.versions import add_version, rollback_to_version
from storage import (
    load_authors,
    load_mockups,
    load_projects,
    load_records,
    load_versions,
    save_authors,
    save_mockups,
    save_projects,
    save_versions,
)

BANK = Project(1, "Мобильный банк", "Приложение для iOS и Android")
MOCKUP = Mockup(1, BANK, "Экран авторизации")
DESIGNER = Author(1, "Анна Смирнова", "designer", [1])


def test_projects_round_trip(tmp_path):
    file_name = str(tmp_path / "projects.json")
    save_projects([BANK], file_name)
    loaded = load_projects(file_name)
    assert len(loaded) == 1
    assert isinstance(loaded[0], Project)
    assert loaded[0].name == BANK.name


def test_authors_round_trip(tmp_path):
    file_name = str(tmp_path / "authors.json")
    save_authors([DESIGNER], file_name)
    loaded = load_authors(file_name)
    assert loaded[0].can_upload_to(1)


def test_mockups_are_linked_to_projects(tmp_path):
    file_name = str(tmp_path / "mockups.json")
    save_mockups([MOCKUP], file_name)
    loaded = load_mockups([BANK], file_name)
    assert isinstance(loaded[0], Mockup)
    assert loaded[0].project is BANK


def test_versions_are_linked_to_mockup_and_author(tmp_path):
    file_name = str(tmp_path / "versions.json")
    versions = []
    add_version(versions, MOCKUP, DESIGNER, "login.fig", "10", "Первая")
    save_versions(versions, file_name)
    loaded = load_versions([MOCKUP], [DESIGNER], file_name)
    assert isinstance(loaded[0], Version)
    assert loaded[0].mockup is MOCKUP
    assert loaded[0].author is DESIGNER


def test_json_stores_identifiers(tmp_path):
    file_name = str(tmp_path / "versions.json")
    versions = []
    add_version(versions, MOCKUP, DESIGNER, "login.fig", "10", "Первая")
    save_versions(versions, file_name)
    record = load_records(file_name)[0]
    assert record["mockup_id"] == MOCKUP.id
    assert record["author_id"] == DESIGNER.id


def test_rollback_and_archive_survive_round_trip(tmp_path):
    file_name = str(tmp_path / "versions.json")
    versions = []
    first = add_version(
        versions, MOCKUP, DESIGNER, "login.fig", "10", "Первая"
    )
    first.archive()
    rollback_to_version(versions, MOCKUP, 1, DESIGNER)
    save_versions(versions, file_name)
    loaded = load_versions([MOCKUP], [DESIGNER], file_name)
    assert loaded[0].is_archived
    assert loaded[1].source_number == 1
    assert "откат к v1" in loaded[1].describe()


def test_missing_file_returns_empty_list(tmp_path):
    assert load_records(str(tmp_path / "nothing.json")) == []
