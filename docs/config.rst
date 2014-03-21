Configuration
========================================================================

This extension has a number of configuration values that can be
tweaked.  However, the :ref:`default configuration <defconf>` contains
everything to get you up and running, and will usually require only a
few modifications to match personal needs.


.. _confvals:

Configuration Values
------------------------------------------------------------------------

.. note::

   Configuration values are still subject to change at this point, so
   be warned before trying any of these.

.. confval:: podcast/browse_label

   The top-level directory name for browsing podcasts.

.. confval:: podcast/browse_limit

   The maximum number of browse results and podcast episodes shown.

.. confval:: podcast/search_limit

   The maximum number of search results shown.

.. confval:: podcast/sort_order

   How to sort podcast episodes for browsing: ``asc`` (oldest first)
   or ``desc`` (newest first).

.. confval:: podcast/update_interval

   Podcast directory update interval in seconds.

.. confval:: podcast/cache_size

   Number of podcasts to cache.

.. confval:: podcast/cache_ttl

   Cache time-to-live in seconds.

   For best results, this should be less than
   :confval:`podcast/update_interval`.

.. confval:: podcast/timeout

   HTTP request timeout in seconds.

.. confval:: podcast/feeds

   A list of links to podcast RSS feeds for the *feeds* directory
   service.

.. confval:: podcast/feeds_label

   The *feeds* directory name to display when browsing.


.. _defconf:

Default Configuration
------------------------------------------------------------------------

For reference, this is the default configuration shipped with
Mopidy-Podcast release |release|:

.. literalinclude:: ../mopidy_podcast/ext.conf
   :language: ini
