"""The module to provide dialogs for defining new matrices."""

from numpy import array
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QGridLayout, QHBoxLayout, QSizePolicy, QSpacerItem, QVBoxLayout

from lintrans.matrices import MatrixWrapper

ALPHABET_NO_I = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'


def is_float(string: str) -> bool:
    """Check if a string is a float."""
    try:
        float(string)
        return True
    except ValueError:
        return False


class DefineNumericallyDialog(QDialog):
    """The dialog class that allows the user to define a new matrix numerically."""

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

        QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Return'), self).activated.connect(self.button_confirm.click)

        self.button_cancel = QtWidgets.QPushButton(self)
        self.button_cancel.setText('Cancel')
        self.button_cancel.clicked.connect(self.close)
        self.button_cancel.setToolTip('Cancel this definition<br><b>(Ctrl + Q)</b>')

        QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Q'), self).activated.connect(self.button_cancel.click)

        self.label_equals = QtWidgets.QLabel()
        self.label_equals.setText('=')

        self.element_tl = QtWidgets.QLineEdit(self)
        self.element_tl.textChanged.connect(self.update_confirm_button)

        self.element_tr = QtWidgets.QLineEdit(self)
        self.element_tr.textChanged.connect(self.update_confirm_button)

        self.element_bl = QtWidgets.QLineEdit(self)
        self.element_bl.textChanged.connect(self.update_confirm_button)

        self.element_br = QtWidgets.QLineEdit(self)
        self.element_br.textChanged.connect(self.update_confirm_button)

        self.matrix_elements = (self.element_tl, self.element_tr, self.element_bl, self.element_br)

        self.letter_combo_box = QtWidgets.QComboBox(self)

        # Everything except I, because that's the identity
        for letter in ALPHABET_NO_I:
            self.letter_combo_box.addItem(letter)

        self.letter_combo_box.activated.connect(self.load_matrix)

        # === Arrange the widgets

        self.setContentsMargins(10, 10, 10, 10)

        self.grid_matrix = QGridLayout()
        self.grid_matrix.setSpacing(20)
        self.grid_matrix.addWidget(self.element_tl, 0, 0)
        self.grid_matrix.addWidget(self.element_tr, 0, 1)
        self.grid_matrix.addWidget(self.element_bl, 1, 0)
        self.grid_matrix.addWidget(self.element_br, 1, 1)

        self.hlay_buttons = QHBoxLayout()
        self.hlay_buttons.setSpacing(20)
        self.hlay_buttons.addItem(QSpacerItem(50, 5, hPolicy=QSizePolicy.Expanding, vPolicy=QSizePolicy.Minimum))
        self.hlay_buttons.addWidget(self.button_cancel)
        self.hlay_buttons.addWidget(self.button_confirm)

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
            if elem.text() == '' or not is_float(elem.text()):
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
        letter = self.letter_combo_box.currentText()
        matrix = array([
            [float(self.element_tl.text()), float(self.element_tr.text())],
            [float(self.element_bl.text()), float(self.element_br.text())]
        ])

        self.matrix_wrapper[letter] = matrix
        self.close()
