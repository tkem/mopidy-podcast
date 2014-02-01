"""RFC 3986 compliant, scheme-agnostic replacement for urlparse.
The urlparse module is not compliant with RFC 3986, and is generally
unusable with custom (private) URI schemes.

"""

from __future__ import unicode_literals

import re

from collections import namedtuple

URI_RE = re.compile(r"""
(?:([^:/?#]+):)?  # scheme
(?://([^/?#]*))?  # authority
([^?#]*)          # path
(?:\?([^#]*))?    # query
(?:\#(.*))?       # fragment
""", flags=(re.VERBOSE))

URI_FIELDS = ('scheme', 'authority', 'path', 'query', 'fragment')


class SplitResult(namedtuple('SplitResult', URI_FIELDS)):

    # TODO: getuserinfo(), gethost(), getport()

    def geturi(self):
        return uriunsplit(self)


def urisplit(uri):
    """Split a URI into a named tuple with five components:
    <scheme>://<authority>/<path>?<query>#<fragment>.  Note that
    %-escapes are not expaneded.

    """
    return SplitResult(*URI_RE.match(uri).groups(''))


def uriunsplit(data):
    """Combine the elements of a tuple as returned by urisplit() into a
    complete URI as a string.  The data argument can be any five-item
    iterable.  Note that this may result in a slightly different, but
    equivalent URI string.

    """
    scheme, authority, path, query, fragment = data
    if authority:
        if path.startswith('/'):
            uri = '//' + authority + path
        else:
            uri = '//' + authority + '/' + path
    elif path.startswith('/'):
        # RFC 3986 3.3: If a URI does not contain an authority
        # component, then the path cannot begin with two slash
        # characters ("//").
        uri = '/' + path.lstrip('/')
    else:
        uri = path
    if scheme:
        uri = scheme + ':' + uri
    if query:
        uri += '?' + query
    if fragment:
        uri += '#' + fragment
    return uri


def uricompose(scheme='', authority='', path='', query='', fragment=''):
    return uriunsplit((scheme, authority, path, query, fragment))
