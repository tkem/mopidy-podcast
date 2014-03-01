Mopidy-Podcast
========================================================================

Mopidy-Podcast is a Mopidy_ extension for searching and streaming
Podcasts.


Installation
------------------------------------------------------------------------

Like other Mopidy extensions, Mopidy-Podcast can be installed using
pip by running::

    pip install Mopidy-Podcast

You can also download and install Debian/Ubuntu packages for
Mopidy-Podcast releases_.


Configuration
------------------------------------------------------------------------

Configuration items are still subject to change at this point, but
basically you have to provide a list of feed URLs for your favorite
Podcasts, which will then show up under "Podcasts" -- or whatever you
set "browse_label" to -- when browsing::

  [podcast]
  enabled = true

  # links to podcast RSS feeds; examples from npr.org
  feed_urls =
      http://www.npr.org/rss/podcast.php?id=510019
      http://www.npr.org/rss/podcast.php?id=510253
      http://www.npr.org/rss/podcast.php?id=510306

  # top-level name for browsing
  browse_label = Podcasts

  # podcast update interval in seconds
  update_interval = 86400

  # sort order: "asc" (oldest first) or "desc" (newest first)
  sort_order = desc

Configured Podcasts will be updated and checked for new episodes every
"update_interval" seconds.


Project Resources
------------------------------------------------------------------------

- `Source Code`_
- `Issue Tracker`_
- `Change Log`_

.. image:: https://pypip.in/v/Mopidy-Podcast/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-Podcast/
    :alt: Latest PyPI version

.. image:: https://pypip.in/d/Mopidy-Podcast/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-Podcast/
    :alt: Number of PyPI downloads


License
------------------------------------------------------------------------

Mopidy-Podcast is Copyright 2014 Thomas Kemmer.

Licensed under the `Apache License, Version 2.0`_.


.. _Mopidy: http://www.mopidy.com/
.. _releases: https://github.com/tkem/mopidy-podcast/releases
.. _Source Code: https://github.com/tkem/mopidy-podcast
.. _Issue Tracker: https://github.com/tkem/mopidy-podcast/issues/
.. _Change Log: https://github.com/tkem/mopidy-podcast/blob/master/Changes
.. _Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
