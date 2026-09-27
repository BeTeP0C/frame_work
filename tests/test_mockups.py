from models import Mockup, Project
from models.mockups import (
    add_mockup,
    count_mockups_by_project,
    filter_mockups_by_project,
    find_mockup,
    search_mockups,
    sort_mockups_by_name,
)

BANK = Project(1, "Мобильный банк", "Приложение для iOS и Android")
SHOP = Project(2, "Сайт доставки", "Промо-страница и личный кабинет")


def test_add_mockup_creates_object():
    mockups = []
    mockup = add_mockup(mockups, BANK, "Экран авторизации")
    assert isinstance(mockup, Mockup)
    assert mockup.id == 1
    assert mockup.project is BANK


def test_find_mockup():
    mockups = []
    mockup = add_mockup(mockups, BANK, "Корзина")
    assert find_mockup(mockups, mockup.id) is mockup


def test_find_mockup_returns_none():
    assert find_mockup([], 10) is None


def test_mockup_matches_ignores_case():
    mockup = Mockup(1, BANK, "Экран авторизации")
    assert mockup.matches("ЭКРАН")
    assert not mockup.matches("корзина")


def test_search_mockups():
    mockups = []
    add_mockup(mockups, BANK, "Экран авторизации")
    add_mockup(mockups, BANK, "Корзина")
    assert len(search_mockups(mockups, "экран")) == 1


def test_filter_mockups_by_project():
    mockups = []
    add_mockup(mockups, BANK, "Экран авторизации")
    add_mockup(mockups, SHOP, "Главная страница")
    assert len(filter_mockups_by_project(mockups, SHOP)) == 1


def test_sort_mockups_by_name():
    mockups = []
    add_mockup(mockups, BANK, "Корзина")
    add_mockup(mockups, BANK, "Главная страница")
    names = [mockup.name for mockup in sort_mockups_by_name(mockups)]
    assert names == ["Главная страница", "Корзина"]


def test_count_mockups_by_project():
    mockups = []
    add_mockup(mockups, BANK, "Экран авторизации")
    add_mockup(mockups, SHOP, "Корзина")
    add_mockup(mockups, SHOP, "Главная страница")
    counters = count_mockups_by_project([BANK, SHOP], mockups)
    assert counters == {"Мобильный банк": 1, "Сайт доставки": 2}


def test_mockup_str():
    mockup = Mockup(1, BANK, "Экран авторизации")
    assert str(mockup) == "Мобильный банк / Экран авторизации"
