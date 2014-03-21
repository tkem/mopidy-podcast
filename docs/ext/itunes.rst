Mopidy-Podcast-iTunes
========================================================================

Mopidy-Podcast-iTunes is a Mopidy-Podcast extension for searching and
browsing podcasts on the `iTunes Store`_.


Installation
------------------------------------------------------------------------

First, make sure you have Mopidy-Podcast version 0.4.0 or later
installed.  Then Mopidy-Podcast-iTunes can be installed using pip by
running::

    pip install Mopidy-Podcast-iTunes

After a restart, Mopidy-Podcast will pick up the installed extension
automatically and use it for browsing and searching.

You can also download and install Debian/Ubuntu packages for
Mopidy-Podcast-iTunes releases_.


.. _itunes_confvals:

Configuration Values
------------------------------------------------------------------------

.. confval:: podcast-itunes/display_name

   A user-fiendly name to display for browsing the iTunes Store.

.. confval:: podcast-itunes/base_url

   The iTunes Store base URL to use.

.. confval:: podcast-itunes/country

   The ISO two-letter country code for the iTunes Store to use,

.. confval:: podcast-itunes/explicit

   Whether you explicit content should be included in search results;
   possible values are `Yes`, `No`, or default (blank).

.. confval:: podcast-itunes/charts

   The iTunes charts to display when browsing. Possible
   values are `Podcasts`, `AudioPodcasts` and `VideoPodcasts`

.. confval:: podcast-itunes/charts_label

   The directory name to display for browsing charts of a
   genre/category with subgenres.  "{0}" is replaced with the genre
   name, "{1}" with # the iTunes genre ID.

.. confval:: podcast-itunes/root_genre_id

   The iTunes root genre ID for browsing.


.. _iTunes Store: https://itunes.apple.com/genre/podcasts/id26
.. _releases: https://github.com/tkem/mopidy-podcast-itunes/releases
