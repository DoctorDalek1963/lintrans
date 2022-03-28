# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This simple module provides a :class:`MatrixExpressionValidator` class to validate matrix expression input."""

from __future__ import annotations

import re

from PyQt5.QtGui import QValidator

from lintrans.matrices import parse


class MatrixExpressionValidator(QValidator):
    """This class validates matrix expressions in a Qt input box."""

    def validate(self, text: str, pos: int) -> tuple[QValidator.State, str, int]:
        """Validate the given text according to the rules defined in the :mod:`lintrans.matrices` module."""
        clean_text = re.sub(r'[\sA-Z\d.rot()^{},+-]', '', text)

        if clean_text == '':
            if parse.validate_matrix_expression(clean_text):
                return QValidator.Acceptable, text, pos
            else:
                return QValidator.Intermediate, text, pos

        return QValidator.Invalid, text, pos
