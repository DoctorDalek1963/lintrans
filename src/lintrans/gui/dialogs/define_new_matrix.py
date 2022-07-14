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
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QShortcut, QSizePolicy, QSpacerItem, QVBoxLayout

from lintrans.gui.dialogs.misc import FixedSizeDialog
from lintrans.gui.plots import DefineVisuallyWidget
from lintrans.gui.settings import DisplaySettings
from lintrans.gui.validate import MatrixExpressionValidator
from lintrans.matrices import MatrixWrapper
from lintrans.matrices.utility import is_valid_float, round_float
from lintrans.typing_ import MatrixType

ALPHABET_NO_I = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'


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

        self.button_confirm = QtWidgets.QPushButton(self)
        self.button_confirm.setText('Confirm')
        self.button_confirm.setEnabled(False)
        self.button_confirm.clicked.connect(self.confirm_matrix)
        self.button_confirm.setToolTip('Confirm this as the new matrix<br><b>(Ctrl + Enter)</b>')
        QShortcut(QKeySequence('Ctrl+Return'), self).activated.connect(self.button_confirm.click)

        self.button_cancel = QtWidgets.QPushButton(self)
        self.button_cancel.setText('Cancel')
        self.button_cancel.clicked.connect(self.reject)
        self.button_cancel.setToolTip('Cancel this definition<br><b>(Escape)</b>')

        self.label_equals = QtWidgets.QLabel()
        self.label_equals.setText('=')

        self.combobox_letter = QtWidgets.QComboBox(self)

        for letter in ALPHABET_NO_I:
            self.combobox_letter.addItem(letter)

        self.combobox_letter.activated.connect(self.load_matrix)

        # === Arrange the widgets

        self.setContentsMargins(10, 10, 10, 10)

        self.hlay_buttons = QHBoxLayout()
        self.hlay_buttons.setSpacing(20)
        self.hlay_buttons.addItem(QSpacerItem(50, 5, hPolicy=QSizePolicy.Expanding, vPolicy=QSizePolicy.Minimum))
        self.hlay_buttons.addWidget(self.button_cancel)
        self.hlay_buttons.addWidget(self.button_confirm)

        self.hlay_definition = QHBoxLayout()
        self.hlay_definition.setSpacing(20)
        self.hlay_definition.addWidget(self.combobox_letter)
        self.hlay_definition.addWidget(self.label_equals)

        self.vlay_all = QVBoxLayout()
        self.vlay_all.setSpacing(20)

        self.setLayout(self.vlay_all)

    @property
    def selected_letter(self) -> str:
        """Return the letter currently selected in the combo box."""
        return str(self.combobox_letter.currentText())

    @abc.abstractmethod
    @pyqtSlot()
    def update_confirm_button(self) -> None:
        """Enable the confirm button if it should be enabled, else, disable it."""

    @pyqtSlot(int)
    def load_matrix(self, index: int) -> None:
        """Load the selected matrix into the dialog.

        This method is optionally able to be overridden. If it is not overridden,
        then no matrix is loaded when selecting a name.

        We have this method in the superclass so that we can define it as the slot
        for the :meth:`QComboBox.activated` signal in this constructor, rather than
        having to define that in the constructor of every subclass.
        """

    @abc.abstractmethod
    @pyqtSlot()
    def confirm_matrix(self) -> None:
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

        self.plot = DefineVisuallyWidget(self, display_settings=display_settings)

        # === Arrange the widgets

        self.hlay_definition.addWidget(self.plot)
        self.hlay_definition.setStretchFactor(self.plot, 1)

        self.vlay_all.addLayout(self.hlay_definition)
        self.vlay_all.addLayout(self.hlay_buttons)

        # We load the default matrix A into the plot
        self.load_matrix(0)

        # We also enable the confirm button, because any visually defined matrix is valid
        self.button_confirm.setEnabled(True)

    @pyqtSlot()
    def update_confirm_button(self) -> None:
        """Enable the confirm button.

        .. note::
           The confirm button is always enabled in this dialog and this method is never actually used,
           so it's got an empty body. It's only here because we need to implement the abstract method.
        """

    @pyqtSlot(int)
    def load_matrix(self, index: int) -> None:
        """Show the selected matrix on the plot. If the matrix is None, show the identity."""
        matrix = self.matrix_wrapper[self.selected_letter]

        if matrix is None:
            matrix = self.matrix_wrapper['I']

        self.plot.visualize_matrix_transformation(matrix)
        self.plot.update()

    @pyqtSlot()
    def confirm_matrix(self) -> None:
        """Confirm the matrix that's been defined visually."""
        matrix: MatrixType = array([
            [self.plot.point_i[0], self.plot.point_j[0]],
            [self.plot.point_i[1], self.plot.point_j[1]]
        ])

        self.matrix_wrapper[self.selected_letter] = matrix
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
        self.element_tl = QtWidgets.QLineEdit(self)
        self.element_tl.textChanged.connect(self.update_confirm_button)
        self.element_tl.setValidator(QDoubleValidator())

        self.element_tr = QtWidgets.QLineEdit(self)
        self.element_tr.textChanged.connect(self.update_confirm_button)
        self.element_tr.setValidator(QDoubleValidator())

        self.element_bl = QtWidgets.QLineEdit(self)
        self.element_bl.textChanged.connect(self.update_confirm_button)
        self.element_bl.setValidator(QDoubleValidator())

        self.element_br = QtWidgets.QLineEdit(self)
        self.element_br.textChanged.connect(self.update_confirm_button)
        self.element_br.setValidator(QDoubleValidator())

        self.matrix_elements = (self.element_tl, self.element_tr, self.element_bl, self.element_br)

        # === Arrange the widgets

        self.grid_matrix = QGridLayout()
        self.grid_matrix.setSpacing(20)
        self.grid_matrix.addWidget(self.element_tl, 0, 0)
        self.grid_matrix.addWidget(self.element_tr, 0, 1)
        self.grid_matrix.addWidget(self.element_bl, 1, 0)
        self.grid_matrix.addWidget(self.element_br, 1, 1)

        self.hlay_definition.addLayout(self.grid_matrix)

        self.vlay_all.addLayout(self.hlay_definition)
        self.vlay_all.addLayout(self.hlay_buttons)

        # We load the default matrix A into the boxes
        self.load_matrix(0)

        self.element_tl.setFocus()

    @pyqtSlot()
    def update_confirm_button(self) -> None:
        """Enable the confirm button if there are valid floats in every box."""
        for elem in self.matrix_elements:
            if not is_valid_float(elem.text()):
                # If they're not all numbers, then we can't confirm it
                self.button_confirm.setEnabled(False)
                return

        # If we didn't find anything invalid
        self.button_confirm.setEnabled(True)

    @pyqtSlot(int)
    def load_matrix(self, index: int) -> None:
        """If the selected matrix is defined, load its values into the boxes."""
        matrix = self.matrix_wrapper[self.selected_letter]

        if matrix is None:
            for elem in self.matrix_elements:
                elem.setText('')

        else:
            self.element_tl.setText(round_float(matrix[0][0]))
            self.element_tr.setText(round_float(matrix[0][1]))
            self.element_bl.setText(round_float(matrix[1][0]))
            self.element_br.setText(round_float(matrix[1][1]))

        self.update_confirm_button()

    @pyqtSlot()
    def confirm_matrix(self) -> None:
        """Confirm the matrix in the boxes and assign it to the name in the combo box."""
        matrix: MatrixType = array([
            [float(self.element_tl.text()), float(self.element_tr.text())],
            [float(self.element_bl.text()), float(self.element_br.text())]
        ])

        self.matrix_wrapper[self.selected_letter] = matrix
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

        self.lineedit_expression_box = QtWidgets.QLineEdit(self)
        self.lineedit_expression_box.setPlaceholderText('Enter matrix expression...')
        self.lineedit_expression_box.textChanged.connect(self.update_confirm_button)
        self.lineedit_expression_box.setValidator(MatrixExpressionValidator())

        # === Arrange the widgets

        self.hlay_definition.addWidget(self.lineedit_expression_box)

        self.vlay_all.addLayout(self.hlay_definition)
        self.vlay_all.addLayout(self.hlay_buttons)

        # Load the matrix if it's defined as an expression
        self.load_matrix(0)

        self.lineedit_expression_box.setFocus()

    @pyqtSlot()
    def update_confirm_button(self) -> None:
        """Enable the confirm button if the matrix expression is valid in the wrapper."""
        text = self.lineedit_expression_box.text()
        valid_expression = self.matrix_wrapper.is_valid_expression(text)

        self.button_confirm.setEnabled(valid_expression and self.selected_letter not in text)

    @pyqtSlot(int)
    def load_matrix(self, index: int) -> None:
        """If the selected matrix is defined an expression, load that expression into the box."""
        if (expr := self.matrix_wrapper.get_expression(self.selected_letter)) is not None:
            self.lineedit_expression_box.setText(expr)
        else:
            self.lineedit_expression_box.setText('')

    @pyqtSlot()
    def confirm_matrix(self) -> None:
        """Evaluate the matrix expression and assign its value to the name in the combo box."""
        self.matrix_wrapper[self.selected_letter] = self.lineedit_expression_box.text()
        self.accept()
