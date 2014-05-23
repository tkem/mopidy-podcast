Mopidy-Podcast Data Models
========================================================================

Mopidy-Podcast extends Mopidy's `data model`_ by providing additional
domain-specific types.  These immutable data models are used for all
data transfer between Mopidy-Podcast extensions and the Mopidy-Podcast
core module.  The intricacies of converting from/to Mopidy's native
data models are left to the Mopidy-Podcast module, so extension
developers can work solely with domain objects.

These models are based on Apple's -- rather informal -- `podcast
specification`_, which in turn is based on `RSS 2.0`_.

.. module:: mopidy_podcast.models

.. autoclass:: Podcast
   :members:

   :param uri: podcast URI
   :type uri: string
   :param title: podcast title
   :type title: string
   :param link: Web site URI
   :type link: string
   :param copyright: copyright notice
   :type copyright: string
   :param language: ISO two-letter language code
   :type language: string
   :param pubdate: publication date and time
   :type pubdate: :class:`datetime.datetime`
   :param author: author name
   :type author: string
   :param block: prevent the podcast from appearing
   :type block: boolean
   :param category: main category
   :type category: string
   :param image: podcast image
   :type image: :class:`Image`
   :param explicit: whether the podcast contains explicit material
   :type explicit: boolean
   :param complete: whether the podcast is complete
   :type complete: boolean
   :param newfeedurl: new feed location
   :type newfeedurl: string
   :param subtitle: short description
   :type subtitle: string
   :param summary: long description
   :type summary: string
   :param episodes: podcast episodes
   :type episodes: list of :class:`Episode`

.. autoclass:: Episode
   :members:

   :param uri: episode URI
   :type uri: string
   :param title: episode title
   :type title: string
   :param guid: globally unique identifier
   :type guid: string
   :param pubdate: publication date and time
   :type pubdate: :class:`datetime.datetime`
   :param author: author name
   :type author: string
   :param block: prevent the episode from appearing
   :type block: boolean
   :param image: episode image
   :type image: :class:`Image`
   :param duration: episode duration
   :type duration: :class:`datetime.timedelta`
   :param explicit: whether the podcast contains explicit material
   :type explicit: boolean
   :param order: override default ordering
   :type order: integer
   :param subtitle: short description
   :type subtitle: string
   :param summary: long description
   :type summary: string
   :param enclosure: media object
   :type summary: :class:`Enclosure`

.. autoclass:: Image
   :members:

   :param uri: image URI
   :type uri: string
   :param title: image title
   :type name: string or :const:`None`
   :param width: image width in pixels
   :type width: integer or :const:`None`
   :param height: image height in pixels
   :type height: integer or :const:`None`

.. autoclass:: Enclosure
   :members:

   :param uri: enclosure URI
   :type uri: string
   :param length: enclosure file size in bytes
   :type length: integer
   :param type: enclosure MIME type
   :type type: string

.. autoclass:: Ref
   :members:

   :param uri: object URI
   :type uri: string
   :param name: object name
   :type name: string
   :param type: object type
   :type type: string


.. _data model: http://docs.mopidy.com/en/latest/api/models/
.. _podcast specification: https://www.apple.com/itunes/podcasts/specs.html
.. _RSS 2.0: http://cyber.law.harvard.edu/rss/rss.html
