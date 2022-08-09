# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This simple module provides a :class:`MatrixExpressionValidator` class to validate matrix expression input."""

from __future__ import annotations

import re
from typing import Tuple

from PyQt5.QtGui import QValidator

from lintrans.matrices import parse


class MatrixExpressionValidator(QValidator):
    """This class validates matrix expressions in a Qt input box."""

    def validate(self, text: str, pos: int) -> Tuple[QValidator.State, str, int]:
        """Validate the given text according to the rules defined in the :mod:`lintrans.matrices` module."""
        # We want to extend the naive character class by adding a comma, which isn't
        # normally allowed in expressions, but is allowed for sequential animations
        bad_chars = re.sub(parse.NAIVE_CHARACTER_CLASS[:-1] + ',]', '', text)

        # If there are bad chars, just reject it
        if bad_chars != '':
            return QValidator.Invalid, text, pos

        # Now we need to check if it's actually a valid expression
        if all(parse.validate_matrix_expression(expression) for expression in text.split(',')):
            return QValidator.Acceptable, text, pos

        # Else, if it's got all the right characters but it's not a valid expression
        return QValidator.Intermediate, text, pos
