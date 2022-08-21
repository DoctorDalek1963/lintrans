# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module contains the main :class:`MatrixWrapper` class and a function to create a matrix from an angle."""

from __future__ import annotations

import re
from copy import copy
from functools import reduce
from operator import add, matmul
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np

from lintrans.typing_ import is_matrix_type, MatrixType
from .parse import get_matrix_identifiers, parse_matrix_expression, validate_matrix_expression
from .utility import create_rotation_matrix


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
        """Initialize a :class:`MatrixWrapper` object with a dictionary of matrices which can be accessed."""
        self._matrices: Dict[str, Optional[Union[MatrixType, str]]] = {
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

        .. note::
           If the named matrix is defined as an expression, then this method will return its evaluation.
           If you want the expression itself, use :meth:`get_expression`.

        :param str name: The name of the matrix to get
        :returns Optional[MatrixType]: The value of the matrix (could be None)

        :raises NameError: If there is no matrix with the given name
        """
        # Return a new rotation matrix
        if (match := re.match(r'^rot\((-?\d*\.?\d*)\)$', name)) is not None:
            return create_rotation_matrix(float(match.group(1)))

        if name not in self._matrices:
            if validate_matrix_expression(name):
                return self.evaluate_expression(name)

            raise NameError(f'Unrecognised matrix name "{name}"')

        # We copy the matrix before we return it so the user can't accidentally mutate the matrix
        matrix = copy(self._matrices[name])

        if isinstance(matrix, str):
            return self.evaluate_expression(matrix)

        return matrix

    def __setitem__(self, name: str, new_matrix: Optional[Union[MatrixType, str]]) -> None:
        """Set the value of matrix ``name`` with the new_matrix.

        The new matrix may be a simple 2x2 NumPy array, or it could be a string, representing an
        expression in terms of other, previously defined matrices.

        :param str name: The name of the matrix to set the value of
        :param Optional[Union[MatrixType, str]] new_matrix: The value of the new matrix (could be None)

        :raises NameError: If the name isn't a legal matrix name
        :raises TypeError: If the matrix isn't a valid 2x2 NumPy array or expression in terms of other defined matrices
        :raises ValueError: If you attempt to define a matrix in terms of itself
        """
        if not (name in self._matrices and name != 'I'):
            raise NameError('Matrix name is illegal')

        if new_matrix is None:
            self._matrices[name] = None
            return

        if isinstance(new_matrix, str):
            if self.is_valid_expression(new_matrix):
                if name not in new_matrix and \
                        name not in self.get_expression_dependencies(new_matrix):
                    self._matrices[name] = new_matrix
                    return
                else:
                    raise ValueError('Cannot define a matrix recursively')

        if not is_matrix_type(new_matrix):
            raise TypeError('Matrix must be a 2x2 NumPy array')

        # All matrices must have float entries
        a = float(new_matrix[0][0])
        b = float(new_matrix[0][1])
        c = float(new_matrix[1][0])
        d = float(new_matrix[1][1])

        self._matrices[name] = np.array([[a, b], [c, d]])

    def get_matrix_dependencies(self, matrix_name: str) -> Set[str]:
        """Return all the matrices (as identifiers) that the given matrix (indirectly) depends on.

        If A depends on nothing, B directly depends on A, and C directly depends on B,
        then we say C depends on B `and` A.
        """
        expression = self.get_expression(matrix_name)
        if expression is None:
            return set()

        s = set()
        identifiers = get_matrix_identifiers(expression)
        for identifier in identifiers:
            s.add(identifier)
            s.update(self.get_matrix_dependencies(identifier))

        return s

    def get_expression_dependencies(self, expression: str) -> Set[str]:
        """Return all the matrices that the given expression depends on.

        This method just calls :meth:`get_matrix_dependencies` on each matrix
        identifier in the expression. See that method for details.

        If an expression contains a matrix that has no dependencies, then the
        expression is `not` considered to depend on that matrix. But it `is`
        considered to depend on any matrix that has its own dependencies.
        """
        s = set()
        for iden in get_matrix_identifiers(expression):
            s.update(self.get_matrix_dependencies(iden))
        return s

    def get_expression(self, name: str) -> Optional[str]:
        """If the named matrix is defined as an expression, return that expression, else return None.

        :param str name: The name of the matrix
        :returns Optional[str]: The expression that the matrix is defined as, or None

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
        :returns bool: Whether the expression is valid in this wrapper

        :raises LinAlgError: If a matrix is defined in terms of the inverse of a singular matrix
        """
        # Get rid of the transposes to check all capital letters
        new_expression = expression.replace('^T', '').replace('^{T}', '')

        # Make sure all the referenced matrices are defined
        for matrix in [x for x in new_expression if re.match('[A-Z]', x)]:
            if self[matrix] is None:
                return False

            if (expr := self.get_expression(matrix)) is not None:
                if not self.is_valid_expression(expr):
                    return False

        return validate_matrix_expression(expression)

    def evaluate_expression(self, expression: str) -> MatrixType:
        """Evaluate a given expression and return the matrix evaluation.

        :param str expression: The expression to be parsed
        :returns MatrixType: The matrix result of the expression

        :raises ValueError: If the expression is invalid
        """
        if not self.is_valid_expression(expression):
            raise ValueError('The expression is invalid')

        parsed_result = parse_matrix_expression(expression)
        final_groups: List[List[MatrixType]] = []

        for group in parsed_result:
            f_group: List[MatrixType] = []

            for multiplier, identifier, index in group:
                if index == 'T':
                    m = self[identifier]

                    # This assertion is just so mypy doesn't complain
                    # We know this won't be None, because we know that this matrix is defined in this wrapper
                    assert m is not None
                    matrix_value = m.T

                else:
                    # Again, this assertion is just for mypy
                    # We know this will be a matrix, but since upgrading from NumPy 1.21 to 1.23
                    # (to fix a bug with GH Actions on Windows), mypy complains about matrix_power()
                    base_matrix = self[identifier]
                    assert is_matrix_type(base_matrix)

                    matrix_value = np.linalg.matrix_power(base_matrix, 1 if index == '' else int(index))

                matrix_value *= 1 if multiplier == '' else float(multiplier)
                f_group.append(matrix_value)

            final_groups.append(f_group)

        return reduce(add, [reduce(matmul, group) for group in final_groups])

    def get_defined_matrices(self) -> List[Tuple[str, Union[MatrixType, str]]]:
        """Return a list of tuples containing the name and value of all defined matrices in the wrapper.

        :returns: A list of tuples where the first element is the name, and the second element is the value
        :rtype: List[Tuple[str, Union[MatrixType, str]]]
        """
        matrices = []

        for name, value in self._matrices.items():
            if value is not None:
                matrices.append((name, value))

        return matrices
