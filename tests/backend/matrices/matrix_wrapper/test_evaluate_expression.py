# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""Test the MatrixWrapper evaluate_expression() method."""

import numpy as np
import pytest
from conftest import get_test_wrapper
from numpy import linalg as la
from pytest import approx

from lintrans.matrices import MatrixWrapper, create_rotation_matrix
from lintrans.typing_ import MatrixType


def test_simple_matrix_addition(test_wrapper: MatrixWrapper) -> None:
    """Test simple addition and subtraction of two matrices."""
    # NOTE: We assert that all of these values are not None just to stop mypy complaining
    # These values will never actually be None because they're set in the wrapper() fixture
    # There's probably a better way  do this, because this method is a bit of a bodge, but this works for now
    assert test_wrapper['A'] is not None and test_wrapper['B'] is not None and test_wrapper['C'] is not None and \
           test_wrapper['D'] is not None and test_wrapper['E'] is not None and test_wrapper['F'] is not None and \
           test_wrapper['G'] is not None

    assert (test_wrapper.evaluate_expression('A+B') == test_wrapper['A'] + test_wrapper['B']).all()
    assert (test_wrapper.evaluate_expression('E+F') == test_wrapper['E'] + test_wrapper['F']).all()
    assert (test_wrapper.evaluate_expression('G+D') == test_wrapper['G'] + test_wrapper['D']).all()
    assert (test_wrapper.evaluate_expression('C+C') == test_wrapper['C'] + test_wrapper['C']).all()
    assert (test_wrapper.evaluate_expression('D+A') == test_wrapper['D'] + test_wrapper['A']).all()
    assert (test_wrapper.evaluate_expression('B+C') == test_wrapper['B'] + test_wrapper['C']).all()

    assert test_wrapper == get_test_wrapper()


def test_simple_two_matrix_multiplication(test_wrapper: MatrixWrapper) -> None:
    """Test simple multiplication of two matrices."""
    assert test_wrapper['A'] is not None and test_wrapper['B'] is not None and test_wrapper['C'] is not None and \
           test_wrapper['D'] is not None and test_wrapper['E'] is not None and test_wrapper['F'] is not None and \
           test_wrapper['G'] is not None

    assert (test_wrapper.evaluate_expression('AB') == test_wrapper['A'] @ test_wrapper['B']).all()
    assert (test_wrapper.evaluate_expression('BA') == test_wrapper['B'] @ test_wrapper['A']).all()
    assert (test_wrapper.evaluate_expression('AC') == test_wrapper['A'] @ test_wrapper['C']).all()
    assert (test_wrapper.evaluate_expression('DA') == test_wrapper['D'] @ test_wrapper['A']).all()
    assert (test_wrapper.evaluate_expression('ED') == test_wrapper['E'] @ test_wrapper['D']).all()
    assert (test_wrapper.evaluate_expression('FD') == test_wrapper['F'] @ test_wrapper['D']).all()
    assert (test_wrapper.evaluate_expression('GA') == test_wrapper['G'] @ test_wrapper['A']).all()
    assert (test_wrapper.evaluate_expression('CF') == test_wrapper['C'] @ test_wrapper['F']).all()
    assert (test_wrapper.evaluate_expression('AG') == test_wrapper['A'] @ test_wrapper['G']).all()

    assert test_wrapper.evaluate_expression('A2B') == approx(test_wrapper['A'] @ (2 * test_wrapper['B']))
    assert test_wrapper.evaluate_expression('2AB') == approx((2 * test_wrapper['A']) @ test_wrapper['B'])
    assert test_wrapper.evaluate_expression('C3D') == approx(test_wrapper['C'] @ (3 * test_wrapper['D']))
    assert test_wrapper.evaluate_expression('4.2E1.2A') == approx((4.2 * test_wrapper['E']) @ (1.2 * test_wrapper['A']))

    assert test_wrapper == get_test_wrapper()


def test_identity_multiplication(test_wrapper: MatrixWrapper) -> None:
    """Test that multiplying by the identity doesn't change the value of a matrix."""
    assert test_wrapper['A'] is not None and test_wrapper['B'] is not None and test_wrapper['C'] is not None and \
           test_wrapper['D'] is not None and test_wrapper['E'] is not None and test_wrapper['F'] is not None and \
           test_wrapper['G'] is not None

    assert (test_wrapper.evaluate_expression('I') == test_wrapper['I']).all()
    assert (test_wrapper.evaluate_expression('AI') == test_wrapper['A']).all()
    assert (test_wrapper.evaluate_expression('IA') == test_wrapper['A']).all()
    assert (test_wrapper.evaluate_expression('GI') == test_wrapper['G']).all()
    assert (test_wrapper.evaluate_expression('IG') == test_wrapper['G']).all()

    assert (test_wrapper.evaluate_expression('EID') == test_wrapper['E'] @ test_wrapper['D']).all()
    assert (test_wrapper.evaluate_expression('IED') == test_wrapper['E'] @ test_wrapper['D']).all()
    assert (test_wrapper.evaluate_expression('EDI') == test_wrapper['E'] @ test_wrapper['D']).all()
    assert (test_wrapper.evaluate_expression('IEIDI') == test_wrapper['E'] @ test_wrapper['D']).all()
    assert (test_wrapper.evaluate_expression('EI^3D') == test_wrapper['E'] @ test_wrapper['D']).all()

    assert test_wrapper == get_test_wrapper()


def test_simple_three_matrix_multiplication(test_wrapper: MatrixWrapper) -> None:
    """Test simple multiplication of two matrices."""
    assert test_wrapper['A'] is not None and test_wrapper['B'] is not None and test_wrapper['C'] is not None and \
           test_wrapper['D'] is not None and test_wrapper['E'] is not None and test_wrapper['F'] is not None and \
           test_wrapper['G'] is not None

    assert (test_wrapper.evaluate_expression('ABC') == test_wrapper['A'] @ test_wrapper['B'] @ test_wrapper['C']).all()
    assert (test_wrapper.evaluate_expression('ACB') == test_wrapper['A'] @ test_wrapper['C'] @ test_wrapper['B']).all()
    assert (test_wrapper.evaluate_expression('BAC') == test_wrapper['B'] @ test_wrapper['A'] @ test_wrapper['C']).all()
    assert (test_wrapper.evaluate_expression('EFG') == test_wrapper['E'] @ test_wrapper['F'] @ test_wrapper['G']).all()
    assert (test_wrapper.evaluate_expression('DAC') == test_wrapper['D'] @ test_wrapper['A'] @ test_wrapper['C']).all()
    assert (test_wrapper.evaluate_expression('GAE') == test_wrapper['G'] @ test_wrapper['A'] @ test_wrapper['E']).all()
    assert (test_wrapper.evaluate_expression('FAG') == test_wrapper['F'] @ test_wrapper['A'] @ test_wrapper['G']).all()
    assert (test_wrapper.evaluate_expression('GAF') == test_wrapper['G'] @ test_wrapper['A'] @ test_wrapper['F']).all()

    assert test_wrapper == get_test_wrapper()


def test_matrix_inverses(test_wrapper: MatrixWrapper) -> None:
    """Test the inverses of single matrices."""
    assert test_wrapper['A'] is not None and test_wrapper['B'] is not None and test_wrapper['C'] is not None and \
           test_wrapper['D'] is not None and test_wrapper['E'] is not None and test_wrapper['F'] is not None and \
           test_wrapper['G'] is not None

    assert (test_wrapper.evaluate_expression('A^{-1}') == la.inv(test_wrapper['A'])).all()
    assert (test_wrapper.evaluate_expression('B^{-1}') == la.inv(test_wrapper['B'])).all()
    assert (test_wrapper.evaluate_expression('C^{-1}') == la.inv(test_wrapper['C'])).all()
    assert (test_wrapper.evaluate_expression('D^{-1}') == la.inv(test_wrapper['D'])).all()
    assert (test_wrapper.evaluate_expression('E^{-1}') == la.inv(test_wrapper['E'])).all()
    assert (test_wrapper.evaluate_expression('F^{-1}') == la.inv(test_wrapper['F'])).all()
    assert (test_wrapper.evaluate_expression('G^{-1}') == la.inv(test_wrapper['G'])).all()

    assert (test_wrapper.evaluate_expression('A^-1') == la.inv(test_wrapper['A'])).all()
    assert (test_wrapper.evaluate_expression('B^-1') == la.inv(test_wrapper['B'])).all()
    assert (test_wrapper.evaluate_expression('C^-1') == la.inv(test_wrapper['C'])).all()
    assert (test_wrapper.evaluate_expression('D^-1') == la.inv(test_wrapper['D'])).all()
    assert (test_wrapper.evaluate_expression('E^-1') == la.inv(test_wrapper['E'])).all()
    assert (test_wrapper.evaluate_expression('F^-1') == la.inv(test_wrapper['F'])).all()
    assert (test_wrapper.evaluate_expression('G^-1') == la.inv(test_wrapper['G'])).all()

    assert test_wrapper == get_test_wrapper()


def test_matrix_powers(test_wrapper: MatrixWrapper) -> None:
    """Test that matrices can be raised to integer powers."""
    assert test_wrapper['A'] is not None and test_wrapper['B'] is not None and test_wrapper['C'] is not None and \
           test_wrapper['D'] is not None and test_wrapper['E'] is not None and test_wrapper['F'] is not None and \
           test_wrapper['G'] is not None

    assert (test_wrapper.evaluate_expression('A^2') == la.matrix_power(test_wrapper['A'], 2)).all()
    assert (test_wrapper.evaluate_expression('B^4') == la.matrix_power(test_wrapper['B'], 4)).all()
    assert (test_wrapper.evaluate_expression('C^{12}') == la.matrix_power(test_wrapper['C'], 12)).all()
    assert (test_wrapper.evaluate_expression('D^12') == la.matrix_power(test_wrapper['D'], 12)).all()
    assert (test_wrapper.evaluate_expression('E^8') == la.matrix_power(test_wrapper['E'], 8)).all()
    assert (test_wrapper.evaluate_expression('F^{-6}') == la.matrix_power(test_wrapper['F'], -6)).all()
    assert (test_wrapper.evaluate_expression('G^-2') == la.matrix_power(test_wrapper['G'], -2)).all()

    assert test_wrapper == get_test_wrapper()


def test_matrix_transpose(test_wrapper: MatrixWrapper) -> None:
    """Test matrix transpositions."""
    assert test_wrapper['A'] is not None and test_wrapper['B'] is not None and test_wrapper['C'] is not None and \
           test_wrapper['D'] is not None and test_wrapper['E'] is not None and test_wrapper['F'] is not None and \
           test_wrapper['G'] is not None

    assert (test_wrapper.evaluate_expression('A^{T}') == test_wrapper['A'].T).all()
    assert (test_wrapper.evaluate_expression('B^{T}') == test_wrapper['B'].T).all()
    assert (test_wrapper.evaluate_expression('C^{T}') == test_wrapper['C'].T).all()
    assert (test_wrapper.evaluate_expression('D^{T}') == test_wrapper['D'].T).all()
    assert (test_wrapper.evaluate_expression('E^{T}') == test_wrapper['E'].T).all()
    assert (test_wrapper.evaluate_expression('F^{T}') == test_wrapper['F'].T).all()
    assert (test_wrapper.evaluate_expression('G^{T}') == test_wrapper['G'].T).all()

    assert (test_wrapper.evaluate_expression('A^T') == test_wrapper['A'].T).all()
    assert (test_wrapper.evaluate_expression('B^T') == test_wrapper['B'].T).all()
    assert (test_wrapper.evaluate_expression('C^T') == test_wrapper['C'].T).all()
    assert (test_wrapper.evaluate_expression('D^T') == test_wrapper['D'].T).all()
    assert (test_wrapper.evaluate_expression('E^T') == test_wrapper['E'].T).all()
    assert (test_wrapper.evaluate_expression('F^T') == test_wrapper['F'].T).all()
    assert (test_wrapper.evaluate_expression('G^T') == test_wrapper['G'].T).all()

    assert test_wrapper == get_test_wrapper()


def test_rotation_matrices(test_wrapper: MatrixWrapper) -> None:
    """Test that 'rot(angle)' can be used in an expression."""
    assert (test_wrapper.evaluate_expression('rot(90)') == create_rotation_matrix(90)).all()
    assert (test_wrapper.evaluate_expression('rot(180)') == create_rotation_matrix(180)).all()
    assert (test_wrapper.evaluate_expression('rot(270)') == create_rotation_matrix(270)).all()
    assert (test_wrapper.evaluate_expression('rot(360)') == create_rotation_matrix(360)).all()
    assert (test_wrapper.evaluate_expression('rot(45)') == create_rotation_matrix(45)).all()
    assert (test_wrapper.evaluate_expression('rot(30)') == create_rotation_matrix(30)).all()

    assert (test_wrapper.evaluate_expression('rot(13.43)') == create_rotation_matrix(13.43)).all()
    assert (test_wrapper.evaluate_expression('rot(49.4)') == create_rotation_matrix(49.4)).all()
    assert (test_wrapper.evaluate_expression('rot(-123.456)') == create_rotation_matrix(-123.456)).all()
    assert (test_wrapper.evaluate_expression('rot(963.245)') == create_rotation_matrix(963.245)).all()
    assert (test_wrapper.evaluate_expression('rot(-235.24)') == create_rotation_matrix(-235.24)).all()

    assert test_wrapper == get_test_wrapper()


def test_multiplication_and_addition(test_wrapper: MatrixWrapper) -> None:
    """Test multiplication and addition of matrices together."""
    assert test_wrapper['A'] is not None and test_wrapper['B'] is not None and test_wrapper['C'] is not None and \
           test_wrapper['D'] is not None and test_wrapper['E'] is not None and test_wrapper['F'] is not None and \
           test_wrapper['G'] is not None

    assert (test_wrapper.evaluate_expression('AB+C') ==
            test_wrapper['A'] @ test_wrapper['B'] + test_wrapper['C']).all()
    assert (test_wrapper.evaluate_expression('DE-D') ==
            test_wrapper['D'] @ test_wrapper['E'] - test_wrapper['D']).all()
    assert (test_wrapper.evaluate_expression('FD+AB') ==
            test_wrapper['F'] @ test_wrapper['D'] + test_wrapper['A'] @ test_wrapper['B']).all()
    assert (test_wrapper.evaluate_expression('BA-DE') ==
            test_wrapper['B'] @ test_wrapper['A'] - test_wrapper['D'] @ test_wrapper['E']).all()

    assert (test_wrapper.evaluate_expression('2AB+3C') ==
            (2 * test_wrapper['A']) @ test_wrapper['B'] + (3 * test_wrapper['C'])).all()
    assert (test_wrapper.evaluate_expression('4D7.9E-1.2A') ==
            (4 * test_wrapper['D']) @ (7.9 * test_wrapper['E']) - (1.2 * test_wrapper['A'])).all()

    assert test_wrapper == get_test_wrapper()


def test_complicated_expressions(test_wrapper: MatrixWrapper) -> None:
    """Test evaluation of complicated expressions."""
    assert test_wrapper['A'] is not None and test_wrapper['B'] is not None and test_wrapper['C'] is not None and \
           test_wrapper['D'] is not None and test_wrapper['E'] is not None and test_wrapper['F'] is not None and \
           test_wrapper['G'] is not None

    assert (test_wrapper.evaluate_expression('-3.2A^T 4B^{-1} 6C^{-1} + 8.1D^{2} 3.2E^4') ==
            (-3.2 * test_wrapper['A'].T) @ (4 * la.inv(test_wrapper['B'])) @ (6 * la.inv(test_wrapper['C']))
            + (8.1 * la.matrix_power(test_wrapper['D'], 2)) @ (3.2 * la.matrix_power(test_wrapper['E'], 4))).all()

    assert (test_wrapper.evaluate_expression('53.6D^{2} 3B^T - 4.9F^{2} 2D + A^3 B^-1') ==
            (53.6 * la.matrix_power(test_wrapper['D'], 2)) @ (3 * test_wrapper['B'].T)
            - (4.9 * la.matrix_power(test_wrapper['F'], 2)) @ (2 * test_wrapper['D'])
            + la.matrix_power(test_wrapper['A'], 3) @ la.inv(test_wrapper['B'])).all()

    assert test_wrapper == get_test_wrapper()


def test_parenthesized_expressions(test_wrapper: MatrixWrapper) -> None:
    """Test evaluation of parenthesized expressions."""
    assert test_wrapper['A'] is not None and test_wrapper['B'] is not None and test_wrapper['C'] is not None and \
           test_wrapper['D'] is not None and test_wrapper['E'] is not None and test_wrapper['F'] is not None and \
           test_wrapper['G'] is not None

    assert (test_wrapper.evaluate_expression('(A^T)^2') == la.matrix_power(test_wrapper['A'].T, 2)).all()
    assert (test_wrapper.evaluate_expression('(B^T)^3') == la.matrix_power(test_wrapper['B'].T, 3)).all()
    assert (test_wrapper.evaluate_expression('(C^T)^4') == la.matrix_power(test_wrapper['C'].T, 4)).all()
    assert (test_wrapper.evaluate_expression('(D^T)^5') == la.matrix_power(test_wrapper['D'].T, 5)).all()
    assert (test_wrapper.evaluate_expression('(E^T)^6') == la.matrix_power(test_wrapper['E'].T, 6)).all()
    assert (test_wrapper.evaluate_expression('(F^T)^7') == la.matrix_power(test_wrapper['F'].T, 7)).all()
    assert (test_wrapper.evaluate_expression('(G^T)^8') == la.matrix_power(test_wrapper['G'].T, 8)).all()

    assert (test_wrapper.evaluate_expression('(rot(45)^1)^T') == create_rotation_matrix(45).T).all()
    assert (test_wrapper.evaluate_expression('(rot(45)^2)^T') == la.matrix_power(create_rotation_matrix(45), 2).T).all()
    assert (test_wrapper.evaluate_expression('(rot(45)^3)^T') == la.matrix_power(create_rotation_matrix(45), 3).T).all()
    assert (test_wrapper.evaluate_expression('(rot(45)^4)^T') == la.matrix_power(create_rotation_matrix(45), 4).T).all()
    assert (test_wrapper.evaluate_expression('(rot(45)^5)^T') == la.matrix_power(create_rotation_matrix(45), 5).T).all()

    assert (test_wrapper.evaluate_expression('D^3(A+6.2F-0.397G^TE)^-2+A') ==
            la.matrix_power(test_wrapper['D'], 3) @ la.matrix_power(
                test_wrapper['A'] + 6.2 * test_wrapper['F'] - 0.397 * test_wrapper['G'].T @ test_wrapper['E'],
                -2
            ) + test_wrapper['A']).all()

    assert (test_wrapper.evaluate_expression('-1.2F^{3}4.9D^T(A^2(B+3E^TF)^-1)^2') ==
            -1.2 * la.matrix_power(test_wrapper['F'], 3) @ (4.9 * test_wrapper['D'].T) @
            la.matrix_power(
                la.matrix_power(test_wrapper['A'], 2) @ la.matrix_power(
                    test_wrapper['B'] + 3 * test_wrapper['E'].T @ test_wrapper['F'],
                    -1
                ),
                2
            )).all()


def test_anonymous_matrices(test_wrapper: MatrixWrapper) -> None:
    """Test that anonymous matrices get evaluated correctly."""
    assert test_wrapper['A'] is not None and test_wrapper['B'] is not None and test_wrapper['C'] is not None and \
           test_wrapper['D'] is not None and test_wrapper['E'] is not None and test_wrapper['F'] is not None and \
           test_wrapper['G'] is not None

    assert (test_wrapper.evaluate_expression('[1 2; -3 -1]') == np.array([[1, 2], [-3, -1]])).all()
    assert (test_wrapper.evaluate_expression('[1 2; -3 -1][-5 6; 8.3 2]') ==
            np.array([[1, 2], [-3, -1]]) @ np.array([[-5, 6], [8.3, 2]])).all()
    assert (test_wrapper.evaluate_expression('[1 2; -3 -1]^-1') == la.inv(np.array([[1, 2], [-3, -1]]))).all()
    assert (test_wrapper.evaluate_expression('3A[1 2; -3 -1]^{2}-15[-5 6; 8.3 2]^TB') ==
            3 * test_wrapper['A'] @ la.matrix_power(np.array([[1, 2], [-3, -1]]), 2)
            - 15 * np.array([[-5, 8.3], [6, 2]]) @ test_wrapper['B']).all()


def test_value_errors(test_wrapper: MatrixWrapper) -> None:
    """Test that evaluate_expression() raises a ValueError for any malformed input."""
    invalid_expressions = ['', '+', '-', 'This is not a valid expression', '3+4',
                           'A+2', 'A^', '^2', 'A^-', 'At', 'A^t', '3^2']

    for expression in invalid_expressions:
        with pytest.raises(ValueError):
            test_wrapper.evaluate_expression(expression)


def test_linalgerror() -> None:
    """Test that certain expressions raise np.linalg.LinAlgError."""
    matrix_a: MatrixType = np.array([
        [0, 0],
        [0, 0]
    ])

    matrix_b: MatrixType = np.array([
        [1, 2],
        [1, 2]
    ])

    wrapper = MatrixWrapper()
    wrapper['A'] = matrix_a
    wrapper['B'] = matrix_b

    assert (wrapper.evaluate_expression('A') == matrix_a).all()
    assert (wrapper.evaluate_expression('B') == matrix_b).all()

    with pytest.raises(np.linalg.LinAlgError):
        wrapper.evaluate_expression('A^-1')

    with pytest.raises(np.linalg.LinAlgError):
        wrapper.evaluate_expression('B^-1')

    assert (wrapper['A'] == matrix_a).all()
    assert (wrapper['B'] == matrix_b).all()
