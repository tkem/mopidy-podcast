Mopidy-Podcast
========================================================================

Mopidy-Podcast is a Mopidy_ extension for searching and browsing
podcasts.

This extension lets you browse and search for podcasts using plugable
podcast *directory providers*.  By default, it comes with a single
directory provider, the *feeds* directory, which lets you configure a
list of your favorite podcast RSS feeds.  Feeds will get updated on a
regular basis, depending on the setting of
:confval:`podcast/update_interval`, so you can always browse and
search for the latest episodes.

Other podcast directory providers are available as external extensions
to Mopidy-Podcast.  See the :ref:`extensions <ext>` section for
details.

.. toctree::
   :maxdepth: 2

   install
   config
   ext/index
   api/index
   license

.. _Mopidy: http://www.mopidy.com/
