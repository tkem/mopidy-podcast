**************
Mopidy-Podcast
**************

.. image:: https://img.shields.io/pypi/v/Mopidy-Podcast
    :target: https://pypi.org/project/Mopidy-Podcast/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/github/actions/workflow/status/tkem/mopidy-podcast/ci.yml
   :target: https://github.com/tkem/mopidy-podcast/actions/workflows/ci.yml
   :alt: CI build status

.. image:: https://img.shields.io/readthedocs/mopidy-podcast
    :target: https://mopidy-podcast.readthedocs.io/
    :alt: Documentation build status

.. image:: https://img.shields.io/codecov/c/gh/tkem/mopidy-podcast
    :target: https://codecov.io/gh/tkem/mopidy-podcast
    :alt: Test coverage

.. image:: https://img.shields.io/github/license/tkem/mopidy-podcast
   :target: https://raw.github.com/tkem/mopidy-podcast/master/LICENSE
   :alt: License

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: black

Mopidy-Podcast is a Mopidy_ extension for browsing and playing
podcasts.

This extension lets you browse podcasts distributed as RSS feeds and
play individual episodes in a variety of audio formats.  Podcasts are
mapped to albums, while podcast episodes are shown as tracks in
Mopidy, with metadata converted to Mopidy’s native data model where
applicable.  OPML 2.0 subscription lists and directories are also
supported for multi-level browsing.


Installation
============

On Debian Linux and Debian-based distributions like Ubuntu or
Raspbian, install the ``mopidy-podcast`` package from
apt.mopidy.com_::

  apt-get install mopidy-podcast

Otherwise, install the Python package from PyPI_::

  pip install Mopidy-Podcast


Project Resources
=================

- `Documentation`_
- `Issue tracker`_
- `Source code`_
- `Change log`_

License
=======

Copyright (c) 2014-2026 Thomas Kemmer.

Licensed under the `Apache License, Version 2.0`_.


Credits
=======

- Original author: `Thomas Kemmer <https://github.com/tkem>`__
- Current maintainer: `Thomas Kemmer <https://github.com/tkem>`__
- `Contributors <https://github.com/tkem/mopidy-podcast/graphs/contributors>`_

.. _Mopidy: https://www.mopidy.com/

.. _PyPI: https://pypi.org/project/Mopidy-Podcast/
.. _apt.mopidy.com: https://apt.mopidy.com/

.. _Documentation: https://mopidy-podcast.readthedocs.io/en/latest/
.. _Source code: https://github.com/tkem/mopidy-podcast
.. _Issue tracker: https://github.com/tkem/mopidy-podcast/issues
.. _Change log: https://github.com/tkem/mopidy-podcast/blob/master/CHANGELOG.rst

.. _Apache License, Version 2.0: https://raw.github.com/tkem/mopidy-podcast/master/LICENSE
