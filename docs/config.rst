*************
Configuration
*************

This extension provides a number of configuration values that can be
tweaked.  However, the :ref:`default configuration <defconf>` should
contain everything to get you up and running, and will usually require
only a few modifications, if any, to match personal preferences.


.. _confvals:

Configuration Values
====================

.. confval:: podcast/enabled

   Whether this extension should be enabled or not.

.. confval:: podcast/browse_root

   A local path or URL pointing to an OPML syndication feed to use as
   the root for browsing the *Podcasts* directory in Mopidy.  Relative
   paths refer to files in the extension's configuration directory
   [#footnote1]_.

   For example, this will point the *Podcasts* directory to a
   collection of all the BBC Radio and Music feeds::

      browse_root = http://www.bbc.co.uk/podcasts.opml

   The default value is ``Podcasts.opml``, so simply exporting your
   subscribed feeds from your favorite podcast client under this name
   and dropping the file in Mopidy-Podcast's configuration directory
   is usually all you need to do.

   If set to an empty string, the *Podcasts* directory will be hidden
   when browsing Mopidy.

.. confval:: podcast/browse_order

   Whether to sort podcast episodes by ascending (``asc``) or
   descending (``desc``) publication date for browsing.

.. confval:: podcast/lookup_order

   Whether to sort podcast episodes by ascending (``asc``) or
   descending (``desc``) publication date for lookup, for example when
   adding a podcast to Mopidy's tracklist.

.. confval:: podcast/cache_size

   The maximum number of podcast feeds that will be cached in memory.

.. confval:: podcast/cache_ttl

   The cache's *time to live*, i.e. the number of seconds after which
   a cached feed expires and needs to be reloaded.

.. confval:: podcast/timeout

   The HTTP request timeout when retrieving podcast feeds, in seconds.


.. _defconf:

Default Configuration
=====================

For reference, this is the default configuration shipped with
Mopidy-Podcast release |release|:

.. literalinclude:: ../mopidy_podcast/ext.conf
   :language: ini


.. rubric:: Footnotes

.. [#footnote1] When running Mopidy as a regular user, this will
   usually be ``~/.config/mopidy/podcast``.  When running as a system
   service, this should be ``/etc/mopidy/podcast``.  Note that it may
   be necessary to create these directories manually when installing
   the Python package from PyPi_, depending on local file permissions.


.. _PyPI: https://pypi.python.org/pypi/Mopidy-Podcast/
