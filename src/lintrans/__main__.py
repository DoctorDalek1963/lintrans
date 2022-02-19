#!/usr/bin/env python

# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module very simply runs the app by calling :func:`lintrans.gui.main_window.main`.

This allows the user to run the app like ``python -m lintrans`` from the command line.
"""

import sys

from lintrans.gui import main_window

if __name__ == '__main__':
    main_window.main(sys.argv)
