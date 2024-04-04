import re

import babel
import babel.numbers
from babel.numbers import LC_NUMERIC
from communal.enum import StringEnum


class CurrencyCode:
    def __init__(self, code):
        if isinstance(code, CurrencyCode):
            self.code = code
        elif isinstance(code, str):
            self.validate(code)
            self.code = code
        else:
            raise TypeError(
                "First argument given to CurrencyCode constructor should be "
                "either an instance of CurrencyCode or valid three letter "
                "currency code."
            )

    @classmethod
    def validate(self, code, locale=LC_NUMERIC):
        loc = babel.Locale.parse(locale)
        try:
            return loc.currencies[code]
        except KeyError as e:
            raise ValueError(f"'{code}' is not valid currency code.") from e

    @property
    def symbol(self):
        return babel.numbers.get_currency_symbol(
            self.code,
        )

    def __eq__(self, other):
        if isinstance(other, CurrencyCode):
            return self.code == other.code
        elif isinstance(other, str):
            return self.code == other
        else:
            return NotImplemented

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.code)

    def __repr__(self):
        return self.code

    def __str__(self):
        return self.code


CurrencyCode = StringEnum(
    "CurrencyCode",
    [
        (currency, CurrencyCode(currency))
        for currency in babel.Locale(LC_NUMERIC).currencies
    ],
)


class CurrencyParser:
    currency_decimal_symbols = {
        babel.numbers.get_decimal_symbol(loc)
        for loc in babel.localedata.locale_identifiers()
    }
    currency_group_symbols = {
        babel.numbers.get_group_symbol(loc)
        for loc in babel.localedata.locale_identifiers()
    }
    currency_minus_symbols = {
        babel.numbers.get_minus_sign_symbol(loc)
        for loc in babel.localedata.locale_identifiers()
    }
    currency_plus_symbols = {
        babel.numbers.get_plus_sign_symbol(loc)
        for loc in babel.localedata.locale_identifiers()
    }
    currency_symbols = {
        babel.numbers.get_currency_symbol(str(c)): str(c) for c in CurrencyCode
    }

    currency_pattern = "({symbols})|([\\d{numeric}]+)".format(
        symbols="|".join(
            [
                re.escape(s)
                for s in set(currency_symbols.keys()) | set(currency_symbols.values())
            ]
        ),
        numeric="|".join(
            [
                re.escape(s)
                for s in (
                    currency_decimal_symbols
                    | currency_group_symbols
                    | currency_minus_symbols
                    | currency_plus_symbols
                )
            ]
        ),
    )

    group_pattern = re.compile("[{}]".format("".join(currency_group_symbols)))
    numeric_pattern = re.compile("[{}]".format("".join(currency_group_symbols)))

    currency_regex = re.compile(currency_pattern)

    @classmethod
    def extract(cls, s, locale=LC_NUMERIC):
        matches = cls.currency_regex.findall(s)
        currency = None
        value = None
        for c, v in matches:
            if c and not currency:
                currency = c
            if v and not value:
                value = v

            if currency and value:
                break

        loc = babel.Locale.parse(locale)
        value = babel.numbers.parse_decimal(value, locale=loc)

        if currency:
            currency = CurrencyCode(cls.currency_symbols.get(currency, currency))

        return value, currency
