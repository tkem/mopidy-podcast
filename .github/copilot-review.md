# Code Review — Mopidy-Podcast 4.0.0

**Date:** 2026-11-09
**Reviewed:** `develop` at `94b77b8` ("Fix lookup() returning None for an unknown
episode guid."), i.e. v4.0.0 plus the build environment update and the lookup and
test fixture fixes.

**CI status:** All default `tox` environments pass locally on CPython 3.13.18 (`py`:
31 passed) with Mopidy 4.0.5, cachetools 8.0.0, uritools 7.0.0 and Pykka 4.5.0;
not run on 3.14 locally. GitHub Actions passed on 3.13 and 3.14 for the merged PRs;
its run for this commit had not finished when this review was written. `tox -e
pyright` fails with 48 errors (Code #4). **Coverage:** 88 % with branches; gaps in
`library.py` (80 %: config dir errors, `root_directory` fallbacks) and `feeds.py`.

## Code — Potential Issues

| # | Priority | Location | Finding |
|---|----------|----------|---------|
| 1 | Low | `feeds.py` `parse` | An unrecognized root tag raises `TypeError(("Not a recognized podcast feed: %s", url))`: the message is passed as two arguments and never formatted, so the logged error reads as a tuple. |
| 2 | Low | `feeds.py` `RssFeed.__init__` | An `<rss>` document without `<channel>` fails with `AttributeError: 'NoneType' object has no attribute 'findall'`; the providers log it, but the message does not say what is wrong. |
| 3 | Low | `backend.py` `PodcastFeedCache.__missing__` | URI validation relies on `assert ext_name == Extension.ext_name`, which `python -O` strips. A non-`podcast+` key then tries to open the part after the first `+` (or the empty string). |
| 4 | Low | whole package, `tests/` | pyright `standard` reports 48 errors: Mopidy 4's typed models (`Uri`, `ReleaseDate`, `DurationMs`, `frozenset` artists, `tuple` results) reject plain `str`, `int` and `list` arguments, `self.backend.feeds` is unknown on `backend.Backend`, and the `root_directory` property overrides a class attribute. Blocks adding `pyright` to the envlist. |
| 5 | Info | `library.py` `get_images` | `get_images(None)` raises `TypeError` instead of returning `{}`, unlike the other provider methods (asserted by `test_get_images_error`). |

## Tests — Gaps

| # | Priority | Finding |
|---|----------|---------|
| 1 | Low | `PodcastFeedCache.__missing__` is only exercised with `file:` URIs; the path that stores remote feeds (line 34) and the TTL/size limits from the config are untested, as is the HTTP opener's timeout. |
| 2 | Low | `root_directory` is tested only for a relative `browse_root`; absolute paths, URLs, an empty setting and an unavailable config directory (`get_config_dir` errors) are not. |
| 3 | Info | `itunes:duration` values with hours or only seconds, missing or malformed `pubDate`, and items without `<guid>` but with an enclosure are covered only partly by `tests/rssfeed.xml`. |
| 4 | Info | Two `DeprecationWarning`s ("Use ReleaseDate instead") come from `mopidy.types` at import time, not from this package. |

## Docs (`docs/index.rst`)

| # | Priority | Finding |
|---|----------|---------|
| 1 | Info | `README.rst` still shows a "code style: black" badge, although formatting is done with `ruff format`. |

## Changelog

| # | Priority | Finding |
|---|----------|---------|
| 1 | Medium | The next release's entry needs "Fix ``lookup()`` returning ``None`` for an unknown episode guid.", plus "Update build environment." for the ruff, `tox` and CI changes and one "Minor test improvements." line for the `conftest.py` fix. |
