"""A minimal Sphinx config. Sphinx must be called in an environment with lintrans installed."""

from __future__ import annotations

import inspect
import os
from importlib import import_module
from typing import Dict, List, Optional

from sphinx.application import Sphinx

import lintrans

# -- Project information -----------------------------------------------------

project = 'lintrans'
author = 'D. Dyson (DoctorDalek1963)'
copyright = f'2021 - 2022, {author}'

release = lintrans.__version__
version = lintrans.__version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones
extensions: list[str] = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.linkcode',
    'sphinxcontrib.email'
]

# Add any paths that contain templates here, relative to this directory
templates_path: list[str] = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files
# This pattern also affects html_static_path and html_extra_path
exclude_patterns: list[str] = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes

html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css"
# html_static_path: list[str] = ['_static']

# For RTD theme
html_show_sourcelink = False

html_favicon = '_images/favicon.png'

# -- Options for autodoc -----------------------------------------------------

autodoc_default_options: dict[str, bool | str] = {
    'members': True,
    'member-order': 'alphabetical',
    'undoc-members': True,
    'private-members': True,
    'special-members': True,
    'inherited-members': False,
    'show-inheritance': True,
    'ignore-module-all': False,
    'exclude-members': '__module__, __weakref__, __dict__, __annotations__, '
                       '__dataclass_fields__, __dataclass_params__, __match_args__'
}

autodoc_type_aliases: dict[str, str] = {
    'MatrixType': '~lintrans.typing_.MatrixType',
    'MatrixParseList': '~lintrans.typing_.MatrixParseList',
    'VectorType': '~lintrans.typing_.VectorType'
}

autodoc_class_signature = 'separated'

# -- Options for intersphinx -------------------------------------------------

intersphinx_mapping: dict[str, tuple[str, str | None]] = {
    'python': ('https://docs.python.org/3', None),
    'PyQt5': ('https://doc.qt.io/qt-5/', 'pyqt5-objects.inv')
}

# -- Only include the compilation tutorial if this is an RTD stable build ----

include_compilation: bool

if 'READTHEDOCS' in os.environ \
        and 'READTHEDOCS_VERSION' in os.environ \
        and os.environ['READTHEDOCS_VERSION'] != 'latest':
    exclude_patterns = []
    tags.add('include_compilation')

else:
    exclude_patterns = ['compilation/*']


# -- Functions for setup() ---------------------------------------------------


def _source_read_handler(app: Sphinx, docname: str, source: List[str]) -> None:
    if docname.startswith('compilation/'):
        source[0] = source[0].replace('VERSION_NUMBER', lintrans.__version__)

    elif 'index' in docname and not tags.has('include_compilation'):
        source[0] = source[0].replace('\n   compilation/index', '')


def setup(app: Sphinx) -> None:
    """Set up event handlers for Sphinx config."""
    app.connect('source-read', _source_read_handler)


# -- Functions for extensions ------------------------------------------------


def linkcode_resolve(domain: str, info: Dict[str, str]) -> Optional[str]:
    """Specify the GitHub link for parts of code for ``sphinx.ext.linkcode``."""
    if domain != 'py':
        return None

    # Take the module and fullname and get the class or funtion object
    module_name = info['module']
    thing = import_module(module_name)
    for part in info['fullname'].split('.'):
        thing = getattr(thing, part)

    # We can then inspect the object to find out where it's defined so we can link directly to it
    try:
        lines_list, first_line = inspect.getsourcelines(thing)
        url_filename = inspect.getsourcefile(thing).split('src')[-1]
    except (OSError, TypeError):
        return None

    last_line = first_line + len(lines_list) - 1

    # If this is a include_compilation build, then it's built with a tag
    # That means we want to link directly to that tag on GitHub
    url = 'https://github.com/DoctorDalek1963/lintrans/blob/'
    url += 'v' + lintrans.__version__ if tags.has('include_compilation') else 'main'
    url += f'/src{url_filename}#L{first_line}-L{last_line}'
    return url
