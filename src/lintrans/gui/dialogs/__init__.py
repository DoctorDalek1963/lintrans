# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This package provides separate dialogs for the main GUI.

These dialogs are for defining new matrices in different ways and editing settings.
"""

from .define_new_matrix import (DefineAsExpressionDialog, DefineMatrixDialog,
                                DefineNumericallyDialog, DefineVisuallyDialog)
from .misc import AboutDialog, FileSelectDialog, InfoPanelDialog
from .settings import DisplaySettingsDialog

__all__ = ['AboutDialog', 'DefineAsExpressionDialog', 'DefineMatrixDialog', 'DefineNumericallyDialog',
           'DefineVisuallyDialog', 'DisplaySettingsDialog', 'FileSelectDialog', 'InfoPanelDialog']
