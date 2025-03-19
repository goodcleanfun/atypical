import unicodedata
from pathlib import Path
from typing import ForwardRef, Union
from urllib.parse import quote as quote_orig
from urllib.parse import unquote as unquote_orig

import furl
from communal.encoding import safe_decode
from sartorial import JSONSchemaFormatted, Serializable

__all__ = ["URL", "NormalizedURL"]

URL = ForwardRef("URL")


class URL(str, furl.furl, JSONSchemaFormatted, Serializable):
    __schema_format__ = "url"

    DEFAULT_CHARSET = "utf-8"
    DEFAULT_SCHEME = "https"

    SOURCE_QUERY_PARAMS = {
        "src",
        "source",
        "utm_medium",
        "utm_source",
        "utm_campaign",
        "utm_content",
        "utm_term",
    }

    def __new__(cls, url: str = "", is_normalized=False, **kwargs):
        f = furl.furl(url, **kwargs)
        return str.__new__(cls, f)

    def __init__(self, url: str = "", is_normalized=False, **kwargs):
        super().__init__(url, **kwargs)
        self.is_normalized = is_normalized

    def __eq__(self, other):
        if self.is_normalized and not (isinstance(other, URL) and other.is_normalized):
            other = URL.normalize(other)
        elif not self.is_normalized and not isinstance(other, URL):
            other = URL(other)
        return self.url == other.url

    def __hash__(self):
        return hash(self.url)

    def __str__(self):
        return self.url

    def __repr__(self):
        return self.url

    @classmethod
    def validate(cls, value):
        return cls(value)

    @classmethod
    def parse(cls, value):
        if value is not None:
            return cls(value)
        return value

    @classmethod
    def provide_url_scheme(cls, url, default_scheme=DEFAULT_SCHEME):
        """Make sure the URL has a scheme.
        Params:
            url : string : the URL
            default_scheme : string : the default scheme to use, e.g. 'https'
        Returns:
            string : updated url with validated/attached scheme
        """
        has_scheme = "://" in url
        is_universal_scheme = url.startswith("//")
        is_file_path = url == "-" or (url.startswith("/") and not is_universal_scheme)
        if not url or has_scheme or is_file_path:
            return url
        if is_universal_scheme:
            return default_scheme + ":" + url
        return default_scheme + "://" + url

    @classmethod
    def cleanup(cls, url):
        """Clean up the URL, remove shebangs and trailing space/ampersands/question marks.
        Params:
            url : string : the URL
        Returns:
            string : update url
        """
        url = url.replace("#!", "?_escaped_fragment_=")
        url = url.rstrip("&? ")
        return url

    @classmethod
    def normalize_scheme(cls, scheme: str) -> str:
        """Lowercase scheme
        Params:
            scheme : string : url scheme, e.g., 'https'
        Returns:
            string : normalized scheme data.
        """
        return scheme.lower() if scheme is not None else scheme

    @classmethod
    def normalize_host(cls, host: str, charset=DEFAULT_CHARSET) -> str:
        """Normalize the host, lowercase, remove trailing dots, encode IDN domains.
        Params:
            host : string : url host, e.g., 'example.com'
        Returns:
            string : normalized host data.
        """
        if host is None:
            return host
        host = safe_decode(host, charset)
        host = host.lower()
        host = host.strip(".")
        host = host.encode("idna").decode(charset)
        return host

    @classmethod
    def unquote(cls, string, charset="utf-8"):
        """URL decode a string and normalize unicode to NFC
        Params:
            string : string to be unquoted
            charset : string : optional : output encoding
        Returns:
            string : an unquoted and normalized string
        """
        string = unquote_orig(string)
        string = safe_decode(string, charset)
        string = unicodedata.normalize("NFC", string).encode(charset)
        return string

    @classmethod
    def quote(cls, string, safe="/"):
        """URL encode a string, but do not encode the safe characters.
        Params:
            string : string to be quoted
            safe : string of safe characters
        Returns:
            string : quoted string
        """
        string = quote_orig(string, safe)
        return string

    @classmethod
    def normalize_path(cls, path: Union[str, Path], scheme) -> str:
        """Normalize path part of the url. Quote only the necessary parts
        of the URL (e.g., spaces but not parens, etc.)
        Params:
            path : string : url path, e.g., '/path/to/page.html'
            scheme : string : url scheme, e.g., 'https'
        Returns:
            string : normalized path data.
        """
        # Only perform percent-encoding where it is essential.
        # Always use uppercase A-through-F characters when percent-encoding.
        # All portions of the URI must be utf-8 encoded NFC from Unicode strings
        path = cls.quote(cls.unquote(str(path)), "~:/?#[]@!$&'()*+,;=")
        # Prevent dot-segments appearing in non-relative URI paths.
        if scheme is None or scheme in ["", "http", "https", "ftp", "file"]:
            output, part = [], None
            for part in path.split("/"):
                if part == "":
                    if not output:
                        output.append(part)
                elif part == ".":
                    pass
                elif part == "..":
                    if len(output) > 1:
                        output.pop()
                else:
                    output.append(part)
            if part in ["", ".", ".."]:
                output.append("")
            path = "/".join(output)
        # For schemes that define an empty path to be equivalent to a path of "/",
        # use "/".
        if not path and scheme in ["http", "https", "ftp", "file"]:
            path = "/"
        return path

    @classmethod
    def normalize_fragment(cls, fragment: str) -> str:
        """Normalize fragment part of the url, quote all except ~
        Params:
            fragment : string : url fragment, e.g., 'fragment'
        Returns:
            string : normalized fragment data.
        """
        return cls.quote(cls.unquote(str(fragment)), "~")

    @classmethod
    def normalize_query(cls, query, sort_query_params=True):
        """Normalize query part of the url. Optionally sort the query params
        and remove common source code parameters such as utm tags
        Params:
            query : string : url query, e.g., 'param1=val1&param2=val2'
        Returns:
            string : normalized query data.
        """
        if not isinstance(query, furl.Query):
            query = furl.Query(query)
        for k in cls.SOURCE_QUERY_PARAMS:
            query.params.pop(k, None)
        params = [
            (cls.quote(cls.unquote(k)), cls.quote(cls.unquote(v)))
            for k, v in query.params.items()
        ]
        if sort_query_params:
            params = sorted(params)
        return "&".join(f"{k}={v}" for k, v in params)

    @classmethod
    def normalize(
        cls,
        url: str,
        charset=DEFAULT_CHARSET,
        default_scheme=DEFAULT_SCHEME,
        sort_query_params=True,
    ):
        """Normalize the URL to use percent-encoding (only where necessary and always using uppercase A-through-F characters),
        lowercase scheme and host, remove default port numbers, remove dot-segments, remove source code parameters such as utm tags,
        and by default sort the query parameters (though this is optional).
        >>> URL.normalize('https://en.wikipedia.org/wiki/Springfield (toponym)?utm_medium=social&utm_source=foo&utm_campaign=bar&utm_content=blee&utm_term=blah')
        'https://en.wikipedia.org/wiki/Springfield%20(toponym)'
        Params:
            url : string : the URL
            charset : string : the charset to use, e.g. 'utf-8'
            default_scheme : string : default scheme to use, e.g. 'https'
            sort_query_params : bool : whether to sort the query parameters
        Returns:
            URL : normalized url (subclass of str with additional methods and properties)
        """
        if not url:
            return url
        if isinstance(url, URL):
            url = str(url)
        url = cls.provide_url_scheme(url, default_scheme)
        url = cls.cleanup(url)
        url = URL(url)
        url = url.set(
            scheme=cls.normalize_scheme(url.scheme),
            host=cls.normalize_host(url.host, charset),
            query=cls.normalize_query(url.query, sort_query_params),
            fragment=cls.normalize_fragment(url.fragment),
        )
        if not url.username:
            url.username = None

        if not url.password:
            url.password = None

        url = url.set(
            path=cls.normalize_path(url.path, url.scheme),
        )
        url.is_normalized = True
        return url


class NormalizedURL(URL):
    __schema_format__ = "normalized-url"

    def __init__(self, url: str = "", **kwargs):
        u = URL.normalize(url)
        super().__init__(u.url, is_normalized=True, **kwargs)
