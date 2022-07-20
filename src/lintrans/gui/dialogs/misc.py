#  lintrans - The linear transformation visualizer
#  Copyright (C) 2022 D. Dyson (DoctorDalek1963)
#
#  This program is licensed under GNU GPLv3, available here:
#  <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides miscellaneous dialog classes like :class:`AboutDialog`."""

from __future__ import annotations

import platform
from typing import Union

from PyQt5.QtCore import PYQT_VERSION_STR, QT_VERSION_STR, Qt
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QVBoxLayout, QWidget

import lintrans
from lintrans.matrices.utility import round_float
from lintrans.matrices import MatrixWrapper
from lintrans.typing_ import is_matrix_type, MatrixType


class FixedSizeDialog(QDialog):
    """A simple superclass to create modal dialog boxes with fixed size.

    We override the :meth:`open` method to set the fixed size as soon as the dialog is opened modally.
    """

    def open(self) -> None:
        """Override :meth:`QDialog.open` to set the dialog to a fixed size."""
        super().open()
        self.setFixedSize(self.size())


class AboutDialog(FixedSizeDialog):
    """A simple dialog class to display information about the app to the user.

    It only has an :meth:`__init__` method because it only has label widgets, so no other methods are necessary here.
    """

    def __init__(self, *args, **kwargs):
        """Create an :class:`AboutDialog` object with all the label widgets."""
        super().__init__(*args, **kwargs)

        self.setWindowTitle('About lintrans')

        # === Create the widgets

        label_title = QLabel(self)
        label_title.setText(f'lintrans (version {lintrans.__version__})')
        label_title.setAlignment(Qt.AlignCenter)

        font_title = label_title.font()
        font_title.setPointSize(font_title.pointSize() * 2)
        label_title.setFont(font_title)

        label_version_info = QLabel(self)
        label_version_info.setText(
            f'With Python version {platform.python_version()}\n'
            f'Qt version {QT_VERSION_STR} and PyQt5 version {PYQT_VERSION_STR}\n'
            f'Running on {platform.platform()}'
        )
        label_version_info.setAlignment(Qt.AlignCenter)

        label_info = QLabel(self)
        label_info.setText(
            'lintrans is a program designed to help visualise<br>'
            '2D linear transformations represented with matrices.<br><br>'
            "It's designed for teachers and students and any feedback<br>"
            'is greatly appreciated at <a href="https://github.com/DoctorDalek1963/lintrans" '
            'style="color: black;">my GitHub page</a><br>or via email '
            '(<a href="mailto:dyson.dyson@icloud.com" style="color: black;">dyson.dyson@icloud.com</a>).'
        )
        label_info.setAlignment(Qt.AlignCenter)
        label_info.setTextFormat(Qt.RichText)
        label_info.setOpenExternalLinks(True)

        label_copyright = QLabel(self)
        label_copyright.setText(
            'This program is free software.<br>Copyright 2021-2022 D. Dyson (DoctorDalek1963).<br>'
            'This program is licensed under GPLv3, which can be found '
            '<a href="https://www.gnu.org/licenses/gpl-3.0.html" style="color: black;">here</a>.'
        )
        label_copyright.setAlignment(Qt.AlignCenter)
        label_copyright.setTextFormat(Qt.RichText)
        label_copyright.setOpenExternalLinks(True)

        # === Arrange the widgets

        self.setContentsMargins(10, 10, 10, 10)

        vlay = QVBoxLayout()
        vlay.setSpacing(20)
        vlay.addWidget(label_title)
        vlay.addWidget(label_version_info)
        vlay.addWidget(label_info)
        vlay.addWidget(label_copyright)

        self.setLayout(vlay)


class InfoPanelDialog(FixedSizeDialog):
    """A simple dialog class to display an info panel that shows all currently defined matrices."""

    def __init__(self, matrix_wrapper: MatrixWrapper, *args, **kwargs):
        """Create the dialog box with all the widgets needed to show the information."""
        super().__init__(*args, **kwargs)
        self.wrapper = matrix_wrapper

        self.setWindowTitle('Defined matrices')

        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        bold_font = self.font()
        bold_font.setBold(True)

        name_value_pair: tuple[str, Union[MatrixType, str]]

        for i, name_value_pair in enumerate(self.wrapper.get_defined_matrices()):
            name, value = name_value_pair

            label_name = QLabel(self)
            label_name.setText(name)
            label_name.setFont(bold_font)

            label_equals = QLabel(self)
            label_equals.setText('=')

            widget_matrix = self._get_matrix_widget(value)

            column = 3 * (i // 6)

            grid_layout.addWidget(
                label_name,
                i - 2 * column,
                column,
                Qt.AlignCenter
            )
            grid_layout.addWidget(
                label_equals,
                i - 2 * column,
                column + 1,
                Qt.AlignCenter
            )
            grid_layout.addWidget(
                widget_matrix,
                i - 2 * column,
                column + 2,
                Qt.AlignCenter
            )

        self.setContentsMargins(10, 10, 10, 10)
        self.setLayout(grid_layout)

    def _get_matrix_widget(self, matrix: Union[MatrixType, str]) -> QWidget:
        """Return a :class:`QWidget` containing the value of the matrix.

        If the matrix is defined as an expression, it will be a simple :class:`QLabel`.
        If the matrix is defined as a matrix, it will be a :class:`QWidget` container
        with multiple :class:`QLabel` objects in it.
        """
        if isinstance(matrix, str):
            label = QLabel(self)
            label.setText(matrix)
            return label

        elif is_matrix_type(matrix):
            # tl = top left, br = bottom right, etc.
            label_tl = QLabel(self)
            label_tl.setText(round_float(matrix[0][0]))

            label_tr = QLabel(self)
            label_tr.setText(round_float(matrix[0][1]))

            label_bl = QLabel(self)
            label_bl.setText(round_float(matrix[1][0]))

            label_br = QLabel(self)
            label_br.setText(round_float(matrix[1][1]))

            font_parens = self.font()
            font_parens.setPointSize(int(font_parens.pointSize() * 2.5))
            font_parens.setWeight(int(font_parens.weight() / 2.5))

            label_paren_left = QLabel(self)
            label_paren_left.setText('(')
            label_paren_left.setFont(font_parens)

            label_paren_right = QLabel(self)
            label_paren_right.setText(')')
            label_paren_right.setFont(font_parens)

            container = QWidget(self)
            grid_layout = QGridLayout()

            grid_layout.addWidget(label_paren_left, 0, 0, -1, 1)
            grid_layout.addWidget(label_tl, 0, 1)
            grid_layout.addWidget(label_tr, 0, 2)
            grid_layout.addWidget(label_bl, 1, 1)
            grid_layout.addWidget(label_br, 1, 2)
            grid_layout.addWidget(label_paren_right, 0, 3, -1, 1)

            container.setLayout(grid_layout)

            return container

        raise ValueError('Matrix was not MatrixType or str')
