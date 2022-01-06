"""A simple module to parse matrix expressions.

Constants:
    valid_expression_pattern: str:
        The pre-computed result of compile_valid_expression_pattern()

Classes:
    MatrixParseError(Exception):
        A simple exception to be raised when parsing.

Functions:
    compile_valid_expression_pattern() -> Pattern[str]:
        Compile the single regular expression that will match a valid matrix expression.

    validate_matrix_expression(expression: str) -> bool:
        Validate the given matrix expression.

    parse_matrix_expression(expression: str) -> MatrixParseList:
        Parse the matrix expression and return a list of results.
"""

import re
from typing import Pattern

from ..typing import MatrixParseList


class MatrixParseError(Exception):
    """A simple exception to be raised when parsing."""


def compile_valid_expression_pattern() -> Pattern[str]:
    """Compile the single regular expression that will match a valid matrix expression."""
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

    This function simply checks the expression against a BNF schema. It is not
    aware of which matrices are actually defined in a wrapper. For an aware
    version of this function, use the MatrixWrapper().is_valid_expression() method.

    Here is the schema for a valid expression given in a version of BNF:

        expression        ::=  [ "-" ] matrices { ( "+" | "-" ) matrices };
        matrices          ::=  matrix { matrix };
        matrix            ::=  [ real_number ] matrix_identifier [ index ];
        matrix_identifier ::=  "A" .. "Z" | "rot(" [ "-" ] real_number ")";
        index             ::=  "^{" index_content "}" | "^" index_content | "t";
        index_content     ::=  [ "-" ] integer_not_zero | "T";

        digit_no_zero     ::=  "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9";
        digit             ::=  "0" | digit_no_zero;
        digits            ::=  digit | digits digit;
        integer_not_zero  ::=  digit_no_zero [ digits ];
        real_number       ::=  ( integer_not_zero [ "." digits ] | [ "0" ] "." digits );

    :param str expression: The expression to be validated
    :returns bool: Whether the expression is valid according to the schema
    """
    match = valid_expression_pattern.match(expression)

    if match is None:
        return False

    # Check if the whole expression was matched against
    return expression == match.group(0)


def parse_matrix_expression(expression: str) -> MatrixParseList:
    """Parse the matrix expression and return a list of results.

    The return value is a list of results. This results list contains lists of tuples.
    The top list is the expressions that should be added together, and each sublist
    is expressions that should be multiplied together. These expressions to be
    multiplied are tuples, where each tuple is (multiplier, matrix identifier, index).
    The multiplier can be any real number, the matrix identifier is either a named
    matrix or a new rotation matrix declared with 'rot()', and the index is an
    integer or 'T' for transpose.

    :param str expression: The expression to be parsed
    :returns MatrixParseTuple: A list of results
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
            for t in re.findall(r'(-?\d+\.?\d*)?([A-Z]|rot\(-?\d+\.?\d*\))(\^{(-?\d+|T)})?', group)
        ]
        # We just split the expression by '+' to have separate groups
        for group in expression.split('+')
    ]
