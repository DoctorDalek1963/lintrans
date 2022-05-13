# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides functions to parse and validate matrix expressions."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Pattern

from lintrans.typing_ import MatrixParseList

NAIVE_CHARACTER_CLASS = r'[-+\sA-Z0-9.rot()^{}]'


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
naive_expression_pattern = compile_naive_expression_pattern()


def find_sub_expressions(expression: str) -> list[str]:
    """Find all the sub-expressions in the given expression.

    This function only goes one level deep, so may return strings like ``'A(BC)D'``.

    :raises MatrixParseError: If there are unbalanced parentheses
    """
    sub_expressions: list[str] = []
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

    match = naive_expression_pattern.match(expression)

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
    def tuple(self) -> tuple[str, str, str]:
        """Create a tuple of the token for parsing."""
        return self.multiplier, self.identifier, self.exponent


class ExpressionParser:
    """A class to hold state during parsing."""

    def __init__(self, expression: str):
        """Create an instance of the parser with the given expression."""
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

        self.expression = expression
        self.pointer: int = 0

        self.current_token: MatrixToken = MatrixToken()
        self.current_group: list[tuple[str, str, str]] = []

        self.final_list: MatrixParseList = []

    def __repr__(self) -> str:
        """Return a simple repr."""
        return f'{self.__class__.__module__}.{self.__class__.__name__}("{self.expression}")'

    @property
    def char(self) -> str:
        """Return the char pointed to by the pointer."""
        return self.expression[self.pointer]

    def parse(self) -> MatrixParseList:
        """Parse the instance's matrix expression and return the MatrixParseList.

        :returns MatrixParseList: The parsed expression
        """
        self._parse_multiplication_group()

        while self.pointer < len(self.expression):
            if self.expression[self.pointer] != '+':
                raise MatrixParseError('Expected "+" between multiplication groups')

            self.pointer += 1
            self._parse_multiplication_group()

        return self.final_list

    def _parse_multiplication_group(self) -> None:
        """Parse a group of matrices to be multiplied.

        :returns bool: Success or failure
        """
        while self._parse_matrix():
            if self.pointer >= len(self.expression) or self.char == '+':
                self.final_list.append(self.current_group)
                self.current_group = []
                self.pointer += 1

    def _parse_matrix(self) -> bool:
        """Parse a full matrix using :meth:`_parse_matrix_part`.

        :returns bool: Success or failure
        """
        self.current_token = MatrixToken()

        while self._parse_matrix_part():
            pass  # The actual execution is taken care of in the loop condition

        if self.current_token.identifier == '':
            return False

        self.current_group.append(self.current_token.tuple)
        return True

    def _parse_matrix_part(self) -> bool:
        """Parse part of a matrix (multiplier, identifier, or exponent) from the expression and pointer.

        .. note:: This method mutates ``self.current_token``.

        :returns bool: Success or failure
        :raises MatrixParseError: If we fail to parse this part of the token
        """
        if self.pointer >= len(self.expression):
            return False

        if self.char.isdigit() or self.char == '-':
            if self.current_token.multiplier != '' \
                    or (self.current_token.multiplier == '' and self.current_token.identifier != ''):
                return False

            self._parse_multiplier()

        elif self.char.isalpha() and self.char.isupper():
            if self.current_token.identifier != '':
                return False

            self.current_token.identifier = self.char
            self.pointer += 1

        elif self.char == 'r':
            if self.current_token.identifier != '':
                return False

            self._parse_rot_identifier()

        elif self.char == '(':
            if self.current_token.identifier != '':
                return False

            self._parse_sub_expression()

        elif self.char == '^':
            if self.current_token.exponent != '':
                return False

            self._parse_exponent()

        elif self.char == '+':
            return False

        else:
            raise MatrixParseError(f'Unrecognised character "{self.char}" in matrix expression')

        return True

    def _parse_multiplier(self) -> None:
        """Parse a multiplier from the expression and pointer.

        .. note:: This method mutates ``self.current_token.multiplier``.

        :raises MatrixParseError: If we fail to parse this part of the token
        """
        multiplier = ''

        while self.char.isdigit() or self.char in ('.', '-'):
            multiplier += self.char
            self.pointer += 1

        # There can only be one dot in the multiplier
        if len(multiplier.split('.')) > 2:
            raise MatrixParseError(f'Multiplier "{multiplier}" has more than one dot')

        if '-' in multiplier and '-' in multiplier[1:]:
            raise MatrixParseError('Character "-" can only occur at the start of a multiplier')

        self.current_token.multiplier = multiplier

    def _parse_rot_identifier(self) -> None:
        """Parse a ``rot()``-style identifier from the expression and pointer.

        .. note:: this method mutates ``self.current_token.identifier``.

        :raises MatrixParseError: If we fail to parse this part of the token
        """
        if match := re.match(r'rot\([^()]+\)', self.expression[self.pointer:]):
            self.current_token.identifier = match.group(0)
            self.pointer += len(match.group(0))
        else:
            raise MatrixParseError(f'Invalid rot-identifier "{self.expression[self.pointer:self.pointer + 15]}..."')

    def _parse_sub_expression(self) -> None:
        """Parse a parenthesized sub-expression as the identifier, from the expression and pointer.

        .. note:: this method mutates ``self.current_token.identifier``.

        :raises MatrixParseError: If we fail to parse this part of the token
        """
        if self.char != '(':
            raise MatrixParseError('Sub-expression must start with "("')

        self.pointer += 1
        paren_depth = 1
        identifier = ''

        while paren_depth > 0:
            if self.char == '(':
                paren_depth += 1
            elif self.char == ')':
                paren_depth -= 1

            if paren_depth == 0:
                self.pointer += 1
                break

            identifier += self.char
            self.pointer += 1

        self.current_token.identifier = identifier

    def _parse_exponent(self) -> None:
        """Parse a matrix exponent from the expression and pointer.

        .. note:: this method mutates ``self.current_token.exponent``.

        :raises MatrixParseError: If we fail to parse this part of the token
        """
        if match := re.match(r'\^\{(-?\d+|T)\}', self.expression[self.pointer:]):
            self.current_token.exponent = match.group(1)
            self.pointer += len(match.group(0))
        else:
            raise MatrixParseError(f'Invalid exponent "{self.expression[self.pointer:self.pointer + 10]}..."')


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

    :param str expression: The expression to be parsed
    :returns: A list of parsed components
    :rtype: :data:`lintrans.typing_.MatrixParseList`
    """
    return ExpressionParser(expression).parse()
