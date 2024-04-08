import pytest
from jinja2.exceptions import UndefinedError
from sartorial import Schema

from atypical.templated import Templated


def test_templated():
    t = Templated("{{ foo }}")
    assert t.render(foo="bar") == "bar"
    with pytest.raises(UndefinedError) as e:
        t.render()
    assert str(e.value) == "'foo' is undefined"
    assert Templated("{{ foo }}", foo="bar").render() == "bar"
    assert Templated("{{ foo }}", foo="bar").render(foo="baz") == "baz"
    assert Templated("{{ num }}").render(num=1) == "1"
    assert t.is_jinja("{{ foo }}")
    assert not t.is_jinja("foo")
    assert repr(t) == "{{ foo }}"
    assert str(t) == "{{ foo }}"
    assert t == "{{ foo }}"
    assert t == Templated("{{ foo }}")
    assert t != "{{ bar }}"
    assert t != Templated("{{ bar }}")


def test_templated_in_schema():
    class MyModel(Schema):
        foo: Templated

    m = MyModel(foo="{{ bar }}")
    assert m.foo == "{{ bar }}"
    assert m.foo.render(bar="baz") == "baz"
    assert m.to_json() == '{"foo":"{{ bar }}"}'

    d = MyModel.to_schema_dict()
    assert d["properties"]["foo"]["type"] == "string"
    assert d["properties"]["foo"]["format"] == "jinja2"

    NewModel = Schema.from_schema_dict(d)
    n = NewModel(foo="{{ bar }}")
    assert isinstance(n.foo, Templated)
    assert n.foo.render(bar="baz") == "baz"
