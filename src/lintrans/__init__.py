# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This is the top-level ``lintrans`` package, which contains all the subpackages of the project."""

from . import crash_reporting, global_settings, gui, matrices, typing_

__version__ = '0.3.1-alpha'

__all__ = ['crash_reporting', 'global_settings', 'gui', 'matrices', 'typing_', '__version__']
