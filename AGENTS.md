# Mopidy-Podcast

Mopidy backend extension for browsing and playing podcasts from RSS feeds and OPML
directories. Pure Python ≥ 3.13, `src/` layout, no annotations; depends on Mopidy ≥ 4,
Pykka, `cachetools` and `uritools`. Mopidy-Podcast-iTunes builds on its URI scheme.
Single maintainer; `master` is the release branch and `develop` the integration
branch that PRs and Dependabot target. Code reviews follow
`.github/copilot-instructions.md`.

## Commands

Run everything through `tox`, never bare `pytest`, `ruff` or `pyright`:

```bash
tox -p auto                                  # default environments, as CI does
tox -e py -- tests/test_rss.py -k tracks     # tests; posargs go to pytest
tox -e ruff,ruff-format,docs                 # lint, format, docs
tox -e pyright                               # not in envlist yet: still fails
```

Installing Mopidy builds PyGObject, which needs the GObject introspection and cairo
headers (`libgirepository-2.0-dev`, `libcairo2-dev`, `pkg-config` on Debian/Ubuntu).
CI (GitHub Actions on `tkem/mopidy-podcast`, every push) runs CPython 3.13 and 3.14
inside the `ghcr.io/mopidy/ci` container; without `gh`, check runs via
`https://api.github.com/repos/tkem/mopidy-podcast/actions/runs?branch=<branch>`.
Coverage is reported to Codecov and is not complete; see `.github/copilot-review.md`.

## Code Style

- `ruff check` and `ruff format` with the default rules; `[tool.ruff.lint]` in
  `pyproject.toml` ignores `BLE001` (errors are logged, not raised, on purpose),
  `RUF012` (Mopidy's class attributes) and `S110`. Do not add `noqa` comments.
- No type annotations in `src/`; keep the code compatible with pyright's
  `standard` mode where it is cheap to do so.
- Private state uses double-underscore names (`self.__items`); keep feed and provider
  internals private and expose behavior through the Mopidy provider API only.
- Log with `logger.error("... %s", arg)`, never f-strings, and never raise from
  `browse()`, `lookup()`, `get_images()` or `translate_uri()`: Mopidy clients expect
  an empty result instead.
- Docs (`docs/index.rst`): wrap prose at column 70, two spaces after a sentence,
  `confval` entries for every setting in `ext.conf`. Keep `README.rst` in sync.

## Architecture Constraints

- URIs are `podcast+<feed URL>` for feeds and `podcast+<feed URL>#<guid>` for
  episodes, where the guid falls back to the enclosure URL. Mopidy-Podcast-iTunes
  creates the same URIs; changing the scheme or the guid encoding breaks it and
  every saved playlist.
- `PodcastFeedCache` is a `cachetools.TTLCache` whose `__missing__` downloads and
  parses a feed; `file:` feeds are returned but not stored so local edits show up
  immediately. It is shared with the provider actors via `pykka_traversable`.
- `feeds.parse()` dispatches on the XML root tag (`rss` or `opml`); RSS items without
  an `<enclosure url=...>` are skipped, episodes are sorted by `pubDate`.
- `PodcastLibraryProvider.lookup()` keeps the tracks of the last looked-up feed so
  adding a whole feed to the tracklist does not re-parse it per episode; entries are
  popped on use and dropped by `refresh()`.
- Configuration keys live in `ext.conf` and `Extension.get_config_schema()`; both
  must change together, as must the test `config` fixture.

## Testing

- New behavior needs tests under `tests/`; user-visible changes need docs in
  `docs/index.rst`. Feeds are parsed from inline XML (`test_rss.py`, `test_opml.py`)
  or from `tests/*.xml`; tests never touch the network.
- Provider tests build a real `PodcastBackend` from the `config` fixture with a mock
  `audio`; assert results against what `feeds.parse()` returns for the same file.

## Boundaries

- Never edit `CHANGELOG.rst` or bump `__version__`; both are release-only.
- Never change the URI scheme or configuration keys without a deprecation path.
- Do not re-raise the *Maintainer Decisions* in `.github/copilot-instructions.md`.

## Git

- PRs target `develop` and reference an open issue (except trivial fixes), in
  separate commits:
  `Fix #123: ...`, `Tests for #123: ...`, `Docs for #123: ...`.
- Run `tox -p auto` before pushing. Update this file in the same PR that changes a
  convention, and keep it under 100 lines.
