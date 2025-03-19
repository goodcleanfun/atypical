from email.utils import parseaddr
from functools import total_ordering

from communal.enum import StringEnum
from sartorial import JSONSchemaFormatted, Serializable


class EmailProvider(StringEnum):
    FASTMAIL = "fastmail"
    GMAIL = "gmail"
    MICROSOFT = "microsoft"
    YAHOO = "yahoo"


@total_ordering
class Email(str, JSONSchemaFormatted, Serializable):
    __schema_format__ = "email"

    TLD_MAP = {
        "con": "com",
    }

    DOMAIN_MISSPELLINGS = {
        "gamil.com": "gmail.com",
        "gogglemail.com": "googlemail.com",
        "googlmail.com": "googlemail.com",
        "goglemail.com": "googlemail.com",
        "hotmial.com": "hotmail.com",
        "homtail.com": "hotmail.com",
        "hoitmail.com": "hotmail.com",
        "homail.com": "hotmail.com",
        "homil.com": "hotmail.com",
        "hotmaill.com": "hotmail.com",
        "yaho.com": "yahoo.com",
        "uahoo.com": "yahoo.com",
        "ayhoo.com": "yahoo.com",
    }

    FASTMAIL_DOMAINS = {"fastmail.com", "messagingengine.com", "fastmail.fm"}
    GMAIL_DOMAINS = {"google.com", "googlemail.com", "gmail.com"}
    MICROSOFT_DOMAINS = {"hotmail.com", "outlook.com", "live.com"}
    YAHOO_DOMAINS = {"yahoodns.net", "yahoo.com", "ymail.com"}

    COMMON_DOMAIN_TLDS = dict(
        [
            domain.split(".", 1)
            for domain in (
                FASTMAIL_DOMAINS | GMAIL_DOMAINS | MICROSOFT_DOMAINS | YAHOO_DOMAINS
            )
        ]
    )

    def __new__(cls, email_address: str, parse_as: EmailProvider = None):
        return str.__new__(cls, email_address)

    def __init__(self, email_address: str, parse_as: EmailProvider = None):
        name, email_address = parseaddr(email_address)
        self.name = name.strip()

        address, domain = email_address.lower().split("@")
        sub_address = None

        if domain in self.COMMON_DOMAIN_TLDS:
            domain = ".".join([domain, self.COMMON_DOMAIN_TLDS[domain]])

        if "." not in domain:
            raise ValueError(f"Invalid email {email_address}: no TLD in {domain}")
        sub_domains, tld = domain.rsplit(".", 1)
        tld = self.TLD_MAP.get(tld, tld)
        domain = ".".join([sub_domains, tld])

        domain = self.DOMAIN_MISSPELLINGS.get(domain, domain)

        domain = ".".join([sub_domains, tld])

        domain = self.DOMAIN_MISSPELLINGS.get(domain, domain)

        self.domain = domain
        self.sub_domains = sub_domains
        self.tld = tld

        # Plus addressing is supported by Microsoft domains and FastMail
        if domain in self.GMAIL_DOMAINS or parse_as == EmailProvider.GMAIL:
            address = address.replace(".", "")
            if "+" in address:
                address, sub_address = address.split("+", 1)
        # Yahoo domain handling of - is like plus addressing
        elif domain in self.YAHOO_DOMAINS or parse_as == EmailProvider.YAHOO:
            if "-" in address:
                address = address.split("-")[0]
        elif domain in self.MICROSOFT_DOMAINS or parse_as == EmailProvider.MICROSOFT:
            if "+" in address:
                address, sub_address = address.split("+", 1)
        # FastMail has domain part username aliasing and plus addressing
        elif domain in self.FASTMAIL_DOMAINS or parse_as == EmailProvider.FASTMAIL:
            domain_segments = domain.split(".")
            if len(domain_segments) > 2:
                address = domain_segments[0]
                domain = ".".join(domain_segments[1:])
            elif "+" in address:
                address, sub_address = address.split("+", 1)

        self.address = address
        self.sub_address = sub_address
        self.normalized = "@".join([address, domain])
        if not sub_address:
            self.full = self.normalized
        else:
            self.full = f"{self.address}+{self.sub_address}@{self.domain}"

    def __str__(self):
        return self.normalized

    def __repr__(self):
        return self.normalized

    def __hash__(self):
        return hash(self.normalized)

    def __lt__(self, other):
        if not other:
            return False
        if not isinstance(other, Email):
            try:
                other = Email(other)
            except (ValueError, TypeError):
                return False
        return self.normalized < other.normalized

    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, Email):
            try:
                other = Email(other)
            except (ValueError, TypeError):
                return False
        return self.normalized == other.normalized

    @classmethod
    def parse(cls, email_address: str, parse_as: EmailProvider = None):
        if email_address and isinstance(email_address, str):
            return cls(email_address, parse_as=parse_as)
        else:
            return None

    @classmethod
    def serialize(cls, email_address):
        if isinstance(email_address, Email):
            return str(email_address.normalized)
        return email_address

    @classmethod
    def serialize_full(cls, email_address):
        if isinstance(email_address, Email):
            return str(email_address.full)
        return email_address

    def add_sub_address(self, sub_address):
        if not sub_address:
            return
        self.sub_address = sub_address
        self.full = f"{self.address}+{sub_address}@{self.domain}"

    @classmethod
    def with_sub_address(cls, email_address, sub_address):
        email = Email(email_address)
        if sub_address:
            email.add_sub_address(sub_address)
        return email
