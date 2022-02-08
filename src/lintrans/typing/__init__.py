"""The package that supplies type aliases for linear algebra and transformations."""

from __future__ import annotations

from typing import Any, TypeGuard

from numpy import ndarray
from nptyping import NDArray, Float

__all__ = ['is_matrix_type', 'MatrixType', 'MatrixParseList']

MatrixType = NDArray[(2, 2), Float]
"""This type represents a 2x2 matrix as a NumPy array."""

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
       passed value must be a :attr:`lintrans.typing.MatrixType`.
    """
    return isinstance(matrix, ndarray) and matrix.shape == (2, 2)
