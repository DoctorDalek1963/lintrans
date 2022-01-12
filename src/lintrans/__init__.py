"""This is the top-level lintrans package, which contains all the subpackages of the project.

From this ``__init__.py``, we explicitly export every subpackage.
"""

from . import gui, matrices, typing

__all__ = ['gui', 'matrices', 'typing']

__version__ = '0.0.1-alpha'
