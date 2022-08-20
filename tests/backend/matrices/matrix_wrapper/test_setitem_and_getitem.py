# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""Test the MatrixWrapper __setitem__() and __getitem__() methods."""

from typing import Any, Dict, List

import numpy as np
import pytest
from numpy import linalg as la

from lintrans.matrices import MatrixWrapper
from lintrans.typing_ import MatrixType

valid_matrix_names = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'
invalid_matrix_names = ['bad name', '123456', 'Th15 Is an 1nV@l1D n@m3', 'abc', 'a']

test_matrix: MatrixType = np.array([[1, 2], [4, 3]])


def test_basic_get_matrix(new_wrapper: MatrixWrapper) -> None:
    """Test MatrixWrapper().__getitem__()."""
    for name in valid_matrix_names:
        assert new_wrapper[name] is None

    assert (new_wrapper['I'] == np.array([[1, 0], [0, 1]])).all()


def test_get_name_error(new_wrapper: MatrixWrapper) -> None:
    """Test that MatrixWrapper().__getitem__() raises a NameError if called with an invalid name."""
    for name in invalid_matrix_names:
        with pytest.raises(NameError):
            _ = new_wrapper[name]


def test_basic_set_matrix(new_wrapper: MatrixWrapper) -> None:
    """Test MatrixWrapper().__setitem__()."""
    for name in valid_matrix_names:
        new_wrapper[name] = test_matrix
        assert (new_wrapper[name] == test_matrix).all()

        new_wrapper[name] = None
        assert new_wrapper[name] is None


def test_set_expression(test_wrapper: MatrixWrapper) -> None:
    """Test that MatrixWrapper.__setitem__() can accept a valid expression."""
    test_wrapper['N'] = 'A^2'
    test_wrapper['O'] = 'BA+2C'
    test_wrapper['P'] = 'E^T'
    test_wrapper['Q'] = 'C^-1B'
    test_wrapper['R'] = 'A^{2}3B'
    test_wrapper['S'] = 'N^-1'
    test_wrapper['T'] = 'PQP^-1'

    with pytest.raises(TypeError):
        test_wrapper['U'] = 'A+1'

    with pytest.raises(TypeError):
        test_wrapper['V'] = 'K'

    with pytest.raises(TypeError):
        test_wrapper['W'] = 'L^2'

    with pytest.raises(TypeError):
        test_wrapper['X'] = 'M^-1'

    with pytest.raises(TypeError):
        test_wrapper['Y'] = 'A^2B+C^'


def test_simple_dynamic_evaluation(test_wrapper: MatrixWrapper) -> None:
    """Test that expression-defined matrices are evaluated dynamically."""
    test_wrapper['N'] = 'A^2'
    test_wrapper['O'] = '4B'
    test_wrapper['P'] = 'A+C'

    assert (test_wrapper['N'] == test_wrapper.evaluate_expression('A^2')).all()
    assert (test_wrapper['O'] == test_wrapper.evaluate_expression('4B')).all()
    assert (test_wrapper['P'] == test_wrapper.evaluate_expression('A+C')).all()

    assert (test_wrapper.evaluate_expression('N^2 + 3O') ==
            la.matrix_power(test_wrapper.evaluate_expression('A^2'), 2) +
            3 * test_wrapper.evaluate_expression('4B')
            ).all()
    assert (test_wrapper.evaluate_expression('P^-1 - 3NO^2') ==
            la.inv(test_wrapper.evaluate_expression('A+C')) -
            (3 * test_wrapper.evaluate_expression('A^2')) @
            la.matrix_power(test_wrapper.evaluate_expression('4B'), 2)
            ).all()

    test_wrapper['A'] = np.array([
        [19, -21.5],
        [84, 96.572]
    ])
    test_wrapper['B'] = np.array([
        [-0.993, 2.52],
        [1e10, 0]
    ])
    test_wrapper['C'] = np.array([
        [0, 19512],
        [1.414, 19]
    ])

    assert (test_wrapper['N'] == test_wrapper.evaluate_expression('A^2')).all()
    assert (test_wrapper['O'] == test_wrapper.evaluate_expression('4B')).all()
    assert (test_wrapper['P'] == test_wrapper.evaluate_expression('A+C')).all()

    assert (test_wrapper.evaluate_expression('N^2 + 3O') ==
            la.matrix_power(test_wrapper.evaluate_expression('A^2'), 2) +
            3 * test_wrapper.evaluate_expression('4B')
            ).all()
    assert (test_wrapper.evaluate_expression('P^-1 - 3NO^2') ==
            la.inv(test_wrapper.evaluate_expression('A+C')) -
            (3 * test_wrapper.evaluate_expression('A^2')) @
            la.matrix_power(test_wrapper.evaluate_expression('4B'), 2)
            ).all()


def test_recursive_dynamic_evaluation(test_wrapper: MatrixWrapper) -> None:
    """Test that dynamic evaluation works recursively."""
    test_wrapper['N'] = 'A^2'
    test_wrapper['O'] = '4B'
    test_wrapper['P'] = 'A+C'

    test_wrapper['Q'] = 'N^-1'
    test_wrapper['R'] = 'P-4O'
    test_wrapper['S'] = 'NOP'

    assert test_wrapper['Q'] == pytest.approx(test_wrapper.evaluate_expression('A^-2'))
    assert test_wrapper['R'] == pytest.approx(test_wrapper.evaluate_expression('A + C - 16B'))
    assert test_wrapper['S'] == pytest.approx(test_wrapper.evaluate_expression('A^{2}4BA + A^{2}4BC'))


def test_self_referential_expressions(test_wrapper: MatrixWrapper) -> None:
    """Test that self-referential expressions raise an error."""
    expressions: Dict[str, str] = {
        'A': 'A^2',
        'B': 'A(C^-1A^T)+rot(45)B',
        'C': '2Brot(1482.536)(A^-1D^{2}4CE)^3F'
    }

    for name, expression in expressions.items():
        with pytest.raises(ValueError):
            test_wrapper[name] = expression

    test_wrapper['B'] = '3A^2'
    test_wrapper['C'] = 'ABBA'
    with pytest.raises(ValueError):
        test_wrapper['A'] = 'C^-1'

    test_wrapper['E'] = 'rot(45)B^-1+C^T'
    test_wrapper['F'] = 'EBDBIC'
    test_wrapper['D'] = 'E'
    with pytest.raises(ValueError):
        test_wrapper['D'] = 'F'


def test_get_matrix_dependencies(test_wrapper: MatrixWrapper) -> None:
    """Test MatrixWrapper's get_matrix_dependencies() and get_expression_dependencies() methods."""
    test_wrapper['N'] = 'A^2'
    test_wrapper['O'] = '4B'
    test_wrapper['P'] = 'A+C'
    test_wrapper['Q'] = 'N^-1'
    test_wrapper['R'] = 'P-4O'
    test_wrapper['S'] = 'NOP'

    assert test_wrapper.get_matrix_dependencies('A') == set()
    assert test_wrapper.get_matrix_dependencies('B') == set()
    assert test_wrapper.get_matrix_dependencies('C') == set()
    assert test_wrapper.get_matrix_dependencies('D') == set()
    assert test_wrapper.get_matrix_dependencies('E') == set()
    assert test_wrapper.get_matrix_dependencies('F') == set()
    assert test_wrapper.get_matrix_dependencies('G') == set()

    assert test_wrapper.get_matrix_dependencies('N') == {'A'}
    assert test_wrapper.get_matrix_dependencies('O') == {'B'}
    assert test_wrapper.get_matrix_dependencies('P') == {'A', 'C'}
    assert test_wrapper.get_matrix_dependencies('Q') == {'A', 'N'}
    assert test_wrapper.get_matrix_dependencies('R') == {'A', 'B', 'C', 'O', 'P'}
    assert test_wrapper.get_matrix_dependencies('S') == {'A', 'B', 'C', 'N', 'O', 'P'}

    assert test_wrapper.get_expression_dependencies('ABC') == set()
    assert test_wrapper.get_expression_dependencies('NOB') == {'A', 'B'}
    assert test_wrapper.get_expression_dependencies('N^2O^Trot(90)B^-1') == {'A', 'B'}
    assert test_wrapper.get_expression_dependencies('NOP') == {'A', 'B', 'C'}
    assert test_wrapper.get_expression_dependencies('NOPQ') == {'A', 'B', 'C', 'N'}
    assert test_wrapper.get_expression_dependencies('NOPQR') == {'A', 'B', 'C', 'N', 'O', 'P'}
    assert test_wrapper.get_expression_dependencies('NOPQRS') == {'A', 'B', 'C', 'N', 'O', 'P'}


def test_set_identity_error(new_wrapper: MatrixWrapper) -> None:
    """Test that MatrixWrapper().__setitem__() raises a NameError when trying to assign to the identity matrix."""
    with pytest.raises(NameError):
        new_wrapper['I'] = test_matrix


def test_set_name_error(new_wrapper: MatrixWrapper) -> None:
    """Test that MatrixWrapper().__setitem__() raises a NameError when trying to assign to an invalid name."""
    for name in invalid_matrix_names:
        with pytest.raises(NameError):
            new_wrapper[name] = test_matrix


def test_set_type_error(new_wrapper: MatrixWrapper) -> None:
    """Test that MatrixWrapper().__setitem__() raises a TypeError when trying to set a non-matrix."""
    invalid_values: List[Any] = [
                                 12,
                                 [1, 2, 3, 4, 5],
                                 [[1, 2], [3, 4]],
                                 True,
                                 24.3222,
                                 'This is totally a matrix, I swear',
                                 MatrixWrapper,
                                 MatrixWrapper(),
                                 np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
                                 np.eye(100)
                                 ]

    for value in invalid_values:
        with pytest.raises(TypeError):
            new_wrapper['M'] = value
