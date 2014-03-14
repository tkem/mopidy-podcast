Mopidy-Podcast
========================================================================

Mopidy-Podcast is a Mopidy_ extension for searching and streaming
podcasts.


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
basically you have to specify a list of podcast ``directories`` you want
to use for searching and browsing.

The default ``feeds`` directory is included with the distribution, and
provided a list of feed URLs for your favorite podcasts, will show up
under *Subscribed Feeds* - or whatever you set ``feeds_label`` to -
when browsing::

    [podcast]
    enabled = true

    # list of podcast directories for searching and browsing
    directories = feeds

    # top-level directory name for browsing
    browse_label = Podcasts

    # maximum number of search results
    search_limit = 50

    # maximum number of episodes to show for each podcast
    max_episodes = 100

    # sort order: "asc" (oldest first) or "desc" (newest first)
    sort_order = desc

    # directory update interval in seconds
    update_interval = 86400

    # number of podcasts to cache
    cache_size = 128

    # cache time-to-live in seconds; should be less than "update_interval"
    cache_ttl = 3600

    # optional http request timeout in seconds
    timeout =

    # links to podcast RSS feeds; examples from npr.org
    feeds =
        http://www.npr.org/rss/podcast.php?id=510019
        http://www.npr.org/rss/podcast.php?id=510253
        http://www.npr.org/rss/podcast.php?id=510306

    # feeds directory name for browsing
    feeds_label = Subscribed Feeds

Additional podcast directories are available as extensions:

- Mopidy-Podcast-iTunes_
- Mopidy-Podcast-gpodder.net_

Configured podcast directories will be updated and checked for new
episodes every "update_interval" seconds.


Project Resources
------------------------------------------------------------------------

- `Source Code`_
- `Issue Tracker`_
- `Change Log`_
- `Development Snapshot`_

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
.. _Mopidy-Podcast-iTunes: https://github.com/tkem/mopidy-podcast-itunes
.. _Mopidy-Podcast-gpodder.net: https://github.com/tkem/mopidy-podcast-gpodder
.. _Source Code: https://github.com/tkem/mopidy-podcast
.. _Issue Tracker: https://github.com/tkem/mopidy-podcast/issues/
.. _Change Log: https://github.com/tkem/mopidy-podcast/blob/master/Changes
.. _Development Snapshot: https://github.com/tkem/mopidy-podcast/tarball/master#egg=Mopidy-Podcast-dev
.. _Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0
