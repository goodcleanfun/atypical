from sartorial import Schema

from atypical.email import Email, EmailProvider


def test_email():
    e = Email.parse("example.123+456@gmail")
    assert e.normalized == "example123@gmail.com"
    assert e.sub_address == "456"
    e = Email("example.123@example.com", parse_as=EmailProvider.GMAIL)
    assert e == "example123@example.com"

    class Model(Schema):
        email: Email

    d = Model.to_schema_dict()
    assert d["properties"]["email"]["type"] == "string"
    assert d["properties"]["email"]["format"] == "email"

    NewModel = Schema.from_schema_dict(d)
    n = NewModel(email="example.123@gmail")
    assert isinstance(n.email, Email)
    assert n.email.normalized == "example123@gmail.com"

    m = Model(email="example.123@gmail")
    assert isinstance(m.email, Email)
    assert m.to_json() == '{"email":"example123@gmail.com"}'
