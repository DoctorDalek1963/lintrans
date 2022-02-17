# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This package provides widgets for the visualization plot in the main window and the visual definition dialog."""

from . import classes
from .widgets import DefineVisuallyWidget, VisualizeTransformationWidget

__all__ = ['classes', 'DefineVisuallyWidget', 'VisualizeTransformationWidget']
