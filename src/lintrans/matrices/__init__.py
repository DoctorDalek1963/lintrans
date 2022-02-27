# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This package supplies classes and functions to parse, evaluate, and wrap matrices."""

from . import parse
from .wrapper import create_rotation_matrix, MatrixWrapper

__all__ = ['create_rotation_matrix', 'MatrixWrapper', 'parse']
