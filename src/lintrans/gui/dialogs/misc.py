# lintrans - The linear transformation visualizer
# Copyright (C) 2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides miscellaneous dialog classes like :class:`AboutDialog`."""

from __future__ import annotations

import os
import platform
from typing import List, Tuple, Union

from PyQt5.QtCore import PYQT_VERSION_STR, QT_VERSION_STR, Qt, pyqtSlot
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QDialog, QFileDialog, QGridLayout, QHBoxLayout, QLabel, QPushButton,
                             QShortcut, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

import lintrans
from lintrans.gui.plots import DefinePolygonWidget
from lintrans.matrices import MatrixWrapper
from lintrans.matrices.utility import round_float
from lintrans.typing_ import MatrixType, is_matrix_type


class FixedSizeDialog(QDialog):
    """A simple superclass to create modal dialog boxes with fixed size.

    We override the :meth:`open` method to set the fixed size as soon as the dialog is opened modally.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Set the :cpp:enum:`Qt::WA_DeleteOnClose` attribute to ensure deletion of dialog."""
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

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
            "It's designed for teachers and students and all feedback<br>"
            'is greatly appreciated. Go to <em>Help</em> &gt; <em>Give feedback</em><br>'
            'to report a bug or suggest a new feature, or you can<br>email me directly at '
            '<a href="mailto:dyson.dyson@icloud.com" style="color: black;">dyson.dyson@icloud.com</a>.'
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

        self.setWindowTitle('Defined matrices')

        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        bold_font = self.font()
        bold_font.setBold(True)

        name_value_pair: tuple[str, Union[MatrixType, str]]

        # Each defined matrix will get a widget group. Each group will be a label for the name,
        # a label for '=', and a container widget to either show the matrix numerically, or to
        # show the expression that it's defined as
        for i, name_value_pair in enumerate(matrix_wrapper.get_defined_matrices()):
            name, value = name_value_pair

            # Create all the widgets first
            label_name = QLabel(self)
            label_name.setText(name)
            label_name.setFont(bold_font)

            label_equals = QLabel(self)
            label_equals.setText('=')

            widget_matrix = self._get_matrix_widget(value)

            # We want columns of at most 6 widget groups
            # This column variable manages which column of defined matrices we're on
            # It's multiplied by 3 because all the widgets are in a single grid layout
            # I could factor out each triplet of widgets for a defined matrix into a container widget,
            # but I prefer to keep the widget count lower to reduce any possible lag
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

            # The parens need to be bigger than the numbers, but increasing the font size also
            # makes the font thicker, so we have to reduce the font weight by the same factor
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


class FileSelectDialog(QFileDialog):
    """A subclass of :class:`QFileDialog` that fixes an issue with the default suffix on UNIX platforms."""

    def selectedFiles(self) -> List[str]:
        """Return a list of strings containing the absolute paths of the selected files in the dialog.

        There is an issue on UNIX platforms where a hidden directory will be recognised as a suffix.
        For example, ``/home/dyson/.lintrans/saves/test`` should have ``.lt`` appended, but
        ``.lintrans/saves/test`` gets recognised as the suffix, so the default suffix is not added.

        To fix this, we just look at the basename and see if it needs a suffix added. We do this for
        every name in the list, but there should be just one name, since this class is only intended
        to be used for saving files. We still return the full list of filenames.
        """
        selected_files: List[str] = []

        for filename in super().selectedFiles():
            # path will be the full path of the file, without the extension
            # This method understands hidden directories on UNIX platforms
            path, ext = os.path.splitext(filename)

            if ext == '':
                ext = '.' + self.defaultSuffix()

            selected_files.append(''.join((path, ext)))

        return selected_files


class DefinePolygonDialog(FixedSizeDialog):
    """This dialog class allows the use to define a polygon with :class:`DefinePolygonWidget`."""

    def __init__(self, *args, polygon_points: List[Tuple[float, float]], **kwargs) -> None:
        """Create the dialog with the :class:`DefinePolygonWidget` widget."""
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Define a polygon')
        self.setMinimumSize(700, 550)

        self.polygon_points = polygon_points

        # === Create the widgets

        self._polygon_widget = DefinePolygonWidget(polygon_points=polygon_points)

        button_confirm = QPushButton(self)
        button_confirm.setText('Confirm')
        button_confirm.clicked.connect(self._confirm_polygon)
        button_confirm.setToolTip('Confirm this polygon<br><b>(Ctrl + Enter)</b>')
        QShortcut(QKeySequence('Ctrl+Return'), self).activated.connect(button_confirm.click)

        button_cancel = QPushButton(self)
        button_cancel.setText('Cancel')
        button_cancel.clicked.connect(self.reject)
        button_cancel.setToolTip('Discard this polygon<br><b>(Escape)</b>')

        button_reset = QPushButton(self)
        button_reset.setText('Reset polygon')
        button_reset.clicked.connect(self._polygon_widget.reset_polygon)
        button_reset.setToolTip('Remove all points of the polygon<br><b>(Ctrl + R)</b>')
        QShortcut(QKeySequence('Ctrl+R'), self).activated.connect(button_reset.click)

        # === Arrange the widgets

        self.setContentsMargins(10, 10, 10, 10)

        hlay_buttons = QHBoxLayout()
        hlay_buttons.setSpacing(20)
        hlay_buttons.addWidget(button_reset)
        hlay_buttons.addItem(QSpacerItem(50, 5, hPolicy=QSizePolicy.Expanding, vPolicy=QSizePolicy.Minimum))
        hlay_buttons.addWidget(button_cancel)
        hlay_buttons.addWidget(button_confirm)

        vlay = QVBoxLayout()
        vlay.setSpacing(20)
        vlay.addWidget(self._polygon_widget)
        vlay.addLayout(hlay_buttons)

        self.setLayout(vlay)

    @pyqtSlot()
    def _confirm_polygon(self) -> None:
        """Confirm the polygon that the user has defined."""
        self.polygon_points = self._polygon_widget.points
        self.accept()
