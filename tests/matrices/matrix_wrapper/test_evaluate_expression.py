"""Test the MatrixWrapper evaluate_expression() method."""

import numpy as np
from numpy import linalg as la
import pytest

from lintrans.matrices import MatrixWrapper, create_rotation_matrix


def preset_wrapper() -> MatrixWrapper:
    """Return a new MatrixWrapper object with some preset values."""
    wrapper = MatrixWrapper()

    root_two_over_two = np.sqrt(2) / 2

    wrapper['A'] = np.array([[1, 2], [3, 4]])
    wrapper['B'] = np.array([[6, 4], [12, 9]])
    wrapper['C'] = np.array([[-1, -3], [4, -12]])
    wrapper['D'] = np.array([[13.2, 9.4], [-3.4, -1.8]])
    wrapper['E'] = np.array([
        [root_two_over_two, -1 * root_two_over_two],
        [root_two_over_two, root_two_over_two]
    ])
    wrapper['F'] = np.array([[-1, 0], [0, 1]])
    wrapper['G'] = np.array([[np.pi, np.e], [1729, 743.631]])

    return wrapper


@pytest.fixture
def wrapper() -> MatrixWrapper:
    """Return a new MatrixWrapper object with some preset values."""
    return preset_wrapper()


def test_simple_matrix_addition(wrapper: MatrixWrapper) -> None:
    """Test simple addition and subtraction of two matrices."""

    # NOTE: We assert that all of these values are not None just to stop mypy complaining
    # These values will never actually be None because they're set in the wrapper() fixture
    # There's probably a better way  do this, because this method is a bit of a bodge, but this works for now
    assert wrapper['A'] is not None and wrapper['B'] is not None and wrapper['C'] is not None and \
           wrapper['D'] is not None and wrapper['E'] is not None and wrapper['F'] is not None and \
           wrapper['G'] is not None

    assert (wrapper.evaluate_expression('A+B') == wrapper['A'] + wrapper['B']).all()
    assert (wrapper.evaluate_expression('E+F') == wrapper['E'] + wrapper['F']).all()
    assert (wrapper.evaluate_expression('G+D') == wrapper['G'] + wrapper['D']).all()
    assert (wrapper.evaluate_expression('C+C') == wrapper['C'] + wrapper['C']).all()
    assert (wrapper.evaluate_expression('D+A') == wrapper['D'] + wrapper['A']).all()
    assert (wrapper.evaluate_expression('B+C') == wrapper['B'] + wrapper['C']).all()

    assert wrapper == preset_wrapper()


def test_simple_two_matrix_multiplication(wrapper: MatrixWrapper) -> None:
    """Test simple multiplication of two matrices."""
    assert wrapper['A'] is not None and wrapper['B'] is not None and wrapper['C'] is not None and \
           wrapper['D'] is not None and wrapper['E'] is not None and wrapper['F'] is not None and \
           wrapper['G'] is not None

    assert (wrapper.evaluate_expression('AB') == wrapper['A'] @ wrapper['B']).all()
    assert (wrapper.evaluate_expression('BA') == wrapper['B'] @ wrapper['A']).all()
    assert (wrapper.evaluate_expression('AC') == wrapper['A'] @ wrapper['C']).all()
    assert (wrapper.evaluate_expression('DA') == wrapper['D'] @ wrapper['A']).all()
    assert (wrapper.evaluate_expression('ED') == wrapper['E'] @ wrapper['D']).all()
    assert (wrapper.evaluate_expression('FD') == wrapper['F'] @ wrapper['D']).all()
    assert (wrapper.evaluate_expression('GA') == wrapper['G'] @ wrapper['A']).all()
    assert (wrapper.evaluate_expression('CF') == wrapper['C'] @ wrapper['F']).all()
    assert (wrapper.evaluate_expression('AG') == wrapper['A'] @ wrapper['G']).all()

    assert wrapper == preset_wrapper()


def test_identity_multiplication(wrapper: MatrixWrapper) -> None:
    """Test that multiplying by the identity doesn't change the value of a matrix."""
    assert wrapper['A'] is not None and wrapper['B'] is not None and wrapper['C'] is not None and \
           wrapper['D'] is not None and wrapper['E'] is not None and wrapper['F'] is not None and \
           wrapper['G'] is not None

    assert (wrapper.evaluate_expression('I') == wrapper['I']).all()
    assert (wrapper.evaluate_expression('AI') == wrapper['A']).all()
    assert (wrapper.evaluate_expression('IA') == wrapper['A']).all()
    assert (wrapper.evaluate_expression('GI') == wrapper['G']).all()
    assert (wrapper.evaluate_expression('IG') == wrapper['G']).all()

    assert (wrapper.evaluate_expression('EID') == wrapper['E'] @ wrapper['D']).all()
    assert (wrapper.evaluate_expression('IED') == wrapper['E'] @ wrapper['D']).all()
    assert (wrapper.evaluate_expression('EDI') == wrapper['E'] @ wrapper['D']).all()
    assert (wrapper.evaluate_expression('IEIDI') == wrapper['E'] @ wrapper['D']).all()
    assert (wrapper.evaluate_expression('EI^3D') == wrapper['E'] @ wrapper['D']).all()

    assert wrapper == preset_wrapper()


def test_simple_three_matrix_multiplication(wrapper: MatrixWrapper) -> None:
    """Test simple multiplication of two matrices."""
    assert wrapper['A'] is not None and wrapper['B'] is not None and wrapper['C'] is not None and \
           wrapper['D'] is not None and wrapper['E'] is not None and wrapper['F'] is not None and \
           wrapper['G'] is not None

    assert (wrapper.evaluate_expression('ABC') == wrapper['A'] @ wrapper['B'] @ wrapper['C']).all()
    assert (wrapper.evaluate_expression('ACB') == wrapper['A'] @ wrapper['C'] @ wrapper['B']).all()
    assert (wrapper.evaluate_expression('BAC') == wrapper['B'] @ wrapper['A'] @ wrapper['C']).all()
    assert (wrapper.evaluate_expression('EFG') == wrapper['E'] @ wrapper['F'] @ wrapper['G']).all()
    assert (wrapper.evaluate_expression('DAC') == wrapper['D'] @ wrapper['A'] @ wrapper['C']).all()
    assert (wrapper.evaluate_expression('GAE') == wrapper['G'] @ wrapper['A'] @ wrapper['E']).all()
    assert (wrapper.evaluate_expression('FAG') == wrapper['F'] @ wrapper['A'] @ wrapper['G']).all()
    assert (wrapper.evaluate_expression('GAF') == wrapper['G'] @ wrapper['A'] @ wrapper['F']).all()

    assert wrapper == preset_wrapper()


def test_matrix_inverses(wrapper: MatrixWrapper) -> None:
    """Test the inverses of single matrices."""
    assert wrapper['A'] is not None and wrapper['B'] is not None and wrapper['C'] is not None and \
           wrapper['D'] is not None and wrapper['E'] is not None and wrapper['F'] is not None and \
           wrapper['G'] is not None

    assert (wrapper.evaluate_expression('A^{-1}') == la.inv(wrapper['A'])).all()
    assert (wrapper.evaluate_expression('B^{-1}') == la.inv(wrapper['B'])).all()
    assert (wrapper.evaluate_expression('C^{-1}') == la.inv(wrapper['C'])).all()
    assert (wrapper.evaluate_expression('D^{-1}') == la.inv(wrapper['D'])).all()
    assert (wrapper.evaluate_expression('E^{-1}') == la.inv(wrapper['E'])).all()
    assert (wrapper.evaluate_expression('F^{-1}') == la.inv(wrapper['F'])).all()
    assert (wrapper.evaluate_expression('G^{-1}') == la.inv(wrapper['G'])).all()

    assert (wrapper.evaluate_expression('A^-1') == la.inv(wrapper['A'])).all()
    assert (wrapper.evaluate_expression('B^-1') == la.inv(wrapper['B'])).all()
    assert (wrapper.evaluate_expression('C^-1') == la.inv(wrapper['C'])).all()
    assert (wrapper.evaluate_expression('D^-1') == la.inv(wrapper['D'])).all()
    assert (wrapper.evaluate_expression('E^-1') == la.inv(wrapper['E'])).all()
    assert (wrapper.evaluate_expression('F^-1') == la.inv(wrapper['F'])).all()
    assert (wrapper.evaluate_expression('G^-1') == la.inv(wrapper['G'])).all()

    assert wrapper == preset_wrapper()


def test_matrix_powers(wrapper: MatrixWrapper) -> None:
    """Test that matrices can be raised to integer powers."""
    assert wrapper['A'] is not None and wrapper['B'] is not None and wrapper['C'] is not None and \
           wrapper['D'] is not None and wrapper['E'] is not None and wrapper['F'] is not None and \
           wrapper['G'] is not None

    assert (wrapper.evaluate_expression('A^2') == la.matrix_power(wrapper['A'], 2)).all()
    assert (wrapper.evaluate_expression('B^4') == la.matrix_power(wrapper['B'], 4)).all()
    assert (wrapper.evaluate_expression('C^{12}') == la.matrix_power(wrapper['C'], 12)).all()
    assert (wrapper.evaluate_expression('D^12') == la.matrix_power(wrapper['D'], 12)).all()
    assert (wrapper.evaluate_expression('E^8') == la.matrix_power(wrapper['E'], 8)).all()
    assert (wrapper.evaluate_expression('F^{-6}') == la.matrix_power(wrapper['F'], -6)).all()
    assert (wrapper.evaluate_expression('G^-2') == la.matrix_power(wrapper['G'], -2)).all()

    assert wrapper == preset_wrapper()


def test_matrix_transpose(wrapper: MatrixWrapper) -> None:
    """Test matrix transpositions."""
    assert wrapper['A'] is not None and wrapper['B'] is not None and wrapper['C'] is not None and \
           wrapper['D'] is not None and wrapper['E'] is not None and wrapper['F'] is not None and \
           wrapper['G'] is not None

    assert (wrapper.evaluate_expression('A^{T}') == wrapper['A'].T).all()
    assert (wrapper.evaluate_expression('B^{T}') == wrapper['B'].T).all()
    assert (wrapper.evaluate_expression('C^{T}') == wrapper['C'].T).all()
    assert (wrapper.evaluate_expression('D^{T}') == wrapper['D'].T).all()
    assert (wrapper.evaluate_expression('E^{T}') == wrapper['E'].T).all()
    assert (wrapper.evaluate_expression('F^{T}') == wrapper['F'].T).all()
    assert (wrapper.evaluate_expression('G^{T}') == wrapper['G'].T).all()

    assert (wrapper.evaluate_expression('A^T') == wrapper['A'].T).all()
    assert (wrapper.evaluate_expression('B^T') == wrapper['B'].T).all()
    assert (wrapper.evaluate_expression('C^T') == wrapper['C'].T).all()
    assert (wrapper.evaluate_expression('D^T') == wrapper['D'].T).all()
    assert (wrapper.evaluate_expression('E^T') == wrapper['E'].T).all()
    assert (wrapper.evaluate_expression('F^T') == wrapper['F'].T).all()
    assert (wrapper.evaluate_expression('G^T') == wrapper['G'].T).all()

    assert wrapper == preset_wrapper()


def test_rotation_matrices(wrapper: MatrixWrapper) -> None:
    """Test that 'rot(angle)' can be used in an expression."""
    assert (wrapper.evaluate_expression('rot(90)') == create_rotation_matrix(90)).all()
    assert (wrapper.evaluate_expression('rot(180)') == create_rotation_matrix(180)).all()
    assert (wrapper.evaluate_expression('rot(270)') == create_rotation_matrix(270)).all()
    assert (wrapper.evaluate_expression('rot(360)') == create_rotation_matrix(360)).all()
    assert (wrapper.evaluate_expression('rot(45)') == create_rotation_matrix(45)).all()
    assert (wrapper.evaluate_expression('rot(30)') == create_rotation_matrix(30)).all()

    assert (wrapper.evaluate_expression('rot(13.43)') == create_rotation_matrix(13.43)).all()
    assert (wrapper.evaluate_expression('rot(49.4)') == create_rotation_matrix(49.4)).all()
    assert (wrapper.evaluate_expression('rot(-123.456)') == create_rotation_matrix(-123.456)).all()
    assert (wrapper.evaluate_expression('rot(963.245)') == create_rotation_matrix(963.245)).all()
    assert (wrapper.evaluate_expression('rot(-235.24)') == create_rotation_matrix(-235.24)).all()


def test_value_errors(wrapper: MatrixWrapper) -> None:
    """Test that evaluate_expression() raises a ValueError for any malformed input."""
    with pytest.raises(ValueError):
        wrapper.evaluate_expression('')
        wrapper.evaluate_expression('+')
        wrapper.evaluate_expression('This is not a valid expression')
