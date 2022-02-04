"""This module provides functions to parse and validate matrix expressions."""

from __future__ import annotations

import re
from typing import Pattern

from lintrans.typing import MatrixParseList


class MatrixParseError(Exception):
    """A simple exception to be raised when an error is found when parsing."""


def compile_valid_expression_pattern() -> Pattern[str]:
    """Compile the single RegEx pattern that will match a valid matrix expression."""
    digit_no_zero = '[123456789]'
    digits = '\\d+'
    integer_no_zero = digit_no_zero + '(' + digits + ')?'
    real_number = f'({integer_no_zero}(\\.{digits})?|0?\\.{digits})'

    index_content = f'(-?{integer_no_zero}|T)'
    index = f'(\\^{{{index_content}}}|\\^{index_content})'
    matrix_identifier = f'([A-Z]|rot\\(-?{real_number}\\))'
    matrix = '(' + real_number + '?' + matrix_identifier + index + '?)'
    expression = f'^-?{matrix}+((\\+|-){matrix}+)*$'

    return re.compile(expression)


# This is an expensive pattern to compile, so we compile it when this module is initialized
valid_expression_pattern = compile_valid_expression_pattern()


def validate_matrix_expression(expression: str) -> bool:
    """Validate the given matrix expression.

    This function simply checks the expression against the BNF schema documented in
    :ref:`expression-syntax-docs`. It is not aware of which matrices are actually defined
    in a wrapper. For an aware version of this function, use the
    :meth:`lintrans.matrices.wrapper.MatrixWrapper.is_valid_expression` method.

    :param str expression: The expression to be validated
    :returns: Whether the expression is valid according to the schema
    :rtype: bool
    """
    # Remove all whitespace
    expression = re.sub(r'\s', '', expression)

    match = valid_expression_pattern.match(expression)

    if match is None:
        return False

    # Check if the whole expression was matched against
    return expression == match.group(0)


def parse_matrix_expression(expression: str) -> MatrixParseList:
    """Parse the matrix expression.

    The return value is a list containing lists of tuples. The structure of each tuple is
    (multiplier, matrix identifier, index) where all of them are strings. These tuples are
    contained in lists which represent multplication groups. Each tuple represents a matrix
    and the list holds the matrices that should be multiplied together, in order. These lists
    are contained by a top level list, which we return. These multiplication group lists
    contained in the top level list should be added together once evaluated.

    In the tuples, the multiplier is a string representing a real number, the matrix identifier
    is a capital letter or ``rot(x)`` where x is a real number angle, and the index is a string
    representing an integer, or it's the letter ``T`` for transpose.

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
    :rtype: MatrixParseList
    """
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

    return [
        [
            # The tuple returned by re.findall is (multiplier, matrix identifier, full index, stripped index),
            # so we have to remove the full index, which contains the {}
            (t[0], t[1], t[3])
            for t in re.findall(r'(-?\d*\.?\d*)?([A-Z]|rot\(-?\d+\.?\d*\))(\^{(-?\d+|T)})?', group)
        ]
        # We just split the expression by '+' to have separate groups
        for group in expression.split('+')
    ]
