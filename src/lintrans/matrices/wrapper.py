"""A module primarily containing a simple MatrixWrapper class to wrap matrices and context.

Classes:
    MatrixWrapper:
        A simple wrapper class to hold all possible matrices and allow access to them.

Functions:
    create_rotation_matrix(angle: float, degrees: bool = True) -> MatrixType:
        Create a matrix representing a rotation by the given angle (anticlockwise).
"""

import numpy as np
import re
from functools import reduce
from operator import add, matmul
from typing import Optional

from .. import _parse
from ..typing import MatrixType


class MatrixWrapper:
    """A simple wrapper class to hold all possible matrices and allow access to them.

    The contained matrices can be accessed with square bracket notation.

    :Example:

    >>> wrapper = MatrixWrapper()
    >>> wrapper['I']
    array([[1., 0.],
           [0., 1.]])
    >>> wrapper['M']  # Returns None
    >>> wrapper['M'] = np.array([[1, 2], [3, 4]])
    >>> wrapper['M']
    array([[1., 2.],
           [3., 4.]])

    Methods:
        is_valid_expression(expression: str) -> bool:
            Check if the given expression is valid, using the context of the wrapper.

        evaluate_expression(expression: str) -> MatrixType:
            Evaluate a given expression and return the matrix for that expression.
    """

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

    def __repr__(self) -> str:
        """Return a nice string repr of the MatrixWrapper for debugging."""
        defined_matrices = ''.join([k for k, v in self._matrices.items() if v is not None])
        return f'<{self.__class__.__module__}.{self.__class__.__name__} object with ' \
               f"{len(defined_matrices)} defined matrices: '{defined_matrices}'>"

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
        if (match := re.match(r'rot\((-?\d*\.?\d*)\)', name)) is not None:
            return create_rotation_matrix(float(match.group(1)))

        # Return the transpose of this matrix
        if (match := re.match(r'([A-Z])t', name)) is not None:
            if (matrix := self[match.group(1)]) is not None:
                return matrix.T
            else:
                return None

        if name not in self._matrices:
            raise NameError(f'Unrecognised matrix name "{name}"')

        return self._matrices[name]

    def __setitem__(self, name: str, new_matrix: Optional[MatrixType]) -> None:
        """Set the value of matrix `name` with the new_matrix.

        :param str name: The name of the matrix to set the value of
        :param Optional[MatrixType] new_matrix: The value of the new matrix
        :rtype: None

        :raises NameError: If the name isn't a valid matrix name or is 'I'
        :raises TypeError: If the matrix isn't a valid 2x2 NumPy array
        """
        if name not in self._matrices.keys():
            raise NameError('Matrix name must be a single capital letter')

        if name == 'I':
            raise NameError('Matrix name cannot be "I"')

        if new_matrix is None:
            self._matrices[name] = None
            return

        # We can't just do 'if not isinstance(new_matrix, MatrixType):', because that doesn't work
        if not isinstance(new_matrix, np.ndarray) or not new_matrix.shape == (2, 2):
            raise TypeError('Matrix must be a 2x2 NumPy array')

        # All matrices must have float entries
        a = float(new_matrix[0][0])
        b = float(new_matrix[0][1])
        c = float(new_matrix[1][0])
        d = float(new_matrix[1][1])

        self._matrices[name] = np.array([[a, b], [c, d]])

    def is_valid_expression(self, expression: str) -> bool:
        """Check if the given expression is valid, using the context of the wrapper.

        This method calls _parse.validate_matrix_expression(), but also ensures
        that all the matrices in the expression are defined in the wrapper.

        :param str expression: The expression to validate
        :returns bool: Whether the expression is valid according the schema
        """
        # Get rid of the transposes to check all capital letters
        expression = re.sub(r'\^T', 't', expression)
        expression = re.sub(r'\^{T}', 't', expression)

        # Make sure all the referenced matrices are defined
        for matrix in {x for x in expression if re.match('[A-Z]', x)}:
            if self[matrix] is None:
                return False

        return _parse.validate_matrix_expression(expression)

    def evaluate_expression(self, expression: str) -> MatrixType:
        """Evaluate a given expression and return the matrix for that expression.

        Expressions are written with standard LaTeX notation for exponents. All whitespace is ignored.

        Here is documentation on syntax:
            A single matrix is written as a capital letter like 'A', or as 'rot(x)', where x is some angle in degrees.
            Matrix A multiplied by matrix B is written as 'AB'
            Matrix A plus matrix B is written as 'A+B'
            Matrix A minus matrix B is written as 'A-B'
            Matrix A squared is written as 'A^2'
            Matrix A to the power of 10 is written as 'A^10' or 'A^{10}'
            The inverse of matrix A is written as 'A^-1' or 'A^{-1}'
            The transpose of matrix A is written as 'A^T' or 'At'
            Any matrix may be multiplied by a real constant, like '3A', or '1.2B'

        :param str expression: The expression to be parsed
        :returns MatrixType: The matrix result of the expression

        :raises ValueError: If the expression is invalid
        """
        if not self.is_valid_expression(expression):
            raise ValueError('The expression is invalid')

        parsed_result = _parse.parse_matrix_expression(expression)
        final_groups: list[list[MatrixType]] = []

        for group in parsed_result:
            f_group: list[MatrixType] = []

            for matrix in group:
                if matrix[2] == 'T':
                    m = self[matrix[1]]
                    assert m is not None
                    matrix_value = m.T
                else:
                    matrix_value = np.linalg.matrix_power(self[matrix[1]],
                                                          1 if (index := matrix[2]) == '' else int(index))

                matrix_value *= 1 if (multiplier := matrix[0]) == '' else float(multiplier)
                f_group.append(matrix_value)

            final_groups.append(f_group)

        return reduce(add, [reduce(matmul, group) for group in final_groups])


def create_rotation_matrix(angle: float, degrees: bool = True) -> MatrixType:
    """Create a matrix representing a rotation by the given angle (anticlockwise).

    :Example:

    >>> create_rotation_matrix(30)
    array([[ 0.8660254, -0.5      ],
           [ 0.5      ,  0.8660254]])
    >>> create_rotation_matrix(45)
    array([[ 0.70710678, -0.70710678],
           [ 0.70710678,  0.70710678]])
    >>> create_rotation_matrix(np.pi / 3, degrees=False)
    array([[ 0.5      , -0.8660254],
           [ 0.8660254,  0.5      ]])

    :param float angle: The angle to rotate anticlockwise by
    :param bool degrees: Whether to interpret the angle as degrees (True) or radians (False)
    :returns MatrixType: The resultant rotation matrix
    """
    rad = np.deg2rad(angle) if degrees else angle
    return np.array([
        [np.cos(rad), -1 * np.sin(rad)],
        [np.sin(rad), np.cos(rad)]
    ])
