"""Test the MatrixWrapper __setitem__() and __getitem__() methods."""

import numpy as np
import pytest

from lintrans.matrices import MatrixWrapper
from lintrans.typing import MatrixType

valid_matrix_names = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'
test_matrix: MatrixType = np.array([[1, 2], [4, 3]])


def test_basic_get_matrix(new_wrapper) -> None:
    """Test MatrixWrapper().__getitem__()."""
    for name in valid_matrix_names:
        assert new_wrapper[name] is None

    assert (new_wrapper['I'] == np.array([[1, 0], [0, 1]])).all()


def test_get_name_error(new_wrapper) -> None:
    """Test that MatrixWrapper().__getitem__() raises a NameError if called with an invalid name."""
    with pytest.raises(NameError):
        _ = new_wrapper['bad name']
        _ = new_wrapper['123456']
        _ = new_wrapper['Th15 Is an 1nV@l1D n@m3']
        _ = new_wrapper['abc']
        _ = new_wrapper['a']


def test_basic_set_matrix(new_wrapper) -> None:
    """Test MatrixWrapper().__setitem__()."""
    for name in valid_matrix_names:
        new_wrapper[name] = test_matrix
        assert (new_wrapper[name] == test_matrix).all()

        new_wrapper[name] = None
        assert new_wrapper[name] is None


def test_set_identity_error(new_wrapper) -> None:
    """Test that MatrixWrapper().__setitem__() raises a NameError when trying to assign to I."""
    with pytest.raises(NameError):
        new_wrapper['I'] = test_matrix


def test_set_name_error(new_wrapper) -> None:
    """Test that MatrixWrapper().__setitem__() raises a NameError when trying to assign to an invalid name."""
    with pytest.raises(NameError):
        new_wrapper['bad name'] = test_matrix
        new_wrapper['123456'] = test_matrix
        new_wrapper['Th15 Is an 1nV@l1D n@m3'] = test_matrix
        new_wrapper['abc'] = test_matrix
        new_wrapper['a'] = test_matrix


def test_set_type_error(new_wrapper) -> None:
    """Test that MatrixWrapper().__setitem__() raises a TypeError when trying to set a non-matrix."""
    with pytest.raises(TypeError):
        new_wrapper['M'] = 12
        new_wrapper['M'] = [1, 2, 3, 4, 5]
        new_wrapper['M'] = [[1, 2], [3, 4]]
        new_wrapper['M'] = True
        new_wrapper['M'] = 24.3222
        new_wrapper['M'] = 'This is totally a matrix, I swear'
        new_wrapper['M'] = MatrixWrapper
        new_wrapper['M'] = MatrixWrapper()
        new_wrapper['M'] = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        new_wrapper['M'] = np.eye(100)
