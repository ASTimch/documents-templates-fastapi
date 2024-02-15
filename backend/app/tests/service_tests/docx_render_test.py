import pytest

from app.services.docx_render import CustomFilters

fiom_fixture = "иванов иван петрович"
fiom_results = {
    "fio_short": "Иванов И.П.",
    "fio_title": "Иванов Иван Петрович",
    "genitive": "иванова ивана петровича",
    "dative": "иванову ивану петровичу",
    "ablt": "ивановым иваном петровичем",
    "loct": "иванове иване петровиче",
}
fiof_fixture = "иванова ирина петровна"
fiof_results = {
    "fio_short": "Иванова И.П.",
    "fio_title": "Иванова Ирина Петровна",
    "genitive": "ивановой ирины петровны",
    "dative": "ивановой ирине петровне",
    "ablt": "ивановой ириной петровной",
    "loct": "ивановой ирине петровне",
}

adj_fixture = [
    ("календарный", 1, "календарный"),
    ("календарный", 2, "календарных"),
    ("календарный", 3, "календарных"),
    ("календарный", 4, "календарных"),
    ("календарный", 5, "календарных"),
    ("календарный", 6, "календарных"),
    ("календарный", 7, "календарных"),
    ("календарный", 8, "календарных"),
    ("календарный", 9, "календарных"),
    ("календарный", 10, "календарных"),
    ("календарный", 11, "календарных"),
    ("календарный", 12, "календарных"),
    ("календарный", 21, "календарный"),
    ("календарный", 31, "календарный"),
    ("календарный", 100, "календарных"),
    ("календарный", 101, "календарный"),
]

noun_fixture = [
    ("день", 1, "день"),
    ("день", 2, "дня"),
    ("день", 3, "дня"),
    ("день", 4, "дня"),
    ("день", 5, "дней"),
    ("день", 6, "дней"),
    ("день", 7, "дней"),
    ("день", 8, "дней"),
    ("день", 9, "дней"),
    ("день", 10, "дней"),
    ("день", 11, "дней"),
    ("день", 21, "день"),
    ("день", 22, "дня"),
    ("день", 100, "дней"),
    ("день", 101, "день"),
]

filters_fixture = [
    "fio_short",
    "fio_title",
    "genitive",
    "dative",
    "ablt",
    "loct",
    "noun_plural",
    "adj_plural",
    "currency_to_words",
    "split",
]

currency_fixture = [
    (1.00, "один рубль, 00 копеек"),
    (2, "два рубля, 00 копеек"),
    (3.24, "три рубля, 24 копейки"),
    (4, "четыре рубля, 00 копеек"),
    (5, "пять рублей, 00 копеек"),
    (6, "шесть рублей, 00 копеек"),
    (7, "семь рублей, 00 копеек"),
    (1021, "одна тысяча двадцать один рубль, 00 копеек"),
    (2135, "две тысячи сто тридцать пять рублей, 00 копеек"),
    (1001000, "один миллион одна тысяча рублей, 00 копеек"),
    (1000000001, "один миллиард один рубль, 00 копеек"),
]

split_fixture = [
    (
        "Иванов Иван, Сидоров Петр",
        None,
        ["Иванов", "Иван,", "Сидоров", "Петр"],
    ),
    ("Иванов Иван, Сидоров Петр", ",", ["Иванов Иван", " Сидоров Петр"]),
]


class TestCustomFilters:
    def test_get_filters(self):
        """Проверка, что get_filter возвращает требуемый набор фильтров"""
        filters = CustomFilters()
        all_filters = set(filters.get_filters())
        assert all_filters == set(
            filters_fixture
        ), "Результат get_filters() не соответствует ожидаемому"

    @pytest.mark.parametrize(
        "fio, filter_results",
        [(fiof_fixture, fiof_results), (fiom_fixture, fiom_results)],
    )
    def test_fio_filters(self, fio, filter_results):
        """Проверка фильтров fio_short, fio_title"""
        filters = CustomFilters()
        all_filters = filters.get_filters()
        for filter, result in filter_results.items():
            assert (
                all_filters[filter](fio) == result
            ), f"Фильтр {filter} вернул неожиданный результат"

    @pytest.mark.parametrize("adj, number, result", adj_fixture)
    def test_adj_plural(self, adj, number, result):
        """Проверка фильтра adj_plural (склонение прилагательных)"""
        filter = CustomFilters()
        assert (
            filter.adj_plural(adj, number) == result
        ), "Фильтр adj_plural вернул неожиданный результат"

    @pytest.mark.parametrize("word, number, result", noun_fixture)
    def test_noun_plural(self, word, number, result):
        """Проверка фильтра noun_plural (склонение существительных)"""
        filters = CustomFilters()
        assert (
            filters.noun_plural(word, number) == result
        ), "Фильтр noun_plural вернул неожиданный результат"

    @pytest.mark.parametrize("amount, result", currency_fixture)
    def test_currency_to_words(self, amount, result):
        """Проверка фильтра currency_to_words (стоимость прописью)"""
        filters = CustomFilters()
        assert (
            filters.currency_to_words(amount) == result
        ), "Фильтр currency_to_words вернул неожиданный результат"

    @pytest.mark.parametrize("line, sep, result", split_fixture)
    def test_split(self, line, sep, result):
        """Проверка фильтра split (разделение строки)"""
        filters = CustomFilters()
        assert (
            filters.split(line, sep) == result
        ), "Фильтр split вернул неожиданный результат"
