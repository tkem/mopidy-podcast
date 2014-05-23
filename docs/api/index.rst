Mopidy-Podcast API reference
========================================================================

Mopidy-Podcast extensions that wish to provide alternate podcast
directory services need to subclass
:class:`mopidy_podcast.directory.PodcastDirectory` and install and
configure it with a Mopidy extension.  Directory subclasses need to be
added to Mopidy's registry with key :const:`podcast:directory`, e.g.::

  class MyPodcastExtension(ext.Extension):
      def setup(self, registry):
          registry.add('podcast:directory', MyPodcastDirectory)

.. toctree::
   models
   directory
