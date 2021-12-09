"""The package that supplies type aliases for linear algebra and transformations."""

from nptyping import NDArray, Float

__all__ = ['MatrixType', 'MatrixParseTuple']

MatrixType = NDArray[(2, 2), Float]
MatrixParseTuple = tuple[list[list[tuple[str, str, str]]], str]
