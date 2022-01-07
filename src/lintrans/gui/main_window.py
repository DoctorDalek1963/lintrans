"""The module to provide the main window as a QMainWindow object."""

import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QSizePolicy, QSpacerItem, QVBoxLayout

from lintrans.matrices import MatrixWrapper
from .dialogs import DefineNumericallyDialog


class LintransMainWindow(QMainWindow):
    """The class for the main window in the lintrans GUI."""

    def __init__(self):
        """Create the main window object, creating every widget in it."""
        super().__init__()

        self.matrix_wrapper = MatrixWrapper()

        self.setWindowTitle('Linear Transformations')
        self.setMinimumWidth(750)

        # === Create widgets

        # Left layout: the plot and input box

        # NOTE: This QGraphicsView is only temporary
        self.plot = QtWidgets.QGraphicsView(self)

        self.text_input_expression = QtWidgets.QLineEdit(self)
        self.text_input_expression.setPlaceholderText('Input matrix expression...')
        self.text_input_expression.textChanged.connect(self.update_render_buttons)

        # Right layout: all the buttons

        # Misc buttons

        self.button_create_polygon = QtWidgets.QPushButton(self)
        self.button_create_polygon.setText('Create polygon')
        # TODO: Implement create_polygon()
        # self.button_create_polygon.clicked.connect(self.create_polygon)
        self.button_create_polygon.setToolTip('Define a new polygon to view the transformation of')

        self.button_change_display_settings = QtWidgets.QPushButton(self)
        self.button_change_display_settings.setText('Change\ndisplay settings')
        # TODO: Implement change_display_settings()
        # self.button_change_display_settings.clicked.connect(self.change_display_settings)
        self.button_change_display_settings.setToolTip('Change which things are rendered on the plot')

        # Define new matrix buttons

        self.label_define_new_matrix = QtWidgets.QLabel(self)
        self.label_define_new_matrix.setText('Define a\nnew matrix')
        self.label_define_new_matrix.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)

        # TODO: Implement defining a new matrix visually, numerically, as a rotation, and as an expression

        self.button_define_visually = QtWidgets.QPushButton(self)
        self.button_define_visually.setText('Visually')
        self.button_define_visually.setToolTip('Drag the basis vectors<br><b>(Alt + 1)</b>')
        QtWidgets.QShortcut(QtGui.QKeySequence('Alt+1'), self).activated.connect(self.button_define_visually.click)

        self.button_define_numerically = QtWidgets.QPushButton(self)
        self.button_define_numerically.setText('Numerically')
        self.button_define_numerically.setToolTip('Define a matrix just with numbers<br><b>(Alt + 2)</b>')
        self.button_define_numerically.clicked.connect(
            lambda: DefineNumericallyDialog(self.matrix_wrapper, self).exec()
        )
        QtWidgets.QShortcut(QtGui.QKeySequence('Alt+2'), self).activated.connect(self.button_define_numerically.click)

        self.button_define_as_rotation = QtWidgets.QPushButton(self)
        self.button_define_as_rotation.setText('As a rotation')
        self.button_define_as_rotation.setToolTip('Define an angle to rotate by<br><b>(Alt + 3)</b>')
        QtWidgets.QShortcut(QtGui.QKeySequence('Alt+3'), self).activated.connect(self.button_define_as_rotation.click)

        self.button_define_as_expression = QtWidgets.QPushButton(self)
        self.button_define_as_expression.setText('As an expression')
        self.button_define_as_expression.setToolTip('Define a matrix in terms of other matrices<br><b>(Alt + 4)</b>')
        QtWidgets.QShortcut(QtGui.QKeySequence('Alt+4'), self).activated.connect(self.button_define_as_expression.click)

        # Render buttons

        self.button_render = QtWidgets.QPushButton(self)
        self.button_render.setText('Render')
        self.button_render.setEnabled(False)
        self.button_render.clicked.connect(self.render_expression)
        self.button_render.setToolTip('Render the expression<br><b>(Ctrl + Enter)</b>')

        self.button_render_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Return'), self)
        self.button_render_shortcut.activated.connect(self.button_render.click)

        self.button_animate = QtWidgets.QPushButton(self)
        self.button_animate.setText('Animate')
        self.button_animate.setEnabled(False)
        self.button_animate.clicked.connect(self.animate_expression)
        self.button_animate.setToolTip('Animate the expression<br><b>(Ctrl + Shift + Enter)</b>')

        self.button_animate_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Shift+Return'), self)
        self.button_animate_shortcut.activated.connect(self.button_animate.click)

        # === Arrange widgets

        self.setContentsMargins(10, 10, 10, 10)

        self.vlay_left = QVBoxLayout()
        self.vlay_left.addWidget(self.plot)
        self.vlay_left.addWidget(self.text_input_expression)

        self.vlay_misc_buttons = QVBoxLayout()
        self.vlay_misc_buttons.setSpacing(20)
        self.vlay_misc_buttons.addWidget(self.button_create_polygon)
        self.vlay_misc_buttons.addWidget(self.button_change_display_settings)

        self.vlay_define_new_matrix = QVBoxLayout()
        self.vlay_define_new_matrix.setSpacing(20)
        self.vlay_define_new_matrix.addWidget(self.label_define_new_matrix)
        self.vlay_define_new_matrix.addWidget(self.button_define_visually)
        self.vlay_define_new_matrix.addWidget(self.button_define_numerically)
        self.vlay_define_new_matrix.addWidget(self.button_define_as_rotation)
        self.vlay_define_new_matrix.addWidget(self.button_define_as_expression)

        self.vlay_render = QVBoxLayout()
        self.vlay_render.setSpacing(20)
        self.vlay_render.addWidget(self.button_animate)
        self.vlay_render.addWidget(self.button_render)

        self.vlay_right = QVBoxLayout()
        self.vlay_right.setSpacing(50)
        self.vlay_right.addLayout(self.vlay_misc_buttons)
        self.vlay_right.addItem(QSpacerItem(100, 2, hPolicy=QSizePolicy.Minimum, vPolicy=QSizePolicy.Expanding))
        self.vlay_right.addLayout(self.vlay_define_new_matrix)
        self.vlay_right.addItem(QSpacerItem(100, 2, hPolicy=QSizePolicy.Minimum, vPolicy=QSizePolicy.Expanding))
        self.vlay_right.addLayout(self.vlay_render)

        self.hlay_all = QHBoxLayout()
        self.hlay_all.setSpacing(15)
        self.hlay_all.addLayout(self.vlay_left)
        self.hlay_all.addLayout(self.vlay_right)

        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(self.hlay_all)
        self.setCentralWidget(self.central_widget)

    def update_render_buttons(self) -> None:
        """Enable or disable the render and animate buttons according to the validity of the matrix expression."""
        valid = self.matrix_wrapper.is_valid_expression(self.text_input_expression.text())
        self.button_render.setEnabled(valid)
        self.button_animate.setEnabled(valid)

    def render_expression(self) -> None:
        """Render the expression in the input box, and then clear the box."""
        # TODO: Render the expression
        self.text_input_expression.setText('')

    def animate_expression(self) -> None:
        """Animate the expression in the input box, and then clear the box."""
        # TODO: Animate the expression
        self.text_input_expression.setText('')


def main() -> None:
    """Run the GUI."""
    app = QApplication(sys.argv)
    window = LintransMainWindow()
    window.show()
    sys.exit(app.exec_())
