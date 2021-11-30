"""The lintrans.typing module, used for type aliases."""

from nptyping import NDArray, Float

__all__ = ['MatrixType']

MatrixType = NDArray[(2, 2), Float]
