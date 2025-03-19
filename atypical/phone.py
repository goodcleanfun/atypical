from functools import total_ordering

try:
    import phonenumbers
    from phonenumbers.phonenumber import PhoneNumber as BasePhoneNumber
    from phonenumbers.phonenumberutil import NumberParseException
except ImportError:
    phonenumbers = None
    BasePhoneNumber = object
    NumberParseException = Exception

from communal.exceptions import ConfigurationError
from sartorial import JSONSchemaFormatted, Serializable


class PhoneNumberParseException(NumberParseException):
    """
    Catch this as either a PhoneNumberParseException or
    NumberParseException from the phonenumbers library.
    """

    pass


@total_ordering
class PhoneNumber(str, BasePhoneNumber, JSONSchemaFormatted, Serializable):
    """
    Wrapper class for parsing a phone number using the phonenumbers library,
    based on libphonenumber from Google.

    .. phonenumbers library:
       https://github.com/daviddrysdale/python-phonenumbers

    :param raw_number:
        String representation of the phone number.
    :param country:
        Country code of the phone number.
    :param check_region:
        Whether to check the supplied region parameter;
        should always be True for external callers.
        Can be useful for short codes or toll free
    """

    DEFAULT_REGION = "US"
    DEFAULT_FORMAT = "standard"

    __schema_format__ = "phone"

    def __new__(
        cls, raw_number, region: str = DEFAULT_REGION, check_region: bool = True
    ):
        return str.__new__(cls, raw_number)

    def __init__(
        self, raw_number, region: str = DEFAULT_REGION, check_region: bool = True
    ):
        # Bail if phonenumbers is not found.
        if phonenumbers is None:
            raise ConfigurationError("'phonenumbers' is required to use 'PhoneNumber'")

        if isinstance(raw_number, str):
            try:
                self._phone_number = phonenumbers.parse(
                    raw_number, region, _check_region=check_region
                )
            except NumberParseException as e:
                raise PhoneNumberParseException(
                    getattr(e, "error_type", -1), str(e)
                ) from e
        elif isinstance(raw_number, BasePhoneNumber):
            self._phone_number = raw_number
        elif isinstance(raw_number, PhoneNumber):
            self._phone_number = raw_number._phone_number

        region = phonenumbers.region_code_for_country_code(
            self._phone_number.country_code
        )

        super().__init__(
            country_code=self._phone_number.country_code,
            national_number=self._phone_number.national_number,
            extension=self._phone_number.extension,
            italian_leading_zero=self._phone_number.italian_leading_zero,
            raw_input=self._phone_number.raw_input,
            country_code_source=self._phone_number.country_code_source,
            preferred_domestic_carrier_code=(
                self._phone_number.preferred_domestic_carrier_code
            ),
        )
        self.region = region
        self.national = phonenumbers.format_number(
            self._phone_number, phonenumbers.PhoneNumberFormat.NATIONAL
        )
        self.friendly = self.national
        self.international = phonenumbers.format_number(
            self._phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )
        self.standard = phonenumbers.format_number(
            self._phone_number, phonenumbers.PhoneNumberFormat.E164
        )

    def __composite_values__(self):
        return self.national, self.region

    def is_valid_number(self):
        return phonenumbers.is_valid_number(self._phone_number)

    @property
    def area_code(self):
        if self.country_code == 1:
            return str(self.national_number)[:3]
        return None

    def __str__(self):
        return self.standard

    def __repr__(self):
        return self.standard

    def __hash__(self):
        return hash(self.standard)

    def __lt__(self, other):
        if not other:
            return False
        if not isinstance(other, PhoneNumber):
            try:
                other = PhoneNumber(str(other))
            except (PhoneNumberParseException, TypeError):
                return False
        return self.standard < other.standard

    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, PhoneNumber):
            try:
                other = PhoneNumber(str(other))
            except (PhoneNumberParseException, TypeError):
                return False
        return self.standard == other.standard

    def to_string(self) -> str:
        return self.standard

    @classmethod
    def parse(cls, value, region=DEFAULT_REGION, check_region=True):
        return PhoneNumber(value, region=region, check_region=check_region)

    @classmethod
    def serialize(cls, value, format=DEFAULT_FORMAT, region=DEFAULT_REGION):
        if value:
            if not isinstance(value, PhoneNumber):
                value = PhoneNumber(value, region=region)

            if format == "standard" and value.extension:
                return f"{value.standard};ext={value.extension}"

            return getattr(value, format)

        return value
