# Copilot Instructions for Mopidy-Podcast

Project conventions (stack, commands, code style, architecture constraints, boundaries
and git workflow) live in [`AGENTS.md`](../AGENTS.md). This file adds only the code
review process.

## Code Review

- Reviews **amend `.github/copilot-review.md` in place** (header: date, commit, CI
  status, coverage); never new files, dated sections, a per-commit change summary or
  a list of what was verified (git history is the record).
- Findings are tables ordered High, Medium, Low, Info with columns
  `# | Priority | Location | Finding`; renumber after changes; cross-reference as
  "Code #3". **Resolved issues are removed**, never marked resolved.
- Name the reviewed commit by hash and subject plus its base branch; after a rebase
  replace stale hashes instead of narrating history. List only interpreter versions
  actually run.
- Keep it brief: under 100 lines, one or two sentences per row, numbers only where
  they decide something, current snapshot only (no comparisons with earlier releases).
  Drop "no issues" sections and Info rows that only restate accepted design. Record
  settled matters under *Maintainer Decisions*. A review changes nothing; fix only
  when asked.
- `CHANGELOG.rst` is reviewed, never edited: entries are imperative one-liners with
  ``double backticks`` and no issue numbers, tagged "(breaking change)", "(potentially
  breaking change)" or "(broken since vX.Y.Z)". Every `Fix #123` commit and every
  user-visible behavior change needs an entry; docs-only, test-only and build work
  is one "Minor/Various ... improvements." or "Update build environment." line each;
  two blank lines between releases.
- Verify before reporting: probe behavior with scripts against a real
  `PodcastBackend` and local feed files, never against live podcast servers. Check
  URIs against the scheme in `AGENTS.md`, since Mopidy-Podcast-iTunes and saved
  playlists depend on it.
- Whatever could not be verified must show up: mark the finding, figure or status as
  unverified where it stands (e.g. "not run on 3.14", "CI not run for this commit")
  and say why. Never state an unchecked claim as fact or leave it out.

## Maintainer Decisions (do not re-raise)

- Library and playback providers log errors and return empty results instead of
  raising (`BLE001` is ignored for this reason); clients must not see exceptions.
  This is settled, so the code no longer carries `TODO`/`FIXME` comments about it.
- Local (`file:`) feeds are never cached, so edits show up without `refresh()`.
- The code carries no type annotations; pyright runs in `standard` mode and is not
  part of the default `tox` envlist until its errors are fixed.
- CI runs inside `ghcr.io/mopidy/ci`, since Mopidy depends on PyGObject; free-threaded
  and PyPy builds are not tested.
