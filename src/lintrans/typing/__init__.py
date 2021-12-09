"""The package that supplies type aliases for linear algebra and transformations."""

from nptyping import NDArray, Float

__all__ = ['MatrixType']

MatrixType = NDArray[(2, 2), Float]
