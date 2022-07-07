# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This package supplies type aliases for linear algebra and transformations.

.. note::
   This package is called ``typing_`` and not ``typing`` to avoid name collisions with the
   builtin :mod:`typing`. I don't quite know how this collision occurs, but renaming
   this module fixed the problem.
"""

from __future__ import annotations

from sys import version_info

from numpy import ndarray
from nptyping import NDArray, Float

from typing import Any

if version_info >= (3, 10):
    from typing import TypeGuard

__all__ = ['is_matrix_type', 'MatrixType', 'MatrixParseList', 'VectorType']

MatrixType = NDArray[(2, 2), Float]
"""This type represents a 2x2 matrix as a NumPy array."""

VectorType = NDArray[(2,), Float]
"""This type represents a 2D vector as a NumPy array, for use with :attr:`MatrixType`."""

MatrixParseList = list[list[tuple[str, str, str]]]
"""This is a list containing lists of tuples. Each tuple represents a matrix and is ``(multiplier,
matrix_identifier, index)`` where all of them are strings. These matrix-representing tuples are
contained in lists which represent multiplication groups. Every matrix in the group should be
multiplied together, in order. These multiplication group lists are contained by a top level list,
which is this type. Once these multiplication group lists have been evaluated, they should be summed.

In the tuples, the multiplier is a string representing a real number, the matrix identifier
is a capital letter or ``rot(x)`` where x is a real number angle, and the index is a string
representing an integer, or it's the letter ``T`` for transpose.
"""


def is_matrix_type(matrix: Any) -> TypeGuard[NDArray[(2, 2), Float]]:
    """Check if the given value is a valid matrix type.

    .. note::
       This function is a TypeGuard, meaning if it returns True, then the
       passed value must be a :attr:`lintrans.typing_.MatrixType`.
    """
    return isinstance(matrix, ndarray) and matrix.shape == (2, 2)
