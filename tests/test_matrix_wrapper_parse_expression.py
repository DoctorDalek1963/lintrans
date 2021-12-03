"""Test the MatrixWrapper parse_expression() method."""

import numpy as np
from numpy import linalg as la
import pytest
from lintrans.matrices import MatrixWrapper


@pytest.fixture
def wrapper() -> MatrixWrapper:
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


def test_simple_matrix_addition(wrapper: MatrixWrapper) -> None:
    """Test simple addition and subtraction of two matrices."""

    # NOTE: We assert that all of these values are not None just to stop mypy complaining
    # These values will never actually be None because they're set in the wrapper() fixture
    # There's probably a better way  do this, because this method is a bit of a bdoge, but this works for now
    assert wrapper['A'] is not None and wrapper['B'] is not None and wrapper['C'] is not None and \
        wrapper['D'] is not None and wrapper['E'] is not None and wrapper['F'] is not None and \
        wrapper['G'] is not None

    assert (wrapper.parse_expression('A+B') == wrapper['A'] + wrapper['B']).all()
    assert (wrapper.parse_expression('E+F') == wrapper['E'] + wrapper['F']).all()
    assert (wrapper.parse_expression('G+D') == wrapper['G'] + wrapper['D']).all()
    assert (wrapper.parse_expression('C+C') == wrapper['C'] + wrapper['C']).all()
    assert (wrapper.parse_expression('D+A') == wrapper['D'] + wrapper['A']).all()
    assert (wrapper.parse_expression('B+C') == wrapper['B'] + wrapper['C']).all()


def test_simple_two_matrix_multiplication(wrapper: MatrixWrapper) -> None:
    """Test simple multiplication of two matrices."""
    assert wrapper['A'] is not None and wrapper['B'] is not None and wrapper['C'] is not None and \
           wrapper['D'] is not None and wrapper['E'] is not None and wrapper['F'] is not None and \
           wrapper['G'] is not None

    assert (wrapper.parse_expression('AB') == wrapper['A'] @ wrapper['B']).all()
    assert (wrapper.parse_expression('BA') == wrapper['B'] @ wrapper['A']).all()
    assert (wrapper.parse_expression('AC') == wrapper['A'] @ wrapper['C']).all()
    assert (wrapper.parse_expression('DA') == wrapper['D'] @ wrapper['A']).all()
    assert (wrapper.parse_expression('ED') == wrapper['E'] @ wrapper['D']).all()
    assert (wrapper.parse_expression('FD') == wrapper['F'] @ wrapper['D']).all()
    assert (wrapper.parse_expression('GA') == wrapper['G'] @ wrapper['A']).all()
    assert (wrapper.parse_expression('CF') == wrapper['C'] @ wrapper['F']).all()
    assert (wrapper.parse_expression('AG') == wrapper['A'] @ wrapper['G']).all()


def test_identity_multiplication(wrapper: MatrixWrapper) -> None:
    """Test that multiplying by the identity doesn't change the value of a matrix."""
    assert wrapper['A'] is not None and wrapper['B'] is not None and wrapper['C'] is not None and \
           wrapper['D'] is not None and wrapper['E'] is not None and wrapper['F'] is not None and \
           wrapper['G'] is not None

    assert (wrapper.parse_expression('I') == wrapper['I']).all()
    assert (wrapper.parse_expression('AI') == wrapper['A']).all()
    assert (wrapper.parse_expression('IA') == wrapper['A']).all()
    assert (wrapper.parse_expression('GI') == wrapper['G']).all()
    assert (wrapper.parse_expression('IG') == wrapper['G']).all()

    assert (wrapper.parse_expression('EID') == wrapper['E'] @ wrapper['D']).all()
    assert (wrapper.parse_expression('IED') == wrapper['E'] @ wrapper['D']).all()
    assert (wrapper.parse_expression('EDI') == wrapper['E'] @ wrapper['D']).all()
    assert (wrapper.parse_expression('IEIDI') == wrapper['E'] @ wrapper['D']).all()
    assert (wrapper.parse_expression('EI^3D') == wrapper['E'] @ wrapper['D']).all()


def test_simple_three_matrix_multiplication(wrapper: MatrixWrapper) -> None:
    """Test simple multiplication of two matrices."""
    assert wrapper['A'] is not None and wrapper['B'] is not None and wrapper['C'] is not None and \
           wrapper['D'] is not None and wrapper['E'] is not None and wrapper['F'] is not None and \
           wrapper['G'] is not None

    assert (wrapper.parse_expression('ABC') == wrapper['A'] @ wrapper['B'] @ wrapper['C']).all()
    assert (wrapper.parse_expression('ACB') == wrapper['A'] @ wrapper['C'] @ wrapper['B']).all()
    assert (wrapper.parse_expression('BAC') == wrapper['B'] @ wrapper['A'] @ wrapper['C']).all()
    assert (wrapper.parse_expression('EFG') == wrapper['E'] @ wrapper['F'] @ wrapper['G']).all()
    assert (wrapper.parse_expression('DAC') == wrapper['D'] @ wrapper['A'] @ wrapper['C']).all()
    assert (wrapper.parse_expression('GAE') == wrapper['G'] @ wrapper['A'] @ wrapper['E']).all()
    assert (wrapper.parse_expression('FAG') == wrapper['F'] @ wrapper['A'] @ wrapper['G']).all()
    assert (wrapper.parse_expression('GAF') == wrapper['G'] @ wrapper['A'] @ wrapper['F']).all()


def test_matrix_inverses(wrapper: MatrixWrapper) -> None:
    """Test the inverses of single matrices."""
    assert wrapper['A'] is not None and wrapper['B'] is not None and wrapper['C'] is not None and \
           wrapper['D'] is not None and wrapper['E'] is not None and wrapper['F'] is not None and \
           wrapper['G'] is not None

    assert (wrapper.parse_expression('A^{-1}') == la.inv(wrapper['A'])).all()
    assert (wrapper.parse_expression('B^{-1}') == la.inv(wrapper['B'])).all()
    assert (wrapper.parse_expression('C^{-1}') == la.inv(wrapper['C'])).all()
    assert (wrapper.parse_expression('D^{-1}') == la.inv(wrapper['D'])).all()
    assert (wrapper.parse_expression('E^{-1}') == la.inv(wrapper['E'])).all()
    assert (wrapper.parse_expression('F^{-1}') == la.inv(wrapper['F'])).all()
    assert (wrapper.parse_expression('G^{-1}') == la.inv(wrapper['G'])).all()

    assert (wrapper.parse_expression('A^-1') == la.inv(wrapper['A'])).all()
    assert (wrapper.parse_expression('B^-1') == la.inv(wrapper['B'])).all()
    assert (wrapper.parse_expression('C^-1') == la.inv(wrapper['C'])).all()
    assert (wrapper.parse_expression('D^-1') == la.inv(wrapper['D'])).all()
    assert (wrapper.parse_expression('E^-1') == la.inv(wrapper['E'])).all()
    assert (wrapper.parse_expression('F^-1') == la.inv(wrapper['F'])).all()
    assert (wrapper.parse_expression('G^-1') == la.inv(wrapper['G'])).all()


def test_matrix_powers(wrapper: MatrixWrapper) -> None:
    """Test that matrices can be raised to integer powers."""
    assert wrapper['A'] is not None and wrapper['B'] is not None and wrapper['C'] is not None and \
           wrapper['D'] is not None and wrapper['E'] is not None and wrapper['F'] is not None and \
           wrapper['G'] is not None

    assert (wrapper.parse_expression('A^2') == la.matrix_power(wrapper['A'], 2)).all()
    assert (wrapper.parse_expression('B^4') == la.matrix_power(wrapper['B'], 4)).all()
    assert (wrapper.parse_expression('C^{12}') == la.matrix_power(wrapper['C'], 12)).all()
    assert (wrapper.parse_expression('D^12') == la.matrix_power(wrapper['D'], 12)).all()
    assert (wrapper.parse_expression('E^8') == la.matrix_power(wrapper['E'], 8)).all()
    assert (wrapper.parse_expression('F^{-6}') == la.matrix_power(wrapper['F'], -6)).all()
    assert (wrapper.parse_expression('G^-2') == la.matrix_power(wrapper['G'], -2)).all()


def test_matrix_transpose(wrapper: MatrixWrapper) -> None:
    """Test matrix transpositions."""
    assert wrapper['A'] is not None and wrapper['B'] is not None and wrapper['C'] is not None and \
           wrapper['D'] is not None and wrapper['E'] is not None and wrapper['F'] is not None and \
           wrapper['G'] is not None

    assert (wrapper.parse_expression('A^{T}') == wrapper['A'].T).all()
    assert (wrapper.parse_expression('B^{T}') == wrapper['B'].T).all()
    assert (wrapper.parse_expression('C^{T}') == wrapper['C'].T).all()
    assert (wrapper.parse_expression('D^{T}') == wrapper['D'].T).all()
    assert (wrapper.parse_expression('E^{T}') == wrapper['E'].T).all()
    assert (wrapper.parse_expression('F^{T}') == wrapper['F'].T).all()
    assert (wrapper.parse_expression('G^{T}') == wrapper['G'].T).all()

    assert (wrapper.parse_expression('A^T') == wrapper['A'].T).all()
    assert (wrapper.parse_expression('B^T') == wrapper['B'].T).all()
    assert (wrapper.parse_expression('C^T') == wrapper['C'].T).all()
    assert (wrapper.parse_expression('D^T') == wrapper['D'].T).all()
    assert (wrapper.parse_expression('E^T') == wrapper['E'].T).all()
    assert (wrapper.parse_expression('F^T') == wrapper['F'].T).all()
    assert (wrapper.parse_expression('G^T') == wrapper['G'].T).all()
