:tocdepth: 3

**************
Mopidy-Podcast
**************

Mopidy-Podcast is a Mopidy_ extension for browsing and playing
podcasts.

This extension lets you browse podcasts distributed as RSS feeds and
play individual episodes in a variety of audio formats.  Podcasts are
mapped to albums, while podcast episodes are shown as tracks in
Mopidy, with metadata converted to Mopidy’s native data model where
applicable.  OPML 2.0 subscription lists and directories are also
supported for multi-level browsing.

To use this extension, you first need a way to access podcasts from
Mopidy:

- If you are already using a podcasting client, chances are that it
  supports exporting your subscribed feeds as an OPML file.  Simply
  store this file in the location pointed to by
  :confval:`podcast/browse_root` to access your favorite podcasts from
  Mopidy.

- Since OPML is a simple XML format, it is also feasible to create
  your own, using an XML or text editor of your choice. OPML also
  supports linking to other OPML files, both locally and on the Web,
  so this even allows creating your own *meta directory* pointing to
  podcast collections from the `BBC
  <https://www.bbc.co.uk/podcasts.opml>`_, `gpodder.net
  <https://gpodder.net/search.opml?q=Python>`_, and other sources::

    <?xml version="1.0" encoding="UTF-8"?>
    <opml>
      <body>
        <outline text="TED Radio Hour" type="rss" xmlUrl="https://www.npr.org/rss/podcast.php?id=510298" />
        <outline text="BBC Radio Podcasts" type="include" url="https://www.bbc.co.uk/podcasts.opml" />
        <outline text="gpodder.net - Python" type="include" url="https://gpodder.net/search.opml?q=Python" />
      </body>
    </opml>

- If your client supports entering Mopidy URIs for playback and
  browsing directly, just prefix the feed URL with ``podcast+`` to
  make sure it is not treated as an audio stream::

    mpc add "podcast+https://www.npr.org/rss/podcast.php?id=510298"

- Last but not least, you can install the companion extension
  `Mopidy-Podcast-iTunes`_, to browse and search podcasts on on `Apple
  Podcasts`_.
  

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

      browse_root = https://www.bbc.co.uk/podcasts.opml

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

.. literalinclude:: ../src/mopidy_podcast/ext.conf
   :language: ini


.. rubric:: Footnotes

.. [#footnote1] When running Mopidy as a regular user, this will
   usually be ``~/.config/mopidy/podcast``.  When running as a system
   service, this should be ``/etc/mopidy/podcast``.  Note that it may
   be necessary to create these directories manually when installing
   the Python package from PyPi_, depending on local file permissions.

.. _PyPI: https://pypi.org/project/Mopidy-Podcast/

.. _Mopidy: https://www.mopidy.com/
.. _OPML 2.0 specification: http://dev.opml.org/spec2.html
.. _Mopidy-Podcast-iTunes: https://github.com/tkem/mopidy-podcast-itunes/
.. _Apple Podcasts: https://podcasts.apple.com/
