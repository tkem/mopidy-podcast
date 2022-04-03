v3.0.1 (2022-04-03)
===================

- Officially support Python 3.9 and 3.10.


v3.0.0 (2019-12-25)
===================

- Depend on final release of Mopidy 3.0.0.


v3.0.0a1 (2019-12-06)
=====================

- Require Python >= 3.7.

- Require Mopidy >= 3.0.0a5.

- Require Pykka >= 2.0.1.

- Update project setup.


v2.0.3 (2018-07-23)
===================

- Skip empty ``<itunes:author>`` tags.


v2.0.2 (2018-01-10)
===================

- Skip cache for local feeds.

- Accept uppercase ``URL`` attributes in OPML feeds.


v2.0.1 (2016-08-10)
===================

- Add OPML example to docs.

- Remove PyPI downloads badge from README.

- Correct tests under extreme timezones (thanks to Chris Lamb).


v2.0.0 (2016-03-23)
===================

- Add support for OPML subscription lists and directories.

- Add configuration options for browse and lookup order.

- Change URI scheme for podcast episodes to use GUID as fragment
  identifier.

- Drop ``feeds`` directory.

- Drop directory API.

- Drop search support.

- Upgrade dependencies to Mopidy v1.1.1.


v1.1.2 (2015-08-27)
===================

- Pass ``episodes`` as ``list`` to ``Podcast.copy()``.


v1.1.1 (2015-03-25)
===================

- Prepare for Mopidy v1.0 exact search API.


v1.1.0 (2014-11-22)
===================

- Improve ``podcast`` URI scheme.

- Report podcasts as albums when browsing.

- Update dependencies.

- Update unit tests.


v1.0.0 (2014-05-24)
===================

- Move RSS parsing to ``FeedsDirectory``.

- Support for additional podcast/episode properties.

- Add ``search_results`` config value.

- Add ``uri_schemes`` property to ``PodcastDirectory``.

- Add ``uri`` property to ``Podcast`` and ``Episode``.

- Support for ``<itunes:image>``.

- Convert ``Podcast.Image`` and ``Episode.Enclosure`` to Mopidy model
  types.


v0.4.0 (2014-04-11)
===================

- ``PodcastDirectory`` and models API changes.

- Performance and stability improvements.

- Configuration cleanup.


v0.3.0 (2014-03-14)
===================

- Complete rewrite to integrate podcast directory extensions.


v0.2.0 (2014-02-07)
===================

- Improve handling of iTunes tags.

- Improve performance by removing feedparser.

- Support searching for podcasts and episodes.


v0.1.0 (2014-02-01)
===================

- Initial release.
