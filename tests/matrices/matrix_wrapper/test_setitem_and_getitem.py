"""Test the MatrixWrapper __setitem__() and __getitem__() methods."""

import numpy as np
import pytest
from lintrans.matrices import MatrixWrapper

valid_matrix_names = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'
test_matrix = np.array([[1, 2], [4, 3]])


@pytest.fixture
def wrapper() -> MatrixWrapper:
    """Return a new MatrixWrapper object."""
    return MatrixWrapper()


def test_get_matrix(wrapper: MatrixWrapper) -> None:
    """Test MatrixWrapper().__getitem__()."""
    for name in valid_matrix_names:
        assert wrapper[name] is None

    assert (wrapper['I'] == np.array([[1, 0], [0, 1]])).all()


def test_get_name_error(wrapper: MatrixWrapper) -> None:
    """Test that MatrixWrapper().__getitem__() raises a NameError if called with an invalid name."""
    with pytest.raises(NameError):
        _ = wrapper['bad name']
        _ = wrapper['123456']
        _ = wrapper['Th15 Is an 1nV@l1D n@m3']
        _ = wrapper['abc']
        _ = wrapper['a']


def test_set_matrix(wrapper: MatrixWrapper) -> None:
    """Test MatrixWrapper().__setitem__()."""
    for name in valid_matrix_names:
        wrapper[name] = test_matrix
        assert (wrapper[name] == test_matrix).all()

        wrapper[name] = None
        assert wrapper[name] is None


def test_set_identity_error(wrapper: MatrixWrapper) -> None:
    """Test that MatrixWrapper().__setitem__() raises a NameError when trying to assign to I."""
    with pytest.raises(NameError):
        wrapper['I'] = test_matrix


def test_set_name_error(wrapper: MatrixWrapper) -> None:
    """Test that MatrixWrapper().__setitem__() raises a NameError when trying to assign to an invalid name."""
    with pytest.raises(NameError):
        wrapper['bad name'] = test_matrix
        wrapper['123456'] = test_matrix
        wrapper['Th15 Is an 1nV@l1D n@m3'] = test_matrix
        wrapper['abc'] = test_matrix
        wrapper['a'] = test_matrix


def test_set_type_error(wrapper: MatrixWrapper) -> None:
    """Test that MatrixWrapper().__setitem__() raises a TypeError when trying to set a non-matrix."""
    with pytest.raises(TypeError):
        wrapper['M'] = 'M'
        wrapper['M'] = 12
        wrapper['M'] = [1, 2, 3, 4, 5]
        wrapper['M'] = [[1, 2], [3, 4]]
        wrapper['M'] = True
        wrapper['M'] = 24.3222
        wrapper['M'] = 'This is totally a matrix, I swear'
        wrapper['M'] = MatrixWrapper
        wrapper['M'] = MatrixWrapper()
