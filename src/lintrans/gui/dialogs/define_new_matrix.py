"""The module to provide dialogs for defining new matrices."""

import abc

from numpy import array
from PyQt5 import QtWidgets
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QDialog, QGridLayout, QHBoxLayout, QShortcut, QSizePolicy, QSpacerItem, QVBoxLayout

from lintrans.matrices import create_rotation_matrix, MatrixWrapper

ALPHABET_NO_I = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'


def is_float(string: str) -> bool:
    """Check if a string is a float. '' is not a float and will return False."""
    try:
        float(string)
        return True
    except ValueError:
        return False


class DefineDialog(QDialog):
    """A semi-abstract superclass for definitions dialogs."""

    def __init__(self, matrix_wrapper: MatrixWrapper, *args, **kwargs):
        """Create the dialog, but don't run it yet.

        :param matrix_wrapper: The MatrixWrapper that this dialog will mutate
        :type matrix_wrapper: MatrixWrapper
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
        self.button_cancel.setToolTip('Cancel this definition<br><b>(Ctrl + Q)</b>')
        QShortcut(QKeySequence('Ctrl+Q'), self).activated.connect(self.button_cancel.click)

        self.label_equals = QtWidgets.QLabel()
        self.label_equals.setText('=')

        self.letter_combo_box = QtWidgets.QComboBox(self)

        for letter in ALPHABET_NO_I:
            self.letter_combo_box.addItem(letter)

        # === Arrange the widgets

        self.setContentsMargins(10, 10, 10, 10)

        self.horizontal_spacer = QSpacerItem(50, 5, hPolicy=QSizePolicy.Expanding, vPolicy=QSizePolicy.Minimum)

        self.hlay_buttons = QHBoxLayout()
        self.hlay_buttons.setSpacing(20)
        self.hlay_buttons.addItem(self.horizontal_spacer)
        self.hlay_buttons.addWidget(self.button_cancel)
        self.hlay_buttons.addWidget(self.button_confirm)

    @property
    def selected_letter(self) -> str:
        """The letter currently selected in the combo box."""
        return str(self.letter_combo_box.currentText())

    @abc.abstractmethod
    def update_confirm_button(self) -> None:
        """Enable the confirm button if it should be enabled."""

    @abc.abstractmethod
    def confirm_matrix(self) -> None:
        """Confirm the inputted matrix and assign it.

        This should mutate self.matrix_wrapper and then call self.accept().
        """


class DefineNumericallyDialog(DefineDialog):
    """The dialog class that allows the user to define a new matrix numerically."""

    def __init__(self, matrix_wrapper: MatrixWrapper, *args, **kwargs):
        """Create the dialog, but don't run it yet."""
        super().__init__(matrix_wrapper, *args, **kwargs)

        self.setMinimumWidth(500)

        # === Create the widgets

        self.letter_combo_box.activated.connect(self.load_matrix)

        self.element_tl = QtWidgets.QLineEdit(self)
        self.element_tl.textChanged.connect(self.update_confirm_button)

        self.element_tr = QtWidgets.QLineEdit(self)
        self.element_tr.textChanged.connect(self.update_confirm_button)

        self.element_bl = QtWidgets.QLineEdit(self)
        self.element_bl.textChanged.connect(self.update_confirm_button)

        self.element_br = QtWidgets.QLineEdit(self)
        self.element_br.textChanged.connect(self.update_confirm_button)

        self.matrix_elements = (self.element_tl, self.element_tr, self.element_bl, self.element_br)

        # === Arrange the widgets

        self.grid_matrix = QGridLayout()
        self.grid_matrix.setSpacing(20)
        self.grid_matrix.addWidget(self.element_tl, 0, 0)
        self.grid_matrix.addWidget(self.element_tr, 0, 1)
        self.grid_matrix.addWidget(self.element_bl, 1, 0)
        self.grid_matrix.addWidget(self.element_br, 1, 1)

        self.hlay_definition = QHBoxLayout()
        self.hlay_definition.setSpacing(20)
        self.hlay_definition.addWidget(self.letter_combo_box)
        self.hlay_definition.addWidget(self.label_equals)
        self.hlay_definition.addLayout(self.grid_matrix)

        self.vlay_all = QVBoxLayout()
        self.vlay_all.setSpacing(20)
        self.vlay_all.addLayout(self.hlay_definition)
        self.vlay_all.addLayout(self.hlay_buttons)

        self.setLayout(self.vlay_all)

        # Finally, we load the default matrix A into the boxes
        self.load_matrix(0)

    def update_confirm_button(self) -> None:
        """Enable the confirm button if there are numbers in every box."""
        for elem in self.matrix_elements:
            if not is_float(elem.text()):
                # If they're not all numbers, then we can't confirm it
                self.button_confirm.setEnabled(False)
                return

        # If we didn't find anything invalid
        self.button_confirm.setEnabled(True)

    def load_matrix(self, index: int) -> None:
        """If the selected matrix is defined, load it into the boxes."""
        matrix = self.matrix_wrapper[ALPHABET_NO_I[index]]

        if matrix is None:
            for elem in self.matrix_elements:
                elem.setText('')

        else:
            self.element_tl.setText(str(matrix[0][0]))
            self.element_tr.setText(str(matrix[0][1]))
            self.element_bl.setText(str(matrix[1][0]))
            self.element_br.setText(str(matrix[1][1]))

        self.update_confirm_button()

    def confirm_matrix(self) -> None:
        """Confirm the inputted matrix and assign it to the name."""
        matrix = array([
            [float(self.element_tl.text()), float(self.element_tr.text())],
            [float(self.element_bl.text()), float(self.element_br.text())]
        ])

        self.matrix_wrapper[self.selected_letter] = matrix
        self.accept()


class DefineAsARotationDialog(DefineDialog):
    """The dialog that allows the user to define a new matrix as a rotation."""

    def __init__(self, matrix_wrapper: MatrixWrapper, *args, **kwargs):
        """Create the dialog, but don't run it yet."""
        super().__init__(matrix_wrapper, *args, **kwargs)

        # === Create the widgets

        self.label_equals.setText('= rot(')

        self.text_angle = QtWidgets.QLineEdit(self)
        self.text_angle.setPlaceholderText('angle')
        self.text_angle.textChanged.connect(self.update_confirm_button)

        self.label_close_paren = QtWidgets.QLabel(self)
        self.label_close_paren.setText(')')

        self.checkbox_radians = QtWidgets.QCheckBox(self)
        self.checkbox_radians.setText('Radians')

        # === Arrange the widgets

        self.hlay_checkbox_and_buttons = QHBoxLayout()
        self.hlay_checkbox_and_buttons.setSpacing(20)
        self.hlay_checkbox_and_buttons.addWidget(self.checkbox_radians)
        self.hlay_checkbox_and_buttons.addItem(self.horizontal_spacer)
        self.hlay_checkbox_and_buttons.addLayout(self.hlay_buttons)

        self.hlay_definition = QHBoxLayout()
        self.hlay_definition.addWidget(self.letter_combo_box)
        self.hlay_definition.addWidget(self.label_equals)
        self.hlay_definition.addWidget(self.text_angle)
        self.hlay_definition.addWidget(self.label_close_paren)

        self.vlay_all = QVBoxLayout()
        self.vlay_all.setSpacing(20)
        self.vlay_all.addLayout(self.hlay_definition)
        self.vlay_all.addLayout(self.hlay_checkbox_and_buttons)

        self.setLayout(self.vlay_all)

    def update_confirm_button(self) -> None:
        """Enable the confirm button if there is a valid float in the angle box."""
        self.button_confirm.setEnabled(is_float(self.text_angle.text()))

    def confirm_matrix(self) -> None:
        """Confirm the inputted matrix and assign it."""
        self.matrix_wrapper[self.selected_letter] = create_rotation_matrix(
            float(self.text_angle.text()),
            degrees=not self.checkbox_radians.isChecked()
        )
        self.accept()
