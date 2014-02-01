****************************
Mopidy-Podcast
****************************

.. image:: https://pypip.in/v/Mopidy-Podcast/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-Podcast/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/Mopidy-Podcast/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-Podcast/
    :alt: Number of PyPI downloads

Mopidy extension for streaming Podcasts


Installation
============

Install by running::

    pip install Mopidy-Podcast

Or manually install Debian/Ubuntu packages for Mopidy-Podcast
`releases <https://github.com/tkem/mopidy-internetarchive/releases>`_.


Configuration
=============

Configuration items are still subject to change at this point, but
basically you have to provide a list of feed URLs for your Podcasts,
which will then show up under "Podcasts" -- or whatever you set
"browse_label" to -- when browsing::

  [podcast]
  enabled = true

  # links to podcast RSS feeds; examples from npr.org
  feed_urls =
      http://www.npr.org/rss/podcast.php?id=510019
      http://www.npr.org/rss/podcast.php?id=510253
      http://www.npr.org/rss/podcast.php?id=510306

  # top-level name for browsing
  browse_label = Podcasts

  # preload podcasts on startup
  preload = true


Configured Podcasts will be regularly updated for new episodes
(details TBD).



Project resources
=================

- `Source code <https://github.com/tkem/mopidy-podcast>`_
- `Issue tracker <https://github.com/tkem/mopidy-podcast/issues>`_
- `Download development snapshot <https://github.com/tkem/mopidy-podcast/tarball/master#egg=Mopidy-Podcast-dev>`_


Changelog
=========

v0.1.0 (UNRELEASED)
----------------------------------------

- Initial release.
