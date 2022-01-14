"""The package that supplies type aliases for linear algebra and transformations."""

from __future__ import annotations

from typing import Any, TypeGuard

from numpy import ndarray
from nptyping import NDArray, Float

__all__ = ['MatrixType', 'is_matrix_type', 'MatrixParseList']

#: The type that represents a 2x2 matrix as a NumPy array
MatrixType = NDArray[(2, 2), Float]

#: The type of the list that :func:`lintrans.matrices.parse.parse_matrix_expression` returns
MatrixParseList = list[list[tuple[str, str, str]]]


def is_matrix_type(matrix: Any) -> TypeGuard[NDArray[(2, 2), Float]]:
    """Check if the given value is a valid matrix type.

    .. note:: This function is a TypeGuard, meaning if it returns True, then the passed value must be a MatrixType.
    """
    return isinstance(matrix, ndarray) and matrix.shape == (2, 2)
