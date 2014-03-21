Mopidy-Podcast-gpodder.net
========================================================================

Mopidy-Podcast-gpodder.net is a Mopidy-Podcast extension for searching
and browsing podcasts on `gpodder.net`_.


Installation
------------------------------------------------------------------------

First, make sure you have Mopidy-Podcast version 0.4.0 or later
installed.  Then Mopidy-Podcast-gpodder.net can be installed using pip
by running::

    pip install Mopidy-Podcast-gpodder.net

After a restart, Mopidy-Podcast will pick up the installed extension
automatically and use it for browsing and searching.

You can also download and install Debian/Ubuntu packages for
Mopidy-Podcast-gpodder.net releases_.


.. _gpodder_confvals:

Configuration Values
------------------------------------------------------------------------

.. confval:: podcast-gpodder/display_name

   A user-fiendly name to display for browsing gpodder.net.

.. confval:: podcast-gpodder/base_url

   The gpodder.net base URL.

.. confval:: podcast-gpodder/tags

   The number of top-level *tags* to display when browsing.


.. _gpodder.net: http://gpodder.net
.. _releases: https://github.com/tkem/mopidy-podcast-gpodder/releases
