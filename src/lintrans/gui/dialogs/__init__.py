"""This package provides separate dialogs for the main GUI.

These dialogs are for defining new matrices in different ways and editing settings.
"""

from .define_new_matrix import DefineAsAnExpressionDialog, DefineDialog, DefineNumericallyDialog, DefineVisuallyDialog
from .settings import DisplaySettingsDialog

__all__ = ['DefineAsAnExpressionDialog', 'DefineDialog', 'DefineNumericallyDialog',
           'DefineVisuallyDialog', 'DisplaySettingsDialog']
