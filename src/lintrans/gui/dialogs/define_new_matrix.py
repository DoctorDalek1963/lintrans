# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides an abstract :class:`DefineDialog` class and subclasses, allowing definition of new matrices."""

from __future__ import annotations

import abc

from numpy import array
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QDoubleValidator, QKeySequence
from PyQt5.QtWidgets import (QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QShortcut, QSizePolicy, QSpacerItem, QVBoxLayout)

from lintrans.gui.dialogs.misc import FixedSizeDialog
from lintrans.gui.plots import DefineVisuallyWidget
from lintrans.gui.settings import DisplaySettings
from lintrans.gui.validate import MatrixExpressionValidator
from lintrans.matrices import MatrixWrapper
from lintrans.matrices.utility import is_valid_float, round_float
from lintrans.typing_ import MatrixType

_ALPHABET_NO_I = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'


class DefineDialog(FixedSizeDialog):
    """An abstract superclass for definitions dialogs.

    .. warning:: This class should never be directly instantiated, only subclassed.

    .. note::
       I would make this class have ``metaclass=abc.ABCMeta``, but I can't because it subclasses :class:`QDialog`,
       and every superclass of a class must have the same metaclass, and :class:`QDialog` is not an abstract class.
    """

    def __init__(self, *args, matrix_wrapper: MatrixWrapper, **kwargs):
        """Create the widgets and layout of the dialog.

        .. note:: ``*args`` and ``**kwargs`` are passed to the super constructor (:class:`QDialog`).

        :param MatrixWrapper matrix_wrapper: The MatrixWrapper that this dialog will mutate
        """
        super().__init__(*args, **kwargs)

        self.matrix_wrapper = matrix_wrapper
        self.setWindowTitle('Define a matrix')

        # === Create the widgets

        self._button_confirm = QPushButton(self)
        self._button_confirm.setText('Confirm')
        self._button_confirm.setEnabled(False)
        self._button_confirm.clicked.connect(self._confirm_matrix)
        self._button_confirm.setToolTip('Confirm this as the new matrix<br><b>(Ctrl + Enter)</b>')
        QShortcut(QKeySequence('Ctrl+Return'), self).activated.connect(self._button_confirm.click)

        button_cancel = QPushButton(self)
        button_cancel.setText('Cancel')
        button_cancel.clicked.connect(self.reject)
        button_cancel.setToolTip('Cancel this definition<br><b>(Escape)</b>')

        label_equals = QLabel(self)
        label_equals.setText('=')

        self._combobox_letter = QtWidgets.QComboBox(self)

        for letter in _ALPHABET_NO_I:
            self._combobox_letter.addItem(letter)

        self._combobox_letter.activated.connect(self._load_matrix)

        # === Arrange the widgets

        self.setContentsMargins(10, 10, 10, 10)

        self._hlay_buttons = QHBoxLayout()
        self._hlay_buttons.setSpacing(20)
        self._hlay_buttons.addItem(QSpacerItem(50, 5, hPolicy=QSizePolicy.Expanding, vPolicy=QSizePolicy.Minimum))
        self._hlay_buttons.addWidget(button_cancel)
        self._hlay_buttons.addWidget(self._button_confirm)

        self._hlay_definition = QHBoxLayout()
        self._hlay_definition.setSpacing(20)
        self._hlay_definition.addWidget(self._combobox_letter)
        self._hlay_definition.addWidget(label_equals)

        # All subclasses have to manually add the hlay layouts to _vlay_all
        # This is because the subclasses add their own widgets and if we add
        # the layout here, then these new widgets won't be included
        self._vlay_all = QVBoxLayout()
        self._vlay_all.setSpacing(20)

        self.setLayout(self._vlay_all)

    @property
    def _selected_letter(self) -> str:
        """Return the letter currently selected in the combo box."""
        return str(self._combobox_letter.currentText())

    @abc.abstractmethod
    @pyqtSlot()
    def _update_confirm_button(self) -> None:
        """Enable the confirm button if it should be enabled, else, disable it."""

    @pyqtSlot(int)
    def _load_matrix(self, index: int) -> None:
        """Load the selected matrix into the dialog.

        This method is optionally able to be overridden. If it is not overridden,
        then no matrix is loaded when selecting a name.

        We have this method in the superclass so that we can define it as the slot
        for the :meth:`QComboBox.activated` signal in this constructor, rather than
        having to define that in the constructor of every subclass.
        """

    @abc.abstractmethod
    @pyqtSlot()
    def _confirm_matrix(self) -> None:
        """Confirm the inputted matrix and assign it.

        .. note:: When subclassing, this method should mutate ``self.matrix_wrapper`` and then call ``self.accept()``.
        """


class DefineVisuallyDialog(DefineDialog):
    """The dialog class that allows the user to define a matrix visually."""

    def __init__(self, *args, matrix_wrapper: MatrixWrapper, display_settings: DisplaySettings, **kwargs):
        """Create the widgets and layout of the dialog.

        :param MatrixWrapper matrix_wrapper: The MatrixWrapper that this dialog will mutate
        """
        super().__init__(*args, matrix_wrapper=matrix_wrapper, **kwargs)

        self.setMinimumSize(700, 550)

        # === Create the widgets

        self._plot = DefineVisuallyWidget(self, display_settings=display_settings)

        # === Arrange the widgets

        self._hlay_definition.addWidget(self._plot)
        self._hlay_definition.setStretchFactor(self._plot, 1)

        self._vlay_all.addLayout(self._hlay_definition)
        self._vlay_all.addLayout(self._hlay_buttons)

        # We load the default matrix A into the plot
        self._load_matrix(0)

        # We also enable the confirm button, because any visually defined matrix is valid
        self._button_confirm.setEnabled(True)

    @pyqtSlot()
    def _update_confirm_button(self) -> None:
        """Enable the confirm button.

        .. note::
           The confirm button is always enabled in this dialog and this method is never actually used,
           so it's got an empty body. It's only here because we need to implement the abstract method.
        """

    @pyqtSlot(int)
    def _load_matrix(self, index: int) -> None:
        """Show the selected matrix on the plot. If the matrix is None, show the identity."""
        matrix = self.matrix_wrapper[self._selected_letter]

        if matrix is None:
            matrix = self.matrix_wrapper['I']

        self._plot.plot_matrix(matrix)
        self._plot.update()

    @pyqtSlot()
    def _confirm_matrix(self) -> None:
        """Confirm the matrix that's been defined visually."""
        matrix: MatrixType = array([
            [self._plot.point_i[0], self._plot.point_j[0]],
            [self._plot.point_i[1], self._plot.point_j[1]]
        ])

        self.matrix_wrapper[self._selected_letter] = matrix
        self.accept()


class DefineNumericallyDialog(DefineDialog):
    """The dialog class that allows the user to define a new matrix numerically."""

    def __init__(self, *args, matrix_wrapper: MatrixWrapper, **kwargs):
        """Create the widgets and layout of the dialog.

        :param MatrixWrapper matrix_wrapper: The MatrixWrapper that this dialog will mutate
        """
        super().__init__(*args, matrix_wrapper=matrix_wrapper, **kwargs)

        # === Create the widgets

        # tl = top left, br = bottom right, etc.
        self._element_tl = QLineEdit(self)
        self._element_tl.textChanged.connect(self._update_confirm_button)
        self._element_tl.setValidator(QDoubleValidator())

        self._element_tr = QLineEdit(self)
        self._element_tr.textChanged.connect(self._update_confirm_button)
        self._element_tr.setValidator(QDoubleValidator())

        self._element_bl = QLineEdit(self)
        self._element_bl.textChanged.connect(self._update_confirm_button)
        self._element_bl.setValidator(QDoubleValidator())

        self._element_br = QLineEdit(self)
        self._element_br.textChanged.connect(self._update_confirm_button)
        self._element_br.setValidator(QDoubleValidator())

        self._matrix_elements = (self._element_tl, self._element_tr, self._element_bl, self._element_br)

        font_parens = self.font()
        font_parens.setPointSize(int(font_parens.pointSize() * 5))
        font_parens.setWeight(int(font_parens.weight() / 5))

        label_paren_left = QLabel(self)
        label_paren_left.setText('(')
        label_paren_left.setFont(font_parens)

        label_paren_right = QLabel(self)
        label_paren_right.setText(')')
        label_paren_right.setFont(font_parens)

        # === Arrange the widgets

        grid_matrix = QGridLayout()
        grid_matrix.setSpacing(20)
        grid_matrix.addWidget(label_paren_left, 0, 0, -1, 1)
        grid_matrix.addWidget(self._element_tl, 0, 1)
        grid_matrix.addWidget(self._element_tr, 0, 2)
        grid_matrix.addWidget(self._element_bl, 1, 1)
        grid_matrix.addWidget(self._element_br, 1, 2)
        grid_matrix.addWidget(label_paren_right, 0, 3, -1, 1)

        self._hlay_definition.addLayout(grid_matrix)

        self._vlay_all.addLayout(self._hlay_definition)
        self._vlay_all.addLayout(self._hlay_buttons)

        # We load the default matrix A into the boxes
        self._load_matrix(0)

        self._element_tl.setFocus()

    @pyqtSlot()
    def _update_confirm_button(self) -> None:
        """Enable the confirm button if there are valid floats in every box."""
        for elem in self._matrix_elements:
            if not is_valid_float(elem.text()):
                # If they're not all numbers, then we can't confirm it
                self._button_confirm.setEnabled(False)
                return

        # If we didn't find anything invalid
        self._button_confirm.setEnabled(True)

    @pyqtSlot(int)
    def _load_matrix(self, index: int) -> None:
        """If the selected matrix is defined, load its values into the boxes."""
        matrix = self.matrix_wrapper[self._selected_letter]

        if matrix is None:
            for elem in self._matrix_elements:
                elem.setText('')

        else:
            self._element_tl.setText(round_float(matrix[0][0]))
            self._element_tr.setText(round_float(matrix[0][1]))
            self._element_bl.setText(round_float(matrix[1][0]))
            self._element_br.setText(round_float(matrix[1][1]))

        self._update_confirm_button()

    @pyqtSlot()
    def _confirm_matrix(self) -> None:
        """Confirm the matrix in the boxes and assign it to the name in the combo box."""
        matrix: MatrixType = array([
            [float(self._element_tl.text()), float(self._element_tr.text())],
            [float(self._element_bl.text()), float(self._element_br.text())]
        ])

        self.matrix_wrapper[self._selected_letter] = matrix
        self.accept()


class DefineAsAnExpressionDialog(DefineDialog):
    """The dialog class that allows the user to define a matrix as an expression of other matrices."""

    def __init__(self, *args, matrix_wrapper: MatrixWrapper, **kwargs):
        """Create the widgets and layout of the dialog.

        :param MatrixWrapper matrix_wrapper: The MatrixWrapper that this dialog will mutate
        """
        super().__init__(*args, matrix_wrapper=matrix_wrapper, **kwargs)

        self.setMinimumWidth(450)

        # === Create the widgets

        self._lineedit_expression_box = QLineEdit(self)
        self._lineedit_expression_box.setPlaceholderText('Enter matrix expression...')
        self._lineedit_expression_box.textChanged.connect(self._update_confirm_button)
        self._lineedit_expression_box.setValidator(MatrixExpressionValidator())

        # === Arrange the widgets

        self._hlay_definition.addWidget(self._lineedit_expression_box)

        self._vlay_all.addLayout(self._hlay_definition)
        self._vlay_all.addLayout(self._hlay_buttons)

        # Load the matrix if it's defined as an expression
        self._load_matrix(0)

        self._lineedit_expression_box.setFocus()

    @pyqtSlot()
    def _update_confirm_button(self) -> None:
        """Enable the confirm button if the matrix expression is valid in the wrapper."""
        text = self._lineedit_expression_box.text()
        valid_expression = self.matrix_wrapper.is_valid_expression(text)

        self._button_confirm.setEnabled(valid_expression and self._selected_letter not in text)

    @pyqtSlot(int)
    def _load_matrix(self, index: int) -> None:
        """If the selected matrix is defined an expression, load that expression into the box."""
        if (expr := self.matrix_wrapper.get_expression(self._selected_letter)) is not None:
            self._lineedit_expression_box.setText(expr)
        else:
            self._lineedit_expression_box.setText('')

    @pyqtSlot()
    def _confirm_matrix(self) -> None:
        """Evaluate the matrix expression and assign its value to the name in the combo box."""
        self.matrix_wrapper[self._selected_letter] = self._lineedit_expression_box.text()
        self.accept()
