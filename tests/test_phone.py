from sartorial import Schema

from atypical.phone import PhoneNumber


def test_phone():
    p = PhoneNumber.parse("555-555-5555")
    assert not p.is_valid_number()
    assert p.area_code == "555"
    assert p == "555-555-5555"
    assert p.standard == "+15555555555"
    assert p.friendly == "(555) 555-5555"

    assert PhoneNumber("+1 (555) 555-5555") == PhoneNumber("1 (555) 555-5555")
    assert PhoneNumber("(555) 555-5555") == PhoneNumber("555-555-5555")

    class Model(Schema):
        phone: PhoneNumber

    d = Model.to_schema_dict()
    assert d["properties"]["phone"]["type"] == "string"
    assert d["properties"]["phone"]["format"] == "phone"

    NewModel = Schema.from_schema_dict(d)
    n = NewModel(phone="555-555-5555")
    assert isinstance(n.phone, PhoneNumber)
    assert n.phone == "555-555-5555"
    assert n.phone == "+15555555555"
    assert n.phone.standard == "+15555555555"
    assert n.phone.friendly == "(555) 555-5555"

    assert n.to_json() == '{"phone":"+15555555555"}'
