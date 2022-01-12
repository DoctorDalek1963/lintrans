"""This package provides separate dialogs for the main GUI.

These dialogs are mainly for defining new matrices in different ways.
"""

from .define_new_matrix import DefineAsAnExpressionDialog, DefineAsARotationDialog, DefineDialog, \
    DefineNumericallyDialog

__all__ = ['DefineAsAnExpressionDialog', 'DefineAsARotationDialog', 'DefineDialog', 'DefineNumericallyDialog']
