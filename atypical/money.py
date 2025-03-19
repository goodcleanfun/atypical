from decimal import Decimal
from typing import ForwardRef, Union

from babel import Locale
from babel.core import default_locale
from babel.numbers import format_currency, get_decimal_symbol
from money import Money as BaseMoney
from sartorial import JSONSchemaFormatted, Serializable

from atypical.currency import CurrencyCode, CurrencyParser

Money = ForwardRef("Money")


class Money(str, BaseMoney, JSONSchemaFormatted, Serializable):
    __schema_format__ = "money"
    DEFAULT_LOCALE = None

    def __new__(
        cls,
        amount: Union[Decimal, str, int, Money],
        currency: Union[CurrencyCode, str] = CurrencyCode.USD,
        locale: Union[Locale, str] = None,
    ):
        return str.__new__(cls, amount)

    def __init__(
        self,
        amount: Union[Decimal, str, int, Money],
        currency: Union[CurrencyCode, str] = CurrencyCode.USD,
        locale: Union[Locale, str] = None,
    ):
        if isinstance(amount, BaseMoney):
            super().__init__(amount.amount, getattr(amount, "currency", str(currency)))
        elif isinstance(amount, str) and amount:
            value, given_currency = CurrencyParser.extract(amount)
            if given_currency:
                currency = given_currency
            super().__init__(value, str(currency))
        elif not amount:
            super().__init__(0, str(currency))
        else:
            super().__init__(amount, str(currency))
        if locale is None:
            if self.__class__.DEFAULT_LOCALE is None:
                self.__class__.DEFAULT_LOCALE = default_locale("LC_NUMERIC")
            locale = self.__class__.DEFAULT_LOCALE
        self.locale = locale
        self.formatted = format_currency(self.amount, self.currency, locale=self.locale)

    def __str__(self):
        return self.formatted

    def __repr__(self):
        return self.formatted

    def __hash__(self) -> int:
        return BaseMoney.__hash__(self)

    def __lt__(self, other):
        return BaseMoney.__lt__(self, Money(other))

    def __le__(self, other):
        return BaseMoney.__le__(self, Money(other))

    def __eq__(self, other):
        return BaseMoney.__eq__(self, Money(other))

    def __ne__(self, other):
        return BaseMoney.__ne__(self, Money(other))

    def __gt__(self, other):
        return BaseMoney.__gt__(self, Money(other))

    def __ge__(self, other):
        return BaseMoney.__ge__(self, Money(other))

    def __bool__(self):
        return BaseMoney.__bool__(self)

    def __add__(self, other):
        return Money(BaseMoney.__add__(self, Money(other)))

    def __radd__(self, other):
        return Money(BaseMoney.__radd__(self, Money(other)))

    def __sub__(self, other):
        return Money(BaseMoney.__sub__(self, Money(other)))

    def __rsub__(self, other):
        return Money(BaseMoney.__rsub__(self, Money(other)))

    def __mul__(self, other):
        return Money(BaseMoney.__mul__(self, Money(other)))

    def __rmul__(self, other):
        return Money(BaseMoney.__rmul__(self, Money(other)))

    def __truediv__(self, other):
        return Money(BaseMoney.__truediv__(self, Money(other)))

    def __floordiv__(self, other):
        return Money(BaseMoney.__floordiv__(self, Money(other)))

    def __mod__(self, other):
        return Money(BaseMoney.__mod__(self, Money(other)))

    def __divmod__(self, other):
        return Money(BaseMoney.__divmod__(self, Money(other)))

    def __pow__(self, other):
        return Money(BaseMoney.__pow__(self, Money(other)))

    def __neg__(self):
        return Money(BaseMoney.__neg__(self))

    def __pos__(self):
        return Money(BaseMoney.__pos__(self))

    def __abs__(self):
        return Money(BaseMoney.__abs__(self))

    def __int__(self):
        return int(self.amount)

    def __float__(self):
        return float(self.amount)

    def __round__(self, ndigits=None):
        return Money(BaseMoney.__round__(self, ndigits))

    @property
    def friendly(self) -> str:
        symbol = get_decimal_symbol(self.locale)
        return self.formatted.replace(f"{symbol}00", "")

    @property
    def num_cents(self) -> int:
        return int(self.amount * 100)

    def as_cents(self) -> int:
        return self.num_cents

    @classmethod
    def to_cents(cls, amount: Union[Decimal, str, int, Money]) -> int:
        return cls(amount=amount).as_cents()

    @classmethod
    def from_cents(
        cls, amount: int, currency: CurrencyCode = CurrencyCode.USD
    ) -> Money:
        return cls(amount=Decimal(amount) / 100, currency=currency)
