Mopidy-Podcast Directory
========================================================================

.. module:: mopidy_podcast.directory

.. autoclass:: PodcastDirectory
   :members:

.. todo
   :members: name, display_name, PODCAST_TITLE, EPISODE_TITLE, AUTHOR,
             CATEGORY, DESCRIPTION

   :param config: Config dictionary

   .. automethod:: get(self, uri)

      :param string uri: relative URI reference or podcast feed URL
      :rtype: :class:`~mopidy_podcast.models.Podcast`

   .. automethod:: browse(self, uri, limit=None)

      `uri` may be :const:`None` to retrieve the directory's root
      listing, a relative URI reference starting with :const:`/`
      representing some collection within the directory, or an
      absolute podcast feed URL for browsing the podcast's episode.

      The default implementation will call :func:`self.get()` for the
      given `uri`, and return a list of
      :class:`~mopidy_podcast.models.Ref`'s for the result's episodes.

      :param string uri: relative URI reference or podcast feed URL
      :param int limit: maximum number of results to return
      :return: list of episode, podcast and directory :class:`~mopidy_podcast.models.Ref`

   .. automethod:: search(self, terms=None, attribute=None, limit=None)

      `terms` is a list of search strings, and `attribute` is one of
      the search attribute constants defined in
      :class:`PodcastDirectory`, or :const:`None` to match *any*
      attribute.  If multiple `terms` are provides, *all* terms must
      match a given podcast or episode.  If `terms` is empty, the
      result is implementation-defined.

      The default implementation will return an empty list.

      :param list of strings uri: search terms
      :param string attribute: search attribute
      :param int limit: maximum number of results to return
      :return: list of podcast and episode :class:`~mopidy_podcast.models.Ref`'s

   .. automethod:: update(self)

      All cached data must be cleared and reloaded if necessary.
