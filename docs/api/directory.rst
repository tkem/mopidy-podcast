Mopidy-Podcast Directory Provider
========================================================================

.. module:: mopidy_podcast.directory

A :class:`PodcastDirectory` provides access to collections (also
termed directories in Mopidy), podcasts and episodes, possibly via an
external directory service.  Each :class:`PodcastDirectory` instance
manages its own private namespace of URI references, all starting with
an absolute path and optionally containg a query string and fragment
identifier.  The URI reference :const:`/` specifies the *root* of a
podcast directory, and any two podcast directories may use the same URI
reference, e.g. :const:`/Music?topPodcasts`, for different resources.

A :class:`PodcastDirectory` may also register one or more URI schemes
via the :attr:`uri_schemes` attribute.  For example, the *feeds*
directory bundled with Mopidy-Podcast already registers the
:const:`file`, :const:`ftp`, :const:`http` and :const:`https` schemes,
assuming URIs with these schemes point to podcast RSS feeds.  By
returning an absolute URI with one of these schemes, a podcast
directory actually delegates retrieving and parsing the respective
resource to the *feeds* directory.


.. autoclass:: PodcastDirectory

   .. autoattribute:: name

      Subclasses must override this attribute with a string starting
      with an ASCII character and consisting solely of ASCII
      characters, digits and hyphens (:const:`-`).

   .. autoattribute:: root_name

      Subclasses must override this attribute if they implement the
      :func:`browse` method.

   .. autoattribute:: uri_schemes

      Subclasses that provide support for additional URI schemes must
      implement the :func:`get` method for the specified schemes, and
      must also support absolute URIs in their :func:`browse` and
      :func:`search` methods.

      Note that the :const:`file`, :const:`ftp`, :const:`http` and
      :const:`https` schemes are already handled by the *feeds*
      directory implementation.

   .. automethod:: get

      `uri` is an absolute URI corresponding to one of the configured
      :attr:`uri_schemes`.

      If a subclass does not override :attr:`uri_schemes`, this method
      need not be implemented.

      :param string uri: podcast URI
      :rtype: :class:`mopidy_podcast.models.Podcast`

   .. automethod:: browse

      `uri` may be either a URI reference starting with :const:`/`, or
      an absolute URI with one of the configured :attr:`uri_schemes`.

      `limit` specifies the maximum number of objects to return, or
      :const:`None` if no such limit is given.

      Returns a list of :class:`mopidy_podcast.models.Ref` objects for
      the directories, podcasts and episodes at the given `uri`.

      :param string uri: browse URI
      :param int limit: browse limit
      :rtype: :class:`mopidy_podcast.models.Ref` iterable

   .. automethod:: search

      `uri` may be either a URI reference starting with :const:`/`, or
      an absolute URI with one of the configured :attr:`uri_schemes`.

      `terms` is a list of strings specifying search terms.

      `attr` may be an attribute name which must be matched, or
      :const:`None` if any attribute may match `terms`.

      `type`, if given, specifies the type of items to search for, and
      must be either :attr:`mopidy_podcast.models.Ref.PODCAST` or
      :attr:`mopidy_podcast.models.Ref.EPISODE`.

      `limit` specifies the maximum number of objects to return, or
      :const:`None` if no such limit is given.

      Returns a list of :class:`mopidy_podcast.models.Ref` objects for
      the matching podcasts and episodes found at the given `uri`.

      :param string uri: browse URI
      :param terms: search terms
      :type terms: list of strings
      :param string attr: search attribute
      :param string type: search result type
      :param int limit: search limit
      :rtype: :class:`mopidy_podcast.models.Ref` iterable

   .. automethod:: refresh

      This method is called right after :func:`__init__` and should be
      used to perform potentially time-consuming initialization, such
      as retrieving data from a Web site.

      This method may also be called periodically as a request to
      update any locally cached data.

      :param string uri: refresh URI
