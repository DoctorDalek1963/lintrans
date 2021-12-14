"""The package that supplies type aliases for linear algebra and transformations."""

from nptyping import NDArray, Float

__all__ = ['MatrixType', 'MatrixParseList']

MatrixType = NDArray[(2, 2), Float]
MatrixParseList = list[list[tuple[str, str, str]]]
