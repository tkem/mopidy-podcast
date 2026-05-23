# Extract the current version from the source.
import pathlib
import sys

src_directory = (pathlib.Path(__file__).parent.parent / "src").resolve()
sys.path.insert(0, str(src_directory))


def get_version(package):
    """Get the version and release from the source code."""
    text = (src_directory / "mopidy_podcast/__init__.py").read_text()
    for line in text.splitlines():
        if not line.strip().startswith("__version__"):
            continue
        return line.partition("=")[2].strip().strip("\"'")


project = "Mopidy-Podcast"
copyright = "2014-2026 Thomas Kemmer"
release = get_version(project)
version = ".".join(release.split(".")[:2])

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
]
exclude_patterns = ["_build"]
master_doc = "index"
html_theme = "classic"
