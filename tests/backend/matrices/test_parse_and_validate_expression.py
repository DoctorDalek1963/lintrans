# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""Test the :mod:`matrices.parse` module validation and parsing."""

from typing import List, Tuple

import pytest

from lintrans.matrices.parse import (MatrixParseError, find_sub_expressions, get_matrix_identifiers,
                                     parse_matrix_expression, validate_matrix_expression)
from lintrans.typing_ import MatrixParseList

expected_sub_expressions: List[Tuple[str, List[str]]] = [
    ('2(AB)^-1', ['AB']),
    ('-3(A+B)^2-C(B^TA)^-1', ['A+B', 'B^TA']),
    ('rot(45)', []),
    ('()', []),
    ('(())', ['()']),
    ('2.3A^-1(AB)^-1+(BC)^2', ['AB', 'BC']),
    ('(2.3A^-1(AB)^-1+(BC)^2)', ['2.3A^-1(AB)^-1+(BC)^2']),
]


def test_find_sub_expressions() -> None:
    """Test the :func:`lintrans.matrices.parse.find_sub_expressions` function."""
    for inp, output in expected_sub_expressions:
        assert find_sub_expressions(inp) == output


valid_inputs: List[str] = [
    'A', 'AB', '3A', '1.2A', '-3.4A', 'A^2', 'A^-1', 'A^{-1}',
    'A^12', 'A^T', 'A^{5}', 'A^{T}', '4.3A^7', '9.2A^{18}', '0.1A'

    'rot(45)', 'rot(12.5)', '3rot(90)',
    'rot(135)^3', 'rot(51)^T', 'rot(-34)^-1',

    'A+B', 'A+2B', '4.3A+9B', 'A^2+B^T', '3A^7+0.8B^{16}',
    'A-B', '3A-4B', '3.2A^3-16.79B^T', '4.752A^{17}-3.32B^{36}',
    'A-1B', '-A', '-1A', 'A^{2}3.4B', 'A^{-1}2.3B',

    '3A4B', 'A^TB', 'A^{T}B', '4A^6B^3',
    '2A^{3}4B^5', '4rot(90)^3', 'rot(45)rot(13)',
    'Arot(90)', 'AB^2', 'A^2B^2', '8.36A^T3.4B^12',

    '3.5A^{4}5.6rot(19.2)^T-B^{-1}4.1C^5',

    '(A)', '(AB)^-1', '2.3(3B^TA)^2', '-3.4(9D^{2}3F^-1)^T+C', '(AB)(C)',
    '3(rot(34)^-7A)^-1+B', '3A^2B+4A(B+C)^-1D^T-A(C(D+E)B)'
]

invalid_inputs: List[str] = [
    '', 'rot()', 'A^', 'A^1.2', 'A^2 3.4B', 'A^23.4B', 'A^-1 2.3B', 'A^{3.4}', '1,2A', 'ro(12)', '5', '12^2',
    '^T', '^{12}', '.1A', 'A^{13', 'A^3}', 'A^A', '^2', 'A--B', '--A', '+A', '--1A', 'A--B', 'A--1B',
    '.A', '1.A', '2.3AB)^T', '(AB+)', '-4.6(9A', '-2(3.4A^{-1}-C^)^2', '9.2)', '3A^2B+4A(B+C)^-1D^T-A(C(D+EB)',
    '3()^2', '4(your mum)^T', 'rot()', 'rot(10.1.1)', 'rot(--2)',

    'This is 100% a valid matrix expression, I swear'
]


@pytest.mark.parametrize('inputs,output', [(valid_inputs, True), (invalid_inputs, False)])
def test_validate_matrix_expression(inputs: List[str], output: bool) -> None:
    """Test the validate_matrix_expression() function."""
    for inp in inputs:
        assert validate_matrix_expression(inp) == output


expressions_and_parsed_expressions: List[Tuple[str, MatrixParseList]] = [
    # Simple expressions
    ('A', [[('', 'A', '')]]),
    ('A^2', [[('', 'A', '2')]]),
    ('A^{2}', [[('', 'A', '2')]]),
    ('3A', [[('3', 'A', '')]]),
    ('1.4A^3', [[('1.4', 'A', '3')]]),
    ('0.1A', [[('0.1', 'A', '')]]),
    ('0.1A', [[('0.1', 'A', '')]]),
    ('A^12', [[('', 'A', '12')]]),
    ('A^234', [[('', 'A', '234')]]),

    # Multiplications
    ('A 0.1B', [[('', 'A', ''), ('0.1', 'B', '')]]),
    ('A^2 3B', [[('', 'A', '23'), ('', 'B', '')]]),
    ('A^{2}3.4B', [[('', 'A', '2'), ('3.4', 'B', '')]]),
    ('4A^{3} 6B^2', [[('4', 'A', '3'), ('6', 'B', '2')]]),
    ('4.2A^{T} 6.1B^-1', [[('4.2', 'A', 'T'), ('6.1', 'B', '-1')]]),
    ('-1.2A^2 rot(45)^2', [[('-1.2', 'A', '2'), ('', 'rot(45)', '2')]]),
    ('3.2A^T 4.5B^{5} 9.6rot(121.3)', [[('3.2', 'A', 'T'), ('4.5', 'B', '5'), ('9.6', 'rot(121.3)', '')]]),
    ('-1.18A^{-2} 0.1B^{2} 9rot(-34.6)^-1', [[('-1.18', 'A', '-2'), ('0.1', 'B', '2'), ('9', 'rot(-34.6)', '-1')]]),

    # Additions
    ('A + B', [[('', 'A', '')], [('', 'B', '')]]),
    ('A + B - C', [[('', 'A', '')], [('', 'B', '')], [('-1', 'C', '')]]),
    ('A^2 + 0.5B', [[('', 'A', '2')], [('0.5', 'B', '')]]),
    ('2A^3 + 8B^T - 3C^-1', [[('2', 'A', '3')], [('8', 'B', 'T')], [('-3', 'C', '-1')]]),
    ('4.9A^2 - 3rot(134.2)^-1 + 7.6B^8', [[('4.9', 'A', '2')], [('-3', 'rot(134.2)', '-1')], [('7.6', 'B', '8')]]),

    # Additions with multiplication
    ('2.14A^{3} 4.5rot(14.5)^-1 + 8B^T - 3C^-1', [[('2.14', 'A', '3'), ('4.5', 'rot(14.5)', '-1')],
                                                  [('8', 'B', 'T')], [('-3', 'C', '-1')]]),
    ('2.14A^{3} 4.5rot(14.5)^-1 + 8.5B^T 5.97C^14 - 3.14D^{-1} 6.7E^T',
     [[('2.14', 'A', '3'), ('4.5', 'rot(14.5)', '-1')], [('8.5', 'B', 'T'), ('5.97', 'C', '14')],
      [('-3.14', 'D', '-1'), ('6.7', 'E', 'T')]]),

    # Parenthesized expressions
    ('(AB)^-1', [[('', 'AB', '-1')]]),
    ('-3(A+B)^2-C(B^TA)^-1', [[('-3', 'A+B', '2')], [('-1', 'C', ''), ('', 'B^{T}A', '-1')]]),
    ('2.3(3B^TA)^2', [[('2.3', '3B^{T}A', '2')]]),
    ('-3.4(9D^{2}3F^-1)^T+C', [[('-3.4', '9D^{2}3F^{-1}', 'T')], [('', 'C', '')]]),
    ('2.39(3.1A^{-1}2.3B(CD)^-1)^T + (AB^T)^-1', [[('2.39', '3.1A^{-1}2.3B(CD)^{-1}', 'T')], [('', 'AB^{T}', '-1')]])
]


def test_parse_matrix_expression() -> None:
    """Test the parse_matrix_expression() function."""
    for expression, parsed_expression in expressions_and_parsed_expressions:
        # Test it with and without whitespace
        assert parse_matrix_expression(expression) == parsed_expression
        assert parse_matrix_expression(expression.replace(' ', '')) == parsed_expression

    for expression in valid_inputs:
        # Assert that it doesn't raise MatrixParseError
        parse_matrix_expression(expression)


def test_parse_error() -> None:
    """Test that parse_matrix_expression() raises a MatrixParseError."""
    for expression in invalid_inputs:
        with pytest.raises(MatrixParseError):
            parse_matrix_expression(expression)


def test_get_matrix_identifiers() -> None:
    """Test that matrix identifiers can be properly found."""
    assert get_matrix_identifiers('M^T') == {'M'}
    assert get_matrix_identifiers('ABCDEF') == {'A', 'B', 'C', 'D', 'E', 'F'}
    assert get_matrix_identifiers('AB^{-1}3Crot(45)2A(B^2C^-1)') == {'A', 'B', 'C'}
    assert get_matrix_identifiers('A^{2}3A^-1A^TA') == {'A'}
    assert get_matrix_identifiers('rot(45)(rot(25)rot(20))^2') == set()

    for expression in invalid_inputs:
        with pytest.raises(MatrixParseError):
            get_matrix_identifiers(expression)
