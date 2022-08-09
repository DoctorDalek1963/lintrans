# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides functions to parse and validate matrix expressions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Pattern, Tuple

from lintrans.typing_ import MatrixParseList

NAIVE_CHARACTER_CLASS = r'[-+\sA-Z0-9.rot()^{}]'
"""This is a RegEx character class that just holds all the valid characters for an expression.

See :func:`validate_matrix_expression` to actually validate matrix expressions.
"""


class MatrixParseError(Exception):
    """A simple exception to be raised when an error is found when parsing."""


def compile_naive_expression_pattern() -> Pattern[str]:
    """Compile the single RegEx pattern that will match a valid matrix expression."""
    digit_no_zero = '[123456789]'
    digits = '\\d+'
    integer_no_zero = digit_no_zero + '(' + digits + ')?'
    real_number = f'({integer_no_zero}(\\.{digits})?|0\\.{digits})'

    index_content = f'(-?{integer_no_zero}|T)'
    index = f'(\\^{{{index_content}}}|\\^{index_content})'
    matrix_identifier = f'([A-Z]|rot\\(-?{real_number}\\)|\\({NAIVE_CHARACTER_CLASS}+\\))'
    matrix = '(' + real_number + '?' + matrix_identifier + index + '?)'
    expression = f'^-?{matrix}+((\\+-?|-){matrix}+)*$'

    return re.compile(expression)


# This is an expensive pattern to compile, so we compile it when this module is initialized
_naive_expression_pattern = compile_naive_expression_pattern()


def find_sub_expressions(expression: str) -> List[str]:
    """Find all the sub-expressions in the given expression.

    This function only goes one level deep, so may return strings like ``'A(BC)D'``.

    :raises MatrixParseError: If there are unbalanced parentheses
    """
    sub_expressions: List[str] = []
    string = ''
    paren_depth = 0
    pointer = 0

    while True:
        char = expression[pointer]

        if char == '(' and expression[pointer - 3:pointer] != 'rot':
            paren_depth += 1

            # This is a bit of a manual bodge, but it eliminates extraneous parens
            if paren_depth == 1:
                pointer += 1
                continue

        elif char == ')' and re.match(f'{NAIVE_CHARACTER_CLASS}*?rot\\([-\\d.]+$', expression[:pointer]) is None:
            paren_depth -= 1

        if paren_depth > 0:
            string += char

        if paren_depth == 0 and string:
            sub_expressions.append(string)
            string = ''

        pointer += 1

        if pointer >= len(expression):
            break

    if paren_depth != 0:
        raise MatrixParseError('Unbalanced parentheses in expression')

    return sub_expressions


def validate_matrix_expression(expression: str) -> bool:
    """Validate the given matrix expression.

    This function simply checks the expression against the BNF schema documented in
    :ref:`expression-syntax-docs`. It is not aware of which matrices are actually defined
    in a wrapper. For an aware version of this function, use the
    :meth:`lintrans.matrices.wrapper.MatrixWrapper.is_valid_expression` method.

    :param str expression: The expression to be validated
    :returns bool: Whether the expression is valid according to the schema
    """
    # Remove all whitespace
    expression = re.sub(r'\s', '', expression)

    match = _naive_expression_pattern.match(expression)

    if match is None:
        return False

    # Check that the whole expression was matched against
    if expression != match.group(0):
        return False

    try:
        sub_expressions = find_sub_expressions(expression)
    except MatrixParseError:
        return False

    if not sub_expressions:
        return True

    return all(validate_matrix_expression(m) for m in sub_expressions)


@dataclass
class MatrixToken:
    """A simple dataclass to hold information about a matrix token being parsed."""

    multiplier: str = ''
    identifier: str = ''
    exponent: str = ''

    @property
    def tuple(self) -> Tuple[str, str, str]:
        """Create a tuple of the token for parsing."""
        return self.multiplier, self.identifier, self.exponent


class ExpressionParser:
    """A class to hold state during parsing.

    Most of the methods in this class are class-internal and should not be used from outside.

    This class should be used like this:

    >>> ExpressionParser('3A^-1B').parse()
    [[('3', 'A', '-1'), ('', 'B', '')]]
    >>> ExpressionParser('4(M^TA^2)^-2').parse()
    [[('4', 'M^{T}A^{2}', '-2')]]
    """

    def __init__(self, expression: str):
        """Create an instance of the parser with the given expression and initialise variables to use during parsing."""
        # Remove all whitespace
        expression = re.sub(r'\s', '', expression)

        # Check if it's valid
        if not validate_matrix_expression(expression):
            raise MatrixParseError('Invalid expression')

        # Wrap all exponents and transposition powers with {}
        expression = re.sub(r'(?<=\^)(-?\d+|T)(?=[^}]|$)', r'{\g<0>}', expression)

        # Remove any standalone minuses
        expression = re.sub(r'-(?=[A-Z])', '-1', expression)

        # Replace subtractions with additions
        expression = re.sub(r'-(?=\d+\.?\d*([A-Z]|rot))', '+-', expression)

        # Get rid of a potential leading + introduced by the last step
        expression = re.sub(r'^\+', '', expression)

        self._expression = expression
        self._pointer: int = 0

        self._current_token = MatrixToken()
        self._current_group: List[Tuple[str, str, str]] = []

        self._final_list: MatrixParseList = []

    def __repr__(self) -> str:
        """Return a simple repr containing the expression."""
        return f'{self.__class__.__module__}.{self.__class__.__name__}("{self._expression}")'

    @property
    def _char(self) -> str:
        """Return the character pointed to by the pointer."""
        return self._expression[self._pointer]

    def parse(self) -> MatrixParseList:
        """Fully parse the instance's matrix expression and return the :attr:`lintrans.typing_.MatrixParseList`.

        This method uses all the private methods of this class to parse the
        expression in parts. All private methods mutate the instance variables.

        :returns: The parsed expression
        :rtype: :attr:`lintrans.typing_.MatrixParseList`
        """
        self._parse_multiplication_group()

        while self._pointer < len(self._expression):
            if self._expression[self._pointer] != '+':
                raise MatrixParseError('Expected "+" between multiplication groups')

            self._pointer += 1
            self._parse_multiplication_group()

        return self._final_list

    def _parse_multiplication_group(self) -> None:
        """Parse a group of matrices to be multiplied together.

        This method just parses matrices until we get to a ``+``.
        """
        # This loop continues to parse matrices until we fail to do so
        while self._parse_matrix():
            # Once we get to the end of the multiplication group, we add it the final list and reset the group list
            if self._pointer >= len(self._expression) or self._char == '+':
                self._final_list.append(self._current_group)
                self._current_group = []
                self._pointer += 1

    def _parse_matrix(self) -> bool:
        """Parse a full matrix using :meth:`_parse_matrix_part`.

        This method will parse an optional multiplier, an identifier, and an optional exponent. If we
        do this successfully, we return True. If we fail to parse a matrix (maybe we've reached the
        end of the current multiplication group and the next char is ``+``), then we return False.

        :returns bool: Success or failure
        """
        self._current_token = MatrixToken()

        while self._parse_matrix_part():
            pass  # The actual execution is taken care of in the loop condition

        if self._current_token.identifier == '':
            return False

        self._current_group.append(self._current_token.tuple)
        return True

    def _parse_matrix_part(self) -> bool:
        """Parse part of a matrix (multiplier, identifier, or exponent).

        Which part of the matrix we parse is dependent on the current value of the pointer and the expression.
        This method will parse whichever part of matrix token that it can. If it can't parse a part of a matrix,
        or it's reached the next matrix, then we just return False. If we succeeded to parse a matrix part, then
        we return True.

        :returns bool: Success or failure
        :raises MatrixParseError: If we fail to parse this part of the matrix
        """
        if self._pointer >= len(self._expression):
            return False

        if self._char.isdigit() or self._char == '-':
            if self._current_token.multiplier != '' \
                    or (self._current_token.multiplier == '' and self._current_token.identifier != ''):
                return False

            self._parse_multiplier()

        elif self._char.isalpha() and self._char.isupper():
            if self._current_token.identifier != '':
                return False

            self._current_token.identifier = self._char
            self._pointer += 1

        elif self._char == 'r':
            if self._current_token.identifier != '':
                return False

            self._parse_rot_identifier()

        elif self._char == '(':
            if self._current_token.identifier != '':
                return False

            self._parse_sub_expression()

        elif self._char == '^':
            if self._current_token.exponent != '':
                return False

            self._parse_exponent()

        elif self._char == '+':
            return False

        else:
            raise MatrixParseError(f'Unrecognised character "{self._char}" in matrix expression')

        return True

    def _parse_multiplier(self) -> None:
        """Parse a multiplier from the expression and pointer.

        This method just parses a numerical multiplier, which can include
        zero or one ``.`` character and optionally a ``-`` at the start.

        :raises MatrixParseError: If we fail to parse this part of the matrix
        """
        multiplier = ''

        while self._char.isdigit() or self._char in ('.', '-'):
            multiplier += self._char
            self._pointer += 1

        try:
            float(multiplier)
        except ValueError as e:
            raise MatrixParseError(f'Invalid multiplier "{multiplier}"') from e

        self._current_token.multiplier = multiplier

    def _parse_rot_identifier(self) -> None:
        """Parse a ``rot()``-style identifier from the expression and pointer.

        This method will just parse something like ``rot(12.5)``. The angle number must be a real number.

        :raises MatrixParseError: If we fail to parse this part of the matrix
        """
        if match := re.match(r'rot\(([\d.-]+)\)', self._expression[self._pointer:]):
            # Ensure that the number in brackets is a valid float
            try:
                float(match.group(1))
            except ValueError as e:
                raise MatrixParseError(f'Invalid angle number "{match.group(1)}" in rot-identifier') from e

            self._current_token.identifier = match.group(0)
            self._pointer += len(match.group(0))
        else:
            raise MatrixParseError(
                f'Invalid rot-identifier "{self._expression[self._pointer : self._pointer + 15]}..."'
            )

    def _parse_sub_expression(self) -> None:
        """Parse a parenthesized sub-expression as the identifier.

        This method will also validate the expression in the parentheses.

        :raises MatrixParseError: If we fail to parse this part of the matrix
        """
        if self._char != '(':
            raise MatrixParseError('Sub-expression must start with "("')

        self._pointer += 1
        paren_depth = 1
        identifier = ''

        while paren_depth > 0:
            if self._char == '(':
                paren_depth += 1
            elif self._char == ')':
                paren_depth -= 1

            if paren_depth == 0:
                self._pointer += 1
                break

            identifier += self._char
            self._pointer += 1

        if not validate_matrix_expression(identifier):
            raise MatrixParseError(f'Invalid sub-expression identifier "{identifier}"')

        self._current_token.identifier = identifier

    def _parse_exponent(self) -> None:
        """Parse a matrix exponent from the expression and pointer.

        The exponent must be an integer or ``T`` for transpose.

        :raises MatrixParseError: If we fail to parse this part of the token
        """
        if match := re.match(r'\^\{(-?\d+|T)\}', self._expression[self._pointer:]):
            exponent = match.group(1)

            try:
                if exponent != 'T':
                    int(exponent)
            except ValueError as e:
                raise MatrixParseError(f'Invalid exponent "{match.group(1)}"') from e

            self._current_token.exponent = exponent
            self._pointer += len(match.group(0))
        else:
            raise MatrixParseError(
                f'Invalid exponent "{self._expression[self._pointer : self._pointer + 10]}..."'
            )


def parse_matrix_expression(expression: str) -> MatrixParseList:
    """Parse the matrix expression and return a :data:`lintrans.typing_.MatrixParseList`.

    :Example:

    >>> parse_matrix_expression('A')
    [[('', 'A', '')]]
    >>> parse_matrix_expression('-3M^2')
    [[('-3', 'M', '2')]]
    >>> parse_matrix_expression('1.2rot(12)^{3}2B^T')
    [[('1.2', 'rot(12)', '3'), ('2', 'B', 'T')]]
    >>> parse_matrix_expression('A^2 + 3B')
    [[('', 'A', '2')], [('3', 'B', '')]]
    >>> parse_matrix_expression('-3A^{-1}3B^T - 45M^2')
    [[('-3', 'A', '-1'), ('3', 'B', 'T')], [('-45', 'M', '2')]]
    >>> parse_matrix_expression('5.3A^{4} 2.6B^{-2} + 4.6D^T 8.9E^{-1}')
    [[('5.3', 'A', '4'), ('2.6', 'B', '-2')], [('4.6', 'D', 'T'), ('8.9', 'E', '-1')]]
    >>> parse_matrix_expression('2(A+B^TC)^2D')
    [[('2', 'A+B^{T}C', '2'), ('', 'D', '')]]

    :param str expression: The expression to be parsed
    :returns: A list of parsed components
    :rtype: :data:`lintrans.typing_.MatrixParseList`
    """
    return ExpressionParser(expression).parse()
