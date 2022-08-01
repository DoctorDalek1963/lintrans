# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This package supplies the main GUI and associated dialogs for visualization."""

from . import dialogs, plots, session, settings, utility, validate
from .main_window import main

__all__ = ['dialogs', 'main', 'plots', 'session', 'settings', 'utility', 'validate']
