Mopidy-Podcast
========================================================================

Mopidy-Podcast is a Mopidy_ extension for searching and browsing
podcasts.

Mopidy-Podcast extends Mopidy's browsing and searching capabilities to
the podcasting domain by integrating podcasts and their episodes with
Mopidy's native `data model`_.  More specifically, podcasts are mapped
to *albums*, while individual podcast episodes are shown as *tracks*
in Mopidy.  Podcast and episode metadata is retained and converted to
Mopidy's native types where applicable.  An episode's audio stream is
then played using Mopidy's streaming_ extension.

To use Mopidy-Podcast, you first have to configure how to find and
access podcasts:

- If you already have some favorite podcasts published as RSS feeds,
  you can subscribe to them by adding their feed URLs to
  :confval:`podcast/feeds`.  RSS feeds will get updated on a regular
  basis, so you can always browse and search for the latest episodes.

- You can also install one of several -- well, actually two, at the
  time -- :ref:`extensions`, which let you access external podcast
  directory services such as the `Apple iTunes Store`_.

Note that both methods can be combined, i.e. you can configure a list
of your favorite RSS feeds for regular -- and potentially faster --
access, while also installing one or more extensions for exploring.

.. toctree::
   :maxdepth: 2

   install
   config
   extensions
   api/index
   license

.. _Mopidy: http://www.mopidy.com/
.. _data model: http://docs.mopidy.com/en/latest/api/models/
.. _streaming: http://docs.mopidy.com/en/latest/ext/stream/
.. _Apple iTunes Store: https://itunes.apple.com/genre/podcasts/id26
