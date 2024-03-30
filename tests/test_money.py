import locale

from sartorial import Schema

from atypical.money import Money


def test_money():
    locale.setlocale(locale.LC_NUMERIC, "en_US.UTF-8")
    m = Money(100, "USD")
    assert m == "$100.00"
    assert m.amount == 100
    assert m.currency == "USD"
    assert m.formatted.replace("\xa0", "") == "$100.00"
    assert m.num_cents == 10000
    assert m.friendly.replace("\xa0", "") == "$100"

    assert Money.from_cents(10000, "USD") == "$100.00"

    assert Money("$100") == m
    assert Money(100) == m
    assert Money("$100.00") == m
    assert Money("$100.01") != Money("$100.00")
    assert Money("$100.01") > Money("$100.00")
    assert Money("$100.01") >= Money("$100.00")
    assert Money("$100.00") >= Money("$100.00")
    assert Money("$100.00") < Money("$100.01")
    assert Money("$100.00") <= Money("$100.01")
    assert Money("$100.00") <= Money("$100.00")

    assert Money("$100.01").friendly.replace("\xa0", "") == "$100.01"

    assert str(Money("100", "EUR", "de_DE")) == "100,00\xa0€"
    assert Money(100, "EUR", "de_DE").friendly == "100\xa0€"

    class Model(Schema):
        money: Money

    d = Model.to_schema_dict()
    assert d["properties"]["money"]["type"] == "string"
    assert d["properties"]["money"]["format"] == "money"

    NewModel = Schema.from_schema_dict(d)
    n = NewModel(money="100")
    assert isinstance(n.money, Money)
    assert isinstance(n.money, str)
    assert n.money == "$100.00"
    assert n.money.currency == "USD"
    assert n.money.num_cents == 10000

    m = Model(money="100.01")
    m.money += "0.99"
    assert isinstance(m.money, Money)
    assert m.to_json() == '{"money":"$101.00"}'
