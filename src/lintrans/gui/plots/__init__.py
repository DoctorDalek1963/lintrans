# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This package provides widgets for the visualization plot in the main window and the visual definition dialog."""

from .classes import BackgroundPlot, VectorGridPlot
from .widgets import DefinePolygonWidget, DefineVisuallyWidget, VisualizeTransformationWidget

__all__ = ['BackgroundPlot', 'DefinePolygonWidget', 'DefineVisuallyWidget',
           'VectorGridPlot', 'VisualizeTransformationWidget']
