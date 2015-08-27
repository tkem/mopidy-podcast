1.1.2 2015-08-27
----------------

- Pass ``episodes`` as ``list`` to ``Podcast.copy()``.


1.1.1 2015-03-25
----------------

- Prepare for Mopidy v1.0 exact search API.


1.1.0 2014-11-22
----------------

- Improve `podcast` URI scheme.

- Report podcasts as albums when browsing.

- Update dependencies.

- Update unit tests.


1.0.0 2014-05-24
----------------

- Move RSS parsing to ``FeedsDirectory``.

- Support for additional podcast/episode properties.

- Add `search_results` config value.

- Add `uri_schemes` property to ``PodcastDirectory``.

- Add `uri` property to ``Podcast`` and ``Episode``.

- Support for `<itunes:image>`.

- Convert ``Podcast.Image`` and ``Episode.Enclosure`` to Mopidy model
  types.


0.4.0 2014-04-11
----------------

- ``PodcastDirectory`` and models API changes.

- Performance and stability improvements.

- Configuration cleanup.


0.3.0 2014-03-14
----------------

- Complete rewrite to integrate podcast directory extensions.


0.2.0 2014-02-07
----------------

- Improve handling of iTunes tags.

- Improve performance by removing feedparser.

- Support searching for podcasts and episodes.


0.1.0 2014-02-01
----------------

- Initial release.
