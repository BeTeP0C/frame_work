from mockups import (
    add_mockup,
    filter_mockups_by_project,
    find_mockup,
    search_mockups,
    sort_mockups_by_name,
)


def test_add_mockup():
    mockups = []
    add_mockup(mockups, 1, "Экран авторизации")
    assert len(mockups) == 1
    assert mockups[0]["id"] == 1


def test_find_mockup():
    mockups = []
    mockup = add_mockup(mockups, 1, "Корзина")
    assert find_mockup(mockups, mockup["id"]) == mockup


def test_find_mockup_returns_none():
    assert find_mockup([], 10) is None


def test_search_mockups_ignores_case():
    mockups = []
    add_mockup(mockups, 1, "Экран авторизации")
    add_mockup(mockups, 1, "Корзина")
    assert len(search_mockups(mockups, "экран")) == 1


def test_filter_mockups_by_project():
    mockups = []
    add_mockup(mockups, 1, "Экран авторизации")
    add_mockup(mockups, 2, "Главная страница")
    assert len(filter_mockups_by_project(mockups, 2)) == 1


def test_sort_mockups_by_name():
    mockups = []
    add_mockup(mockups, 1, "Корзина")
    add_mockup(mockups, 1, "Главная страница")
    names = [mockup["name"] for mockup in sort_mockups_by_name(mockups)]
    assert names == ["Главная страница", "Корзина"]
