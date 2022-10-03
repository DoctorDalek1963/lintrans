# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides miscellaneous dialog classes like :class:`AboutDialog`."""

from __future__ import annotations

import os
import platform
from typing import Dict, List, Optional, Tuple, Union

from PyQt5.QtCore import PYQT_VERSION_STR, QT_VERSION_STR, Qt, pyqtSlot
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QDialog, QFileDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QPushButton,
                             QRadioButton, QShortcut, QSizePolicy, QSpacerItem, QStackedLayout, QVBoxLayout, QWidget)

import lintrans
from lintrans.global_settings import GlobalSettings
from lintrans.gui.plots import DefinePolygonWidget
from lintrans.matrices import MatrixWrapper
from lintrans.matrices.utility import round_float
from lintrans.typing_ import MatrixType, is_matrix_type
from lintrans.updating import update_lintrans_in_background


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
        self.matrix_wrapper = matrix_wrapper

        self._matrices: Dict[str, Optional[Union[MatrixType, str]]] = {
            name: value
            for name, value in self.matrix_wrapper.get_defined_matrices()
        }

        self.setWindowTitle('Defined matrices')
        self.setContentsMargins(10, 10, 10, 10)

        self._stacked_layout = QStackedLayout(self)
        self.setLayout(self._stacked_layout)

        self._draw_ui()

    def _draw_ui(self) -> None:
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        for i, (name, value) in enumerate(self._matrices.items()):
            if value is None:
                continue

            grid_layout.addWidget(
                self._get_full_matrix_widget(name, value),
                i % 4,
                i // 4,
                Qt.AlignCenter
            )

        container = QWidget(self)
        container.setLayout(grid_layout)
        self._stacked_layout.setCurrentIndex(self._stacked_layout.addWidget(container))

    def _undefine_matrix(self, name: str) -> None:
        """Undefine the given matrix and redraw the dialog."""
        for x in self.matrix_wrapper.undefine_matrix(name):
            self._matrices[x] = None

        self._draw_ui()

    def _get_full_matrix_widget(self, name: str, value: Union[MatrixType, str]) -> QWidget:
        """Return a :class:`QWidget` containing the whole matrix widget composition.

        Each defined matrix will get a widget group. Each group will be a label for the name,
        a label for '=', and a container widget to either show the matrix numerically, or to
        show the expression that it's defined as.

        See :meth:`_get_matrix_data_widget`.
        """
        bold_font = self.font()
        bold_font.setBold(True)

        label_name = QLabel(self)
        label_name.setText(name)
        label_name.setFont(bold_font)

        widget_matrix = self._get_matrix_data_widget(value)

        hlay = QHBoxLayout()
        hlay.setSpacing(10)
        hlay.addWidget(label_name)
        hlay.addWidget(QLabel('=', self))
        hlay.addWidget(widget_matrix)

        vlay = QVBoxLayout()
        vlay.setSpacing(10)
        vlay.addLayout(hlay)

        if name != 'I':
            button_undefine = QPushButton(self)
            button_undefine.setText('Undefine')
            button_undefine.clicked.connect(lambda: self._undefine_matrix(name))

            vlay.addWidget(button_undefine)

        groupbox = QGroupBox(self)
        groupbox.setContentsMargins(10, 10, 10, 10)
        groupbox.setLayout(vlay)

        lay = QVBoxLayout()
        lay.setSpacing(0)
        lay.addWidget(groupbox)

        container = QWidget(self)
        container.setLayout(lay)

        return container

    def _get_matrix_data_widget(self, matrix: Union[MatrixType, str]) -> QWidget:
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


class PromptUpdateDialog(FixedSizeDialog):
    """A simple dialog to ask the user if they want to upgrade their lintrans installation."""

    def __init__(self, *args, new_version: str, **kwargs) -> None:
        """Create the dialog with all its widgets."""
        super().__init__(*args, **kwargs)

        if new_version.startswith('v'):
            new_version = new_version[1:]

        self.setWindowTitle('Update available')

        # === Create the widgets

        label_info = QLabel(self)
        label_info.setText(
            'A new version of lintrans is available!\n'
            f'({lintrans.__version__} -> {new_version})\n\n'
            'Would you like to update now?'
        )
        label_info.setAlignment(Qt.AlignCenter)

        label_explanation = QLabel(self)
        label_explanation.setText(
            'The update will run silently in the background, so you can keep using lintrans uninterrupted.\n'
            f'You can change your choice at any time by editing {GlobalSettings().get_settings_file()}'
        )
        label_explanation.setAlignment(Qt.AlignCenter)

        font = label_explanation.font()
        font.setPointSize(int(0.9 * font.pointSize()))
        font.setItalic(True)
        label_explanation.setFont(font)

        groupbox_radio_buttons = QGroupBox(self)

        self._radio_button_auto = QRadioButton('Always update automatically', groupbox_radio_buttons)
        self._radio_button_prompt = QRadioButton('Always ask to update', groupbox_radio_buttons)
        self._radio_button_never = QRadioButton('Never update', groupbox_radio_buttons)

        # If this prompt is even appearing, then the update type must be 'prompt'
        self._radio_button_prompt.setChecked(True)

        button_remind_me_later = QPushButton('Remind me later', self)
        button_remind_me_later.clicked.connect(lambda: self._save_choice_and_update(False))
        button_remind_me_later.setShortcut(Qt.Key_Escape)
        button_remind_me_later.setFocus()

        button_update_now = QPushButton('Update now', self)
        button_update_now.clicked.connect(lambda: self._save_choice_and_update(True))

        # === Arrange the widgets

        self.setContentsMargins(10, 10, 10, 10)

        hlay_buttons = QHBoxLayout()
        hlay_buttons.setSpacing(20)
        hlay_buttons.addWidget(button_remind_me_later)
        hlay_buttons.addWidget(button_update_now)

        vlay = QVBoxLayout()
        vlay.setSpacing(20)
        vlay.addWidget(label_info)

        vlay_radio_buttons = QVBoxLayout()
        vlay_radio_buttons.setSpacing(10)
        vlay_radio_buttons.addWidget(self._radio_button_auto)
        vlay_radio_buttons.addWidget(self._radio_button_prompt)
        vlay_radio_buttons.addWidget(self._radio_button_never)

        groupbox_radio_buttons.setLayout(vlay_radio_buttons)

        vlay.addWidget(groupbox_radio_buttons)
        vlay.addWidget(label_explanation)
        vlay.addLayout(hlay_buttons)

        self.setLayout(vlay)

    def _save_choice_and_update(self, update_now: bool) -> None:
        """Save the user's choice of how to update and optionally trigger an update now."""
        gs = GlobalSettings()
        if self._radio_button_auto.isChecked():
            gs.set_update_type(gs.UpdateType.auto)

        elif self._radio_button_prompt.isChecked():
            gs.set_update_type(gs.UpdateType.prompt)

        elif self._radio_button_never.isChecked():
            gs.set_update_type(gs.UpdateType.never)

        if update_now:
            # We don't need to check because we'll only get here if we know a new version is available
            update_lintrans_in_background(check=False)
            self.accept()
        else:
            self.reject()
