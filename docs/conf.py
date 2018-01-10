def setup(app):
    app.add_object_type(
        'confval', 'confval',
        objname='configuration value',
        indextemplate='pair: %s; configuration value'
    )


def get_version(filename):
    from re import findall
    with open(filename) as f:
        metadata = dict(findall(r"__([a-z]+)__ = '([^']+)'", f.read()))
    return metadata['version']


project = 'Mopidy-Podcast'
copyright = '2014-2018 Thomas Kemmer'
version = get_version(b'../mopidy_podcast/__init__.py')
release = version

exclude_patterns = ['_build']
master_doc = 'index'
html_theme = 'default'

latex_documents = [(
    'index', 'Mopidy-Podcast.tex',
    'Mopidy-Podcast Documentation',
    'Thomas Kemmer', 'manual'
)]

man_pages = [(
    'index', 'mopidy-podcast', 'Mopidy-Podcast Documentation',
    ['Thomas Kemmer'], 1
)]
