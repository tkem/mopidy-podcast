Configuration
========================================================================

This section describes the configuration values that affect
Mopidy-Podcast's core functions and the bundled :ref:`feeds <feeds>`
directory provider.  For configuring external :ref:`extensions
<extensions>`, please refer to their respective documentation.


General Configuration Values
------------------------------------------------------------------------

.. confval:: podcast/browse_limit

   The maximum number of browse results and podcast episodes to show.

.. confval:: podcast/search_limit

   The maximum number of search results to show.

.. confval:: podcast/search_details

   Whether to return fully detailed search results.  If set to ``off``
   (the default), only a podcast's or episode's name and URI will
   appear in search results, similar to what is shown when browsing.
   If set to ``on``, search results will also include meta information
   such as author name, track counts and lengths, publication dates
   and images, if available.  However, this will slow down searching
   tremendously, so if you enable this you might consider decreasing
   :confval:`podcast/search_limit`.

.. confval:: podcast/update_interval

   The directory update interval in seconds, i.e. how often locally
   stored information should be refreshed.


.. _feeds:

Feeds Directory Configuration Values
------------------------------------------------------------------------

This section lists configuration values specific to the *feeds*
podcast directory provider that is bundled with Mopidy-Podcast.  If
you do not plan to use the *feeds* directory, these can be safely
ignored.

.. confval:: podcast/feeds

   A list of podcast RSS feed URLs to subscribe to.  Individual URLs
   must be seperated by either newlines or commas, with newlines
   preferred.

   To subscribe to some podcasts from NPR_'s highly recommended `All
   Songs Considered`_ program::

     feeds =
         http://www.npr.org/rss/podcast.php?id=510019
         http://www.npr.org/rss/podcast.php?id=510253
         http://www.npr.org/rss/podcast.php?id=510306

.. confval:: podcast/feeds_root_name

   The directory name shown for browsing subscribed feeds.

.. confval:: podcast/feeds_cache_size

   The maximum number of podcast RSS feeds that should be cached.

.. confval:: podcast/feeds_cache_ttl

   The feeds cache *time to live*, i.e. the number of seconds after
   which a cached feed expires and needs to be reloaded.

.. confval:: podcast/feeds_timeout

   The HTTP request timeout when retrieving RSS feeds, in seconds.


Default Configuration
------------------------------------------------------------------------

For reference, this is the default configuration shipped with
Mopidy-Podcast release |release|:

.. literalinclude:: ../mopidy_podcast/ext.conf
   :language: ini


.. _NPR: http://www.npr.org/
.. _All Songs Considered: http://www.npr.org/blogs/allsongs/
