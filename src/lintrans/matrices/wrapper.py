"""This module contains the main :class:`MatrixWrapper` class and a function to create a matrix from an angle."""

from __future__ import annotations

import re
from copy import copy
from functools import reduce
from operator import add, matmul
from typing import Any, Optional, Union

import numpy as np

from .parse import parse_matrix_expression, validate_matrix_expression
from lintrans.typing import is_matrix_type, MatrixType


class MatrixWrapper:
    """A wrapper class to hold all possible matrices and allow access to them.

    .. note::
       When defining a custom matrix, its name must be a capital letter and cannot be ``I``.

    The contained matrices can be accessed and assigned to using square bracket notation.

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
    """

    def __init__(self):
        """Initialise a :class:`MatrixWrapper` object with a dictionary of matrices which can be accessed."""
        self._matrices: dict[str, Optional[Union[MatrixType, str]]] = {
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
        """Return a nice string repr of the :class:`MatrixWrapper` for debugging."""
        defined_matrices = ''.join([k for k, v in self._matrices.items() if v is not None])
        return f'<{self.__class__.__module__}.{self.__class__.__name__} object with ' \
               f"{len(defined_matrices)} defined matrices: '{defined_matrices}'>"

    def __eq__(self, other: Any) -> bool:
        """Check for equality in wrappers by comparing dictionaries.

        :param Any other: The object to compare this wrapper to
        """
        if not isinstance(other, self.__class__):
            return NotImplemented

        # We loop over every matrix and check if every value is equal in each
        for name in self._matrices:
            s_matrix = self[name]
            o_matrix = other[name]

            if s_matrix is None and o_matrix is None:
                continue

            elif (s_matrix is None and o_matrix is not None) or \
                 (s_matrix is not None and o_matrix is None):
                return False

            # This is mainly to satisfy mypy, because we know these must be matrices
            elif not is_matrix_type(s_matrix) or not is_matrix_type(o_matrix):
                return False

            # Now we know they're both NumPy arrays
            elif np.array_equal(s_matrix, o_matrix):
                continue

            else:
                return False

        return True

    def __hash__(self) -> int:
        """Return the hash of the matrices dictionary."""
        return hash(self._matrices)

    def __getitem__(self, name: str) -> Optional[MatrixType]:
        """Get the matrix with the given name.

        If it is a simple name, it will just be fetched from the dictionary. If the name is ``rot(x)``, with
        a given angle in degrees, then we return a new matrix representing a rotation by that angle.

        :param str name: The name of the matrix to get
        :returns: The value of the matrix (may be None)
        :rtype: Optional[MatrixType]

        :raises NameError: If there is no matrix with the given name
        """
        # Return a new rotation matrix
        if (match := re.match(r'rot\((-?\d*\.?\d*)\)', name)) is not None:
            return create_rotation_matrix(float(match.group(1)))

        if name not in self._matrices:
            raise NameError(f'Unrecognised matrix name "{name}"')

        # We copy the matrix before we return it so the user can't accidentally mutate the matrix
        matrix = copy(self._matrices[name])

        if isinstance(matrix, str):
            return self.evaluate_expression(matrix)

        return matrix

    def __setitem__(self, name: str, new_matrix: Optional[Union[MatrixType, str]]) -> None:
        """Set the value of matrix ``name`` with the new_matrix.

        :param str name: The name of the matrix to set the value of
        :param Optional[Union[MatrixType, str]] new_matrix: The value of the new matrix (may be None)

        :raises NameError: If the name isn't a legal matrix name
        :raises TypeError: If the matrix isn't a valid 2x2 NumPy array
        """
        if not (name in self._matrices and name != 'I'):
            raise NameError('Matrix name is illegal')

        if new_matrix is None:
            self._matrices[name] = None
            return

        if isinstance(new_matrix, str):
            if self.is_valid_expression(new_matrix):
                self._matrices[name] = new_matrix
                return

        if not is_matrix_type(new_matrix):
            raise TypeError('Matrix must be a 2x2 NumPy array')

        # All matrices must have float entries
        a = float(new_matrix[0][0])
        b = float(new_matrix[0][1])
        c = float(new_matrix[1][0])
        d = float(new_matrix[1][1])

        self._matrices[name] = np.array([[a, b], [c, d]])

    def get_expression(self, name: str) -> Optional[str]:
        """If the named matrix is defined as an expression, return that expression, else return None.

        :param str name: The name of the matrix
        :returns: The expression that the matrix is defined as, or None
        :rtype: Optional[str]

        :raises NameError: If the name is invalid
        """
        if name not in self._matrices:
            raise NameError('Matrix must have a legal name')

        matrix = self._matrices[name]
        if isinstance(matrix, str):
            return matrix

        return None

    def is_valid_expression(self, expression: str) -> bool:
        """Check if the given expression is valid, using the context of the wrapper.

        This method calls :func:`lintrans.matrices.parse.validate_matrix_expression`, but also
        ensures that all the matrices in the expression are defined in the wrapper.

        :param str expression: The expression to validate
        :returns: Whether the expression is valid in this wrapper
        :rtype: bool
        """
        # Get rid of the transposes to check all capital letters
        new_expression = expression.replace('^T', '').replace('^{T}', '')

        # Make sure all the referenced matrices are defined
        for matrix in {x for x in new_expression if re.match('[A-Z]', x)}:
            if self[matrix] is None:
                return False

            if (expr := self.get_expression(matrix)) is not None:
                if not self.is_valid_expression(expr):
                    return False

        return validate_matrix_expression(expression)

    def evaluate_expression(self, expression: str) -> MatrixType:
        """Evaluate a given expression and return the matrix evaluation.

        :param str expression: The expression to be parsed
        :returns: The matrix result of the expression
        :rtype: MatrixType

        :raises ValueError: If the expression is invalid
        """
        if not self.is_valid_expression(expression):
            raise ValueError('The expression is invalid')

        parsed_result = parse_matrix_expression(expression)
        final_groups: list[list[MatrixType]] = []

        for group in parsed_result:
            f_group: list[MatrixType] = []

            for matrix in group:
                if matrix[2] == 'T':
                    m = self[matrix[1]]

                    # This assertion is just so mypy doesn't complain
                    # We know this won't be None, because we know that this matrix is defined in this wrapper
                    assert m is not None
                    matrix_value = m.T

                else:
                    matrix_value = np.linalg.matrix_power(self[matrix[1]],
                                                          1 if (index := matrix[2]) == '' else int(index))

                matrix_value *= 1 if (multiplier := matrix[0]) == '' else float(multiplier)
                f_group.append(matrix_value)

            final_groups.append(f_group)

        return reduce(add, [reduce(matmul, group) for group in final_groups])


def create_rotation_matrix(angle: float, *, degrees: bool = True) -> MatrixType:
    """Create a matrix representing a rotation (anticlockwise) by the given angle.

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
    :returns: The resultant matrix
    :rtype: MatrixType
    """
    rad = np.deg2rad(angle) if degrees else angle
    return np.array([
        [np.cos(rad), -1 * np.sin(rad)],
        [np.sin(rad), np.cos(rad)]
    ])
