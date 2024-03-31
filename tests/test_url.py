from sartorial import Schema

from atypical.url import URL, NormalizedURL


def test_url():
    u = URL("example.com")
    assert u == "example.com"

    class Model(Schema):
        url: URL

    d = Model.to_schema_dict()
    assert d["properties"]["url"]["type"] == "string"
    assert d["properties"]["url"]["format"] == "url"

    NewModel = Schema.from_schema_dict(d)
    n = NewModel(url="example.com")
    assert isinstance(n.url, URL)
    assert n.url == "example.com"

    m = Model(url="example.com")
    assert isinstance(m.url, URL)
    assert m.to_json() == '{"url":"example.com"}'


def test_normalized_url():
    u = NormalizedURL("example.com")
    assert u.url == "https://example.com/"
    assert u == "example.com"
    d = {u: 1}
    assert URL("https://example.com/") in d

    u = NormalizedURL(
        "https://en.wikipedia.org/wiki/Springfield (toponym)?utm_medium=social&utm_source=foo&utm_campaign=bar&utm_content=blee&utm_term=blah"
    )
    assert u.url == "https://en.wikipedia.org/wiki/Springfield%20(toponym)"
    assert (
        u
        == "https://en.wikipedia.org/wiki/Springfield%20(toponym)?utm_medium=social&utm_source=foo"
    )

    class Model(Schema):
        url: NormalizedURL

    d = Model.to_schema_dict()
    assert d["properties"]["url"]["type"] == "string"
    assert d["properties"]["url"]["format"] == "normalized-url"

    NewModel = Schema.from_schema_dict(d)
    n = NewModel(url="example.com?src=foo")
    print(type(n.url))
    assert isinstance(n.url, NormalizedURL)
    assert n.url == "https://example.com/"
    m = Model(url="example.com?src=foo")
    print(type(m.url))
    assert isinstance(m.url, URL)
    assert m.to_json() == '{"url":"https://example.com/"}'


SCHEME_TESTS = {"http": "http", "HTTP": "http"}


def test_url_normalize_scheme():
    for test, expected in SCHEME_TESTS.items():
        norm = URL.normalize_scheme(test)
        assert norm == expected


HOST_TESTS = {
    "site.com": "site.com",
    "SITE.COM": "site.com",
    "site.com.": "site.com",
    "пример.испытание": "xn--e1afmkfd.xn--80akhbyknj4f",
}


def test_url_normalize_host():
    for test, expected in HOST_TESTS.items():
        norm = URL.normalize_host(test)
        assert norm == expected


PATH_TESTS = {
    "..": "/",
    "": "/",
    "/../foo": "/foo",
    "/..foo": "/..foo",
    "/./../foo": "/foo",
    "/./foo": "/foo",
    "/./foo/.": "/foo/",
    "/.foo": "/.foo",
    "/": "/",
    "/foo..": "/foo..",
    "/foo.": "/foo.",
    "/FOO": "/FOO",
    "/foo/../bar": "/bar",
    "/foo/./bar": "/foo/bar",
    "/foo//": "/foo/",
    "/foo///bar//": "/foo/bar/",
    "/foo/bar/..": "/foo/",
    "/foo/bar/../..": "/",
    "/foo/bar/../../../../baz": "/baz",
    "/foo/bar/../../../baz": "/baz",
    "/foo/bar/../../": "/",
    "/foo/bar/../../baz": "/baz",
    "/foo/bar/../": "/foo/",
    "/foo/bar/../baz": "/foo/baz",
    "/foo/bar/.": "/foo/bar/",
    "/foo/bar/./": "/foo/bar/",
}


def test_url_normalize_path():
    for test, expected in PATH_TESTS.items():
        norm = URL.normalize_path(test, "https")
        assert norm == expected


QUERY_TESTS = {
    "": "",
    "param1=val1&param2=val2": "param1=val1&param2=val2",
    "Ç=Ç": "%C3%87=%C3%87",
    "%C3%87=%C3%87": "%C3%87=%C3%87",
    "q=C%CC%A7": "q=%C3%87",
    "q=foo&utm_medium=social&utm_source=foo&utm_campaign=bar&utm_content=blee&utm_term=blah": "q=foo",
}


def test_url_normalize_query():
    for test, expected in QUERY_TESTS.items():
        norm = URL.normalize_query(test, sort_query_params=False)
        assert norm == expected


SORTED_QUERY_TESTS = {
    "": "",
    "foo=bar&bar=baz": "bar=baz&foo=bar",
    "bar=baz&foo=bar": "bar=baz&foo=bar",
}


def test_url_normalize_sorted_query():
    for test, expected in SORTED_QUERY_TESTS.items():
        norm = URL.normalize_query(test, sort_query_params=True)
        assert norm == expected


FRAGMENT_TESTS = {
    "": "",
    "fragment": "fragment",
    "пример": "%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80",
    "!fragment": "%21fragment",
    "~fragment": "~fragment",
}


def test_url_normalize_fragment():
    for test, expected in FRAGMENT_TESTS.items():
        norm = URL.normalize_fragment(test)
        assert norm == expected
