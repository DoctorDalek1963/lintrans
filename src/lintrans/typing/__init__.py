"""The package that supplies type aliases for linear algebra and transformations."""

from __future__ import annotations

from nptyping import NDArray, Float

__all__ = ['MatrixType', 'MatrixParseList']

#: The type that represents a 2x2 matrix as a NumPy array
MatrixType = NDArray[(2, 2), Float]

#: The type of the list that :func:`lintrans.matrices.parse.parse_matrix_expression` returns
MatrixParseList = list[list[tuple[str, str, str]]]
