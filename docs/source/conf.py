"""A minimal Sphinx config. Sphinx must be called in an environment with lintrans installed."""

from __future__ import annotations

# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import lintrans

# -- Project information -----------------------------------------------------

project = 'lintrans'
author = 'D. Dyson (DoctorDalek1963)'
copyright = f'2021 - 2022, {author}'

# The full version, including alpha/beta/rc tags
release = lintrans.__version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones
extensions: list[str] = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx'
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
html_static_path: list[str] = ['_static']

# For RTD theme
html_show_sourcelink = False

html_favicon = 'favicon.png'

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
    'MatrixType': 'lintrans.typing_.MatrixType',
    'MatrixParseList': 'lintrans.typing_.MatrixParseList'
}

autodoc_class_signature = 'separated'

# -- Options for intersphinx -------------------------------------------------

intersphinx_mapping: dict[str, tuple[str, str | None]] = {
    'python': ('https://docs.python.org/3', None),
    'PyQt5': ('https://doc.qt.io/qt-5/', 'pyqt5-objects.inv')
}
