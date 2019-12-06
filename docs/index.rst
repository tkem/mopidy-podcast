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
  <http://www.bbc.co.uk/podcasts.opml>`_, `gpodder.net
  <http://gpodder.net/search.opml?q=Python>`_, and other sources::

    <?xml version="1.0" encoding="UTF-8"?>
    <opml>
      <body>
        <outline text="TED Radio Hour" type="rss" xmlUrl="http://www.npr.org/rss/podcast.php?id=510298" />
        <outline text="BBC Radio Podcasts" type="include" url="http://www.bbc.co.uk/podcasts.opml" />
        <outline text="gpodder.net - Python" type="include" url="http://gpodder.net/search.opml?q=Python" />
      </body>
    </opml>

- If your client supports entering Mopidy URIs for playback and
  browsing directly, just prefix the feed URL with ``podcast+`` to
  make sure it is not treated as an audio stream::

    mpc add "podcast+http://www.npr.org/rss/podcast.php?id=510298"

- Last but not least, you can install `Mopidy-Podcast-iTunes`_, a
  companion extension to Mopidy-Podcast, to browse and search podcasts
  on the `Apple iTunes Store
  <https://itunes.apple.com/genre/podcasts/id26>`_.


.. toctree::
   :hidden:

   install
   config
   changelog
   license


.. _Mopidy: http://www.mopidy.com/
.. _OPML 2.0 specification: http://dev.opml.org/spec2.html
.. _Mopidy-Podcast-iTunes: https://github.com/tkem/mopidy-podcast-itunes/
