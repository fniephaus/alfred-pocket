"""Lightweight HTTP library with a requests-like interface."""

import codecs
import json
import mimetypes
import os
import re
import secrets
import socket
import string
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zlib

# pylint: disable=consider-using-with
__version__ = open(
    os.path.join(os.path.dirname(__file__), "version"), encoding="utf-8"
).read()

USER_AGENT = f"Alpynist/{__version__}"

# Valid characters for multipart form data boundaries
BOUNDARY_CHARS = string.digits + string.ascii_letters

# HTTP response codes
RESPONSES = {
    100: "Continue",
    101: "Switching Protocols",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    307: "Temporary Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Request Entity Too Large",
    414: "Request-URI Too Long",
    415: "Unsupported Media Type",
    416: "Requested Range Not Satisfiable",
    417: "Expectation Failed",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
}


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Prevent redirections."""

    def redirect_request(self, *args):  # pylint: disable=unused-argument
        """Ignore redirect."""
        return None


# Adapted from https://gist.github.com/babakness/3901174
class CaseInsensitiveDictionary(dict):
    """Dictionary with caseless key search.

    Enables case insensitive searching while preserving case sensitivity
    when keys are listed, ie, via keys() or items() methods.

    Works by storing a lowercase version of the key as the new key and
    stores the original key-value pair as the key's value
    (values become dictionaries).

    """

    def __init__(self, initval=None):
        """Create new case-insensitive dictionary."""
        super().__init__(self)

        if isinstance(initval, dict):
            for key, value in initval.items():
                self.__setitem__(key, value)
        elif isinstance(initval, list):
            for (key, value) in initval:
                self.__setitem__(key, value)

    def __contains__(self, key):
        return dict.__contains__(self, key.lower())

    def __getitem__(self, key):
        return dict.__getitem__(self, key.lower())["val"]

    def __setitem__(self, key, value):
        return dict.__setitem__(self, key.lower(), {"key": key, "val": value})

    def get(self, key, default=None):
        """Return value for case-insensitive key or default."""
        try:
            v = dict.__getitem__(self, key.lower())
        except KeyError:
            return default

        return v["val"]

    def update(self, other):
        """Update values from other ``dict``."""
        for k, v in list(other.items()):
            self[k] = v

    def items(self):
        """Return ``(key, value)`` pairs."""
        return [(v["key"], v["val"]) for v in dict.values(self)]

    def keys(self):
        """Return original keys."""
        return [v["key"] for v in dict.values(self)]

    def values(self):
        """Return all values."""
        return [v["val"] for v in dict.values(self)]

    def iteritems(self):
        """Iterate over ``(key, value)`` pairs."""
        for v in dict.values(self):
            yield v["key"], v["val"]

    def iterkeys(self):
        """Iterate over original keys."""
        for v in dict.values(self):
            yield v["key"]

    def itervalues(self):
        """Interate over values."""
        for v in dict.values(self):
            yield v["val"]


class Request(urllib.request.Request):
    """Subclass of :class:`urllib.request.Request` that supports custom methods."""

    def __init__(self, *args, **kwargs):
        """Create a new :class:`Request`."""
        self._method = kwargs.pop("method", None)
        urllib.request.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        return self._method.upper()


class Response:
    """
    Returned by :func:`request` / :func:`get` / :func:`post` functions.

    Simplified version of the ``Response`` object in the ``requests`` library.

    >>> r = request('http://www.google.com')
    >>> r.status_code  # int
    200
    >>> r.encoding  # str
    ISO-8859-1
    >>> r.content  # bytes
    <html> ...
    >>> r.text  # str, decoded according to charset in HTTP header/meta tag
    <html> ...
    >>> r.json()  # content parsed as JSON

    """

    def __init__(self, request, stream=False):  # pylint: disable=redefined-outer-name
        """Call `request` with :mod:`urllib` and process results.

        :param request: :class:`Request` instance
        :param stream: Whether to stream response or retrieve it all at once
        :type stream: bool

        """
        self.request = request
        self._stream = stream
        self.url = None
        self.raw = None
        self._encoding = None
        self.error = None
        self.status_code = None
        self.reason = None
        self.headers = CaseInsensitiveDictionary()
        self._content = None
        self._content_loaded = False
        self._gzipped = False

        # Execute query
        try:
            # pylint: disable=consider-using-with
            self.raw = urllib.request.urlopen(request)
        except urllib.error.HTTPError as err:
            self.error = err

            try:
                self.url = err.geturl()
            # sometimes (e.g. when authentication fails)
            # urllib can't get a URL from an HTTPError
            # This behaviour changes across Python versions,
            # so no test cover (it isn't important).
            except AttributeError:  # pragma: no cover
                pass

            self.status_code = err.code
        else:
            self.status_code = self.raw.getcode()
            self.url = self.raw.geturl()
        self.reason = RESPONSES.get(self.status_code)

        # Parse additional info if request succeeded
        if not self.error:
            headers = self.raw.info()
            self.transfer_encoding = headers.get_content_charset()
            self.mimetype = headers.get("content-type")

            for key in list(headers.keys()):
                self.headers[key.lower()] = headers.get(key)

            # Is content gzipped?
            # Transfer-Encoding appears to not be used in the wild
            # (contrary to the HTTP standard), but no harm in testing
            # for it
            if "gzip" in headers.get("content-encoding", "") or "gzip" in headers.get(
                "transfer-encoding", ""
            ):
                self._gzipped = True

    @property
    def stream(self):
        """Whether response is streamed.

        Returns:
            bool: `True` if response is streamed.

        """
        return self._stream

    @stream.setter
    def stream(self, value):
        if self._content_loaded:
            raise RuntimeError("`content` has already been read from this Response.")

        self._stream = value

    def json(self):
        """Decode response contents as JSON.

        :returns: object decoded from JSON
        :rtype: list, dict or str

        """
        return json.loads(self.content)

    @property
    def encoding(self):
        """Text encoding of document or ``None``.

        :returns: Text encoding if found.
        :rtype: str or ``None``

        """
        if not self._encoding:
            self._encoding = self._get_encoding()

        return self._encoding

    @property
    def content(self):
        """Content of the response in bytes.

        :returns: Body of HTTP response
        :rtype: bytes

        """
        if not self._content:
            # Decompress gzipped content
            if self._gzipped:
                decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
                self._content = decoder.decompress(self.raw.read())
            else:
                self._content = self.raw.read()

            self._content_loaded = True

        return self._content

    @property
    def text(self):
        """Content of the response in unicode.

        If no encoding can be determined from HTTP headers or the content
        itself, the encoded response body will be returned instead.

        :returns: Body of HTTP response
        :rtype: str or bytes

        """
        if self.encoding:
            return unicodedata.normalize("NFC", str(self.content, self.encoding))

        return self.content

    def iter_content(self, chunk_size=4096, decode_unicode=False):
        """Iterate over response data.

        :param chunk_size: Number of bytes to read into memory
        :type chunk_size: int
        :param decode_unicode: Decode to Unicode using detected encoding
        :type decode_unicode: bool
        :returns: iterator

        """
        if not self.stream:
            raise RuntimeError(
                "You cannot call `iter_content` on a Response unless you passed `stream=True` to `get()`/`post()`/`request()`."
            )

        if self._content_loaded:
            raise RuntimeError("`content` has already been read from this Response.")

        def decode_stream(iterator, r):
            dec = codecs.getincrementaldecoder(r.encoding)(errors="replace")

            for chunk in iterator:
                data = dec.decode(chunk)

                if data:
                    yield data

            data = dec.decode(b"", final=True)

            if data:  # pragma: no cover
                yield data

        def generate():
            if self._gzipped:
                decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)

            while True:
                chunk = self.raw.read(chunk_size)

                if not chunk:
                    break

                if self._gzipped:
                    chunk = decoder.decompress(chunk)

                yield chunk

        chunks = generate()

        if decode_unicode and self.encoding:
            chunks = decode_stream(chunks, self)

        return chunks

    def save_to_path(self, filepath):
        """Save retrieved data to file at ``filepath``.

        :param filepath: Path to save retrieved data.

        """
        filepath = os.path.abspath(filepath)
        dirname = os.path.dirname(filepath)

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        self.stream = True

        with open(filepath, "wb") as fileobj:
            for data in self.iter_content():
                fileobj.write(data)

    def raise_for_status(self):
        """Raise stored error if one occurred.

        error will be instance of :class:`urllib.error.HTTPError`
        """
        if self.error is not None:
            raise self.error

    def _get_encoding(self):
        """Get encoding from HTTP headers or content.

        :returns: encoding or `None`
        :rtype: str or ``None``

        """
        headers = self.raw.info()
        encoding = None

        if headers.get_content_charset():
            encoding = headers.get_content_charset()

        if not self.stream:  # Try sniffing response content
            # Encoding declared in document should override HTTP headers
            if self.mimetype == "text/html":  # sniff HTML headers
                match = re.search(
                    r"""<meta.+charset=["']{0,1}(.+?)["'].*>""", self.content
                )

                if match:
                    encoding = match.group(1)

            elif (
                self.mimetype.startswith("application/")
                or self.mimetype.startswith("text/")
            ) and "xml" in self.mimetype:  # noqa
                match = re.search(
                    r"""<?xml.+encoding=["'](.+?)["'][^>]*\?>""", self.content
                )

                if match:
                    encoding = match.group(1)

        # Format defaults
        if self.mimetype == "application/json" and not encoding:
            # The default encoding for JSON
            encoding = "utf-8"

        elif self.mimetype == "application/xml" and not encoding:
            # The default for 'application/xml'
            encoding = "utf-8"

        if encoding:
            encoding = encoding.lower()

        return encoding


def request(
    method,
    url,
    params=None,
    data=None,
    json_data=None,
    headers=None,
    files=None,
    auth=None,
    timeout=60,
    allow_redirects=False,
    stream=False,
):
    """Initiate an HTTP(S) request. Returns :class:`Response` object.

    :param method: 'GET' or 'POST'
    :type method: str
    :param url: URL to open
    :type url: str
    :param params: mapping of URL parameters
    :type params: dict
    :param data: mapping of form data ``{'field_name': 'value'}`` or
        :class:`str`
    :type data: dict or str
    :param json_data: json data to send in the body of the request
        :class:`dict`
    :type json_data: dict
    :param headers: HTTP headers
    :type headers: dict
    :param files: files to upload (see below).
    :type files: dict
    :param auth: username, password
    :type auth: tuple
    :param timeout: connection timeout limit in seconds
    :type timeout: int
    :param allow_redirects: follow redirections
    :type allow_redirects: bool
    :param stream: Stream content instead of fetching it all at once.
    :type stream: bool
    :returns: Response object
    :rtype: :class:`Response`

    The ``files`` argument is a dictionary::

        {
            "fieldname": {
                "filename": "blah.txt",
                "content": "<binary data>",
                "mimetype": "text/plain",
            }
        }

    * ``fieldname`` is the name of the field in the HTML form.
    * ``mimetype`` is optional. If not provided, :mod:`mimetypes` will
      be used to guess the mimetype, or ``application/octet-stream``
      will be used.

    """
    socket.setdefaulttimeout(timeout)

    # Default handlers
    openers = [urllib.request.ProxyHandler(urllib.request.getproxies())]

    if not allow_redirects:
        openers.append(NoRedirectHandler())

    if auth is not None:  # Add authorisation handler
        username, password = auth
        password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, url, username, password)
        auth_manager = urllib.request.HTTPBasicAuthHandler(password_manager)
        openers.append(auth_manager)

    # Install our custom chain of openers
    opener = urllib.request.build_opener(*openers)
    urllib.request.install_opener(opener)

    if not headers:
        headers = CaseInsensitiveDictionary()
    else:
        headers = CaseInsensitiveDictionary(headers)

    if "User-Agent" not in headers:
        headers["User-Agent"] = USER_AGENT

    # Accept gzip-encoded content
    encodings = [s.strip() for s in headers.get("Accept-Encoding", "").split(",")]
    if "gzip" not in encodings:
        encodings.append("gzip")

    headers["Accept-Encoding"] = ", ".join(encodings)

    if files:
        if not data:
            data = {}

        new_headers, data = _encode_multipart_formdata(data, files)
        headers.update(new_headers)
    elif data and isinstance(data, dict):
        data = urllib.parse.urlencode(data)

    if data:
        data = data.encode("utf-8")

    if json_data and not data:
        data = json.dumps(json_data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    if params:  # GET args (POST args are handled in _encode_multipart_formdata)
        scheme, netloc, path, query, fragment = urllib.parse.urlsplit(url)

        if query:  # Combine query string and `params`
            url_params = urllib.parse.parse_qs(query)
            # `params` take precedence over URL query string
            url_params.update(params)
            params = url_params

        query = urllib.parse.urlencode(params, doseq=True)
        url = urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))

    req = Request(url, data, headers, method=method)
    return Response(req, stream)


def get(
    url,
    params=None,
    headers=None,
    auth=None,
    timeout=60,
    allow_redirects=True,
    stream=False,
):
    """Initiate a GET request. Arguments as for :func:`request`.

    :returns: :class:`Response` instance

    """
    return request(
        "GET",
        url,
        params,
        headers=headers,
        auth=auth,
        timeout=timeout,
        allow_redirects=allow_redirects,
        stream=stream,
    )


def delete(
    url,
    params=None,
    data=None,
    headers=None,
    auth=None,
    timeout=60,
    allow_redirects=True,
    stream=False,
):
    """Initiate a DELETE request. Arguments as for :func:`request`.

    :returns: :class:`Response` instance

    """
    return request(
        "DELETE",
        url,
        params,
        data,
        headers=headers,
        auth=auth,
        timeout=timeout,
        allow_redirects=allow_redirects,
        stream=stream,
    )


def post(
    url,
    params=None,
    data=None,
    json_data=None,
    headers=None,
    files=None,
    auth=None,
    timeout=60,
    allow_redirects=False,
    stream=False,
):
    """Initiate a POST request. Arguments as for :func:`request`.

    :returns: :class:`Response` instance

    """
    return request(
        "POST",
        url,
        params,
        data,
        json_data,
        headers,
        files,
        auth,
        timeout,
        allow_redirects,
        stream,
    )


def put(
    url,
    params=None,
    data=None,
    headers=None,
    files=None,
    auth=None,
    timeout=60,
    allow_redirects=False,
    stream=False,
):
    """Initiate a PUT request. Arguments as for :func:`request`.

    :returns: :class:`Response` instance

    """
    return request(
        "PUT", url, params, data, headers, files, auth, timeout, allow_redirects, stream
    )


def _encode_multipart_formdata(fields, files):
    """Encode form data (``fields``) and ``files`` for POST request.

    :param fields: mapping of ``{name: value}`` pairs for normal form fields.
    :type fields: dict
    :param files: dictionary of fieldnames/files elements for file data.
                  See below for details.
    :type files: dict of :class:`dict`
    :returns: ``(headers, body)`` ``headers`` is a
        :class:`dict` of HTTP headers
    :rtype: 2-tuple ``(dict, str)``

    The ``files`` argument is a dictionary::

        {
            "fieldname": {
                "filename": "blah.txt",
                "content": "<binary data>",
                "mimetype": "text/plain",
            }
        }

    - ``fieldname`` is the name of the field in the HTML form.
    - ``mimetype`` is optional. If not provided, :mod:`mimetypes` will
      be used to guess the mimetype, or ``application/octet-stream``
      will be used.

    """

    def get_content_type(filename):
        """Return or guess mimetype of ``filename``.

        :param filename: filename of file
        :type filename: unicode/str
        :returns: mime-type, e.g. ``text/html``
        :rtype: str

        """
        return mimetypes.guess_type(filename)[0] or "application/octet-stream"

    boundary = "-----" + "".join(secrets.choice(BOUNDARY_CHARS) for i in range(30))
    crlf = "\r\n"
    output = []

    # Normal form fields
    for (k, v) in list(fields.items()):
        if isinstance(k, str):
            k = k.encode("utf-8")

        if isinstance(v, str):
            v = v.encode("utf-8")

        output.append("--" + boundary)
        output.append(f'Content-Disposition: form-data; name="{k}"')
        output.append("")
        output.append(v)

    # Files to upload
    for k, v in list(files.items()):
        filename = v["filename"]
        content = v["content"]

        if "mimetype" in v:
            mimetype = v["mimetype"]
        else:
            mimetype = get_content_type(filename)

        if isinstance(k, str):
            k = k.encode("utf-8")

        if isinstance(filename, str):
            filename = filename.encode("utf-8")

        if isinstance(mimetype, str):
            mimetype = mimetype.encode("utf-8")

        output.append("--" + boundary)
        output.append(
            f'Content-Disposition: form-data; name="{k}"; filename="{filename}"'  # noqa
        )
        output.append(f"Content-Type: {mimetype}")
        output.append("")
        output.append(content)

    output.append("--" + boundary + "--")
    output.append("")
    body = crlf.join(output)
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
    }
    return (headers, body)
