# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This package provides separate dialogs for the main GUI.

These dialogs are for defining new matrices in different ways and editing settings.
"""

from .define_new_matrix import DefineAsAnExpressionDialog, DefineDialog, DefineNumericallyDialog, DefineVisuallyDialog
from .settings import DisplaySettingsDialog

__all__ = ['DefineAsAnExpressionDialog', 'DefineDialog', 'DefineNumericallyDialog',
           'DefineVisuallyDialog', 'DisplaySettingsDialog']
