from __future__ import annotations

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
sys.path.insert(0, os.path.abspath('../../src/lintrans'))

import lintrans


# -- Project information -----------------------------------------------------

project = 'lintrans'
author = 'D. Dyson (DoctorDalek1963)'
copyright = f'2021 - 2022, {author}'

# The full version, including alpha/beta/rc tags
release = lintrans.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# For RTD theme
html_show_sourcelink = False

html_favicon = 'favicon.png'


# -- Options for autodoc -----------------------------------------------------

autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'undoc-members': True,
    'private-members': False,
    'special-members': True,
    'inherited-members': False,
    'show-inheritance': True,
    'ignore-module-all': False,
    'exclude-members': '__module__, __weakref__, __dict__, __annotations__'
}

autodoc_type_aliases = {
    'MatrixType': 'lintrans.typing_.MatrixType',
    'MatrixParseList': 'lintrans.typing_.MatrixParseList'
}

autodoc_class_signature = 'separated'

# -- Options for intersphinx -------------------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'PyQt5': ('https://doc.qt.io/qt-5/', 'pyqt5-objects.inv')
}
