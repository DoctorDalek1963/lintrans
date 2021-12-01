"""A module containing a simple MatrixWrapper class to wrap matrices and context."""

import numpy as np
import re
from functools import reduce
from typing import Optional

from lintrans.typing import MatrixType


class MatrixWrapper:
    """A simple wrapper class to hold all possible matrices and allow access to them."""

    def __init__(self):
        """Initialise a MatrixWrapper object with a matrices dict."""
        self._matrices: dict[str, Optional[MatrixType]] = {
            'A': None, 'B': None, 'C': None, 'D': None,
            'E': None, 'F': None, 'G': None, 'H': None,
            'I': np.eye(2),  # I is always defined as the identity matrix
            'J': None, 'K': None, 'L': None, 'M': None,
            'N': None, 'O': None, 'P': None, 'Q': None,
            'R': None, 'S': None, 'T': None, 'U': None,
            'V': None, 'W': None, 'X': None, 'Y': None,
            'Z': None
        }

    def __getitem__(self, name: str) -> Optional[MatrixType]:
        """Get the matrix with the given name.

        If it is a simple name, it will just be fetched from the dictionary.
        If the name is followed with a 't', then we will return the transpose of the named matrix.
        If the name is 'rot()', with a given angle in degrees, then we return a new rotation matrix with that angle.

        :param str name: The name of the matrix to get
        :returns: The value of the matrix (may be none)
        :rtype: Optional[MatrixType]

        :raises NameError: If there is no matrix with the given name
        """
        # Return a new rotation matrix
        match = re.match(r'rot\((\d+)\)', name)
        if match is not None:
            return create_rotation_matrix(float(match.group(1)))

        # Return the transpose of this matrix
        match = re.match(r'([A-Z])t', name)
        if match is not None:
            matrix = self[match.group(1)]

            if matrix is not None:
                return matrix.T
            else:
                return None

        if name not in self._matrices:
            raise NameError(f'Unrecognised matrix name "{name}"')

        return self._matrices[name]

    def __setitem__(self, name: str, new_matrix: MatrixType) -> None:
        """Set the value of matrix `name` with the new_matrix.

        :param str name: The name of the matrix to set the value of
        :param MatrixType new_matrix: The value of the new matrix
        :rtype: None

        :raises NameError: If the name isn't a valid matrix name or is 'I'
        """
        if name not in self._matrices.keys():
            raise NameError('Matrix name must be a single capital letter')

        if name == 'I':
            raise NameError('Matrix name cannot be "I"')

        # All matrices must have float entries
        a = float(new_matrix[0][0])
        b = float(new_matrix[0][1])
        c = float(new_matrix[1][0])
        d = float(new_matrix[1][1])

        self._matrices[name] = np.array([[a, b], [c, d]])

    def parse_expression(self, expression: str) -> MatrixType:
        """Parse a given expression and return the matrix for that expression.

        Expressions are written with standard LaTeX notation for exponents. All whitespace is ignored.

        Here is documentation on syntax:
            A single matrix is written as 'A'.
            Matrix A multiplied by matrix B is written as 'AB'
            Matrix A plus matrix B is written as 'A+B'
            Matrix A minus matrix B is written as 'A-B'
            Matrix A squared is written as 'A^2'
            Matrix A to the power of 10 is written as 'A^10' or 'A^{10}'
            The inverse of matrix A is written as 'A^-1' or 'A^{-1}'
            The transpose of matrix A is written as 'A^T' or 'At'

        :param str expression: The expression to be parsed
        :returns MatrixType: The matrix result of the expression

        :raises ValueError: If the expression is invalid, such as an empty string
        """
        if expression == '':
            raise ValueError('The expression cannot be an empty string')

        match = re.search(r'[^-+A-Z^{}rot()\d.]', expression)
        if match is not None:
            raise ValueError(f'Invalid character "{match.group(0)}"')

        # Remove all whitespace in the expression
        expression = re.sub(r'\s', '', expression)

        # Wrap all exponents and transposition powers with {}
        expression = re.sub(r'(?<=\^)(-?\d+|T)(?=[^}]|$)', r'{\g<0>}', expression)

        # Replace all subtractions with additions, multiplied by -1
        expression = re.sub(r'(?<=.)-(?=[A-Z])', '+-1', expression)

        # Replace a possible leading minus sign with -1
        expression = re.sub(r'^-(?=[A-Z])', '-1', expression)

        # Change all transposition exponents into lowercase
        expression = expression.replace('^{T}', 't')

        # Split the expression into groups to be multiplied, and then we add those groups at the end
        # We also have to filter out the empty strings to reduce errors
        multiplication_groups = [x for x in expression.split('+') if x != '']

        # Start with the 0 matrix and add each group on
        matrix_sum: MatrixType = np.array([[0., 0.], [0., 0.]])

        for group in multiplication_groups:
            # Generate a list of tuples, each representing a matrix
            # These tuples are (the multiplier, the matrix (with optional
            # 't' at the end to indicate a transpose), the exponent)
            string_matrices: list[tuple[str, str, str]]

            # The generate tuple is (multiplier, matrix, full exponent, stripped exponent)
            # The full exponent contains ^{}, so we ignore it
            # The multiplier and exponent might be '', so we have to set them to '1'
            string_matrices = [(t[0] if t[0] != '' else '1', t[1], t[3] if t[3] != '' else '1')
                               for t in re.findall(r'(-?\d*\.?\d*)([A-Z]t?|rot\(\d+\))(\^{(-?\d+|T)})?', group)]

            # This list is a list of tuple, where each tuple is (a float multiplier,
            # the matrix (gotten from the wrapper's __getitem__()), the integer power)
            matrices: list[tuple[float, MatrixType, int]]
            matrices = [(float(t[0]), self[t[1]], int(t[2])) for t in string_matrices]

            # Process the matrices and make actual MatrixType objects
            processed_matrices: list[MatrixType] = [t[0] * np.linalg.matrix_power(t[1], t[2]) for t in matrices]

            # Add this matrix product to the sum total
            matrix_sum += reduce(lambda m, n: m @ n, processed_matrices)

        return matrix_sum


def create_rotation_matrix(angle: float) -> MatrixType:
    """Create a matrix representing a rotation by the given number of degrees anticlockwise.

    :param float angle: The number of degrees to rotate by
    :returns MatrixType: The resultant rotation matrix
    """
    rad = np.deg2rad(angle)
    return np.array([
        [np.cos(rad), -1 * np.sin(rad)],
        [np.sin(rad), np.cos(rad)]
    ])
