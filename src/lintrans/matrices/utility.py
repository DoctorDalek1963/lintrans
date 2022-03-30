#  lintrans - The linear transformation visualizer
#  Copyright (C) 2022 D. Dyson (DoctorDalek1963)
#
#  This program is licensed under GNU GPLv3, available here:
#  <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides simple utility methods for matrix and vector manipulation."""

from __future__ import annotations

import numpy as np

from lintrans.typing_ import MatrixType


def create_rotation_matrix(angle: float, *, degrees: bool = True) -> MatrixType:
    """Create a matrix representing a rotation (anticlockwise) by the given angle.

    :Example:

    >>> create_rotation_matrix(30)
    array([[ 0.8660254, -0.5      ],
           [ 0.5      ,  0.8660254]])
    >>> create_rotation_matrix(45)
    array([[ 0.70710678, -0.70710678],
           [ 0.70710678,  0.70710678]])
    >>> create_rotation_matrix(np.pi / 3, degrees=False)
    array([[ 0.5      , -0.8660254],
           [ 0.8660254,  0.5      ]])

    :param float angle: The angle to rotate anticlockwise by
    :param bool degrees: Whether to interpret the angle as degrees (True) or radians (False)
    :returns MatrixType: The resultant matrix
    """
    rad = np.deg2rad(angle) if degrees else angle
    return np.array([
        [np.cos(rad), -1 * np.sin(rad)],
        [np.sin(rad), np.cos(rad)]
    ])
