"""This module provides the :class:`LintransMainWindow` class, which provides the main window for the GUI."""

from __future__ import annotations

import sys
import time
import webbrowser
from copy import deepcopy
from typing import Type

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QShortcut, QSizePolicy, QSpacerItem, QVBoxLayout

from lintrans.matrices import MatrixWrapper
from .dialogs import DefineAsAnExpressionDialog, DefineAsARotationDialog, DefineDialog, DefineNumericallyDialog
from .plots import VisualizeTransformationWidget


class LintransMainWindow(QMainWindow):
    """This class provides a main window for the GUI using the Qt framework.

    This class should not be used directly, instead call :func:`lintrans.gui.main_window.main` to create the GUI.
    """

    def __init__(self):
        """Create the main window object, and create and arrange every widget in it.

        This doesn't show the window, it just constructs it. Use :func:`lintrans.gui.main_window.main` to show the GUI.
        """
        super().__init__()

        self.matrix_wrapper = MatrixWrapper()

        self.setWindowTitle('Linear Transformations')
        self.setMinimumWidth(750)

        # === Create menubar

        self.menubar = QtWidgets.QMenuBar(self)

        self.menu_file = QtWidgets.QMenu(self.menubar)
        self.menu_file.setTitle('&File')

        self.menu_help = QtWidgets.QMenu(self.menubar)
        self.menu_help.setTitle('&Help')

        self.action_new = QtWidgets.QAction(self)
        self.action_new.setText('&New')
        self.action_new.setShortcut('Ctrl+N')
        self.action_new.triggered.connect(lambda: print('new'))

        self.action_open = QtWidgets.QAction(self)
        self.action_open.setText('&Open')
        self.action_open.setShortcut('Ctrl+O')
        self.action_open.triggered.connect(lambda: print('open'))

        self.action_save = QtWidgets.QAction(self)
        self.action_save.setText('&Save')
        self.action_save.setShortcut('Ctrl+S')
        self.action_save.triggered.connect(lambda: print('save'))

        self.action_save_as = QtWidgets.QAction(self)
        self.action_save_as.setText('Save as...')
        self.action_save_as.triggered.connect(lambda: print('save as'))

        self.action_tutorial = QtWidgets.QAction(self)
        self.action_tutorial.setText('&Tutorial')
        self.action_tutorial.setShortcut('F1')
        self.action_tutorial.triggered.connect(lambda: print('tutorial'))

        self.action_docs = QtWidgets.QAction(self)
        self.action_docs.setText('&Docs')
        self.action_docs.triggered.connect(
            lambda: webbrowser.open_new_tab('https://doctordalek1963.github.io/lintrans')
        )

        self.action_about = QtWidgets.QAction(self)
        self.action_about.setText('&About')
        self.action_about.triggered.connect(lambda: print('about'))

        # TODO: Implement these actions and enable them
        self.action_new.setEnabled(False)
        self.action_open.setEnabled(False)
        self.action_save.setEnabled(False)
        self.action_save_as.setEnabled(False)
        self.action_tutorial.setEnabled(False)
        self.action_about.setEnabled(False)

        self.menu_file.addAction(self.action_new)
        self.menu_file.addAction(self.action_open)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_save)
        self.menu_file.addAction(self.action_save_as)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_about)

        self.menu_help.addAction(self.action_tutorial)
        self.menu_help.addAction(self.action_docs)

        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_help.menuAction())

        self.setMenuBar(self.menubar)

        # === Create widgets

        # Left layout: the plot and input box

        self.plot = VisualizeTransformationWidget(self)

        self.lineedit_expression_box = QtWidgets.QLineEdit(self)
        self.lineedit_expression_box.setPlaceholderText('Enter matrix expression...')
        self.lineedit_expression_box.textChanged.connect(self.update_render_buttons)

        # Right layout: all the buttons

        # Misc buttons

        self.button_create_polygon = QtWidgets.QPushButton(self)
        self.button_create_polygon.setText('Create polygon')
        # self.button_create_polygon.clicked.connect(self.create_polygon)
        self.button_create_polygon.setToolTip('Define a new polygon to view the transformation of')

        self.button_change_display_settings = QtWidgets.QPushButton(self)
        self.button_change_display_settings.setText('Change\ndisplay settings')
        # self.button_change_display_settings.clicked.connect(self.change_display_settings)
        self.button_change_display_settings.setToolTip('Change which things are rendered on the plot')

        # Define new matrix buttons

        self.label_define_new_matrix = QtWidgets.QLabel(self)
        self.label_define_new_matrix.setText('Define a\nnew matrix')
        self.label_define_new_matrix.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)

        self.button_define_visually = QtWidgets.QPushButton(self)
        self.button_define_visually.setText('Visually')
        self.button_define_visually.setToolTip('Drag the basis vectors<br><b>(Alt + 1)</b>')
        QShortcut(QKeySequence('Alt+1'), self).activated.connect(self.button_define_visually.click)

        self.button_define_numerically = QtWidgets.QPushButton(self)
        self.button_define_numerically.setText('Numerically')
        self.button_define_numerically.setToolTip('Define a matrix just with numbers<br><b>(Alt + 2)</b>')
        self.button_define_numerically.clicked.connect(lambda: self.dialog_define_matrix(DefineNumericallyDialog))
        QShortcut(QKeySequence('Alt+2'), self).activated.connect(self.button_define_numerically.click)

        self.button_define_as_rotation = QtWidgets.QPushButton(self)
        self.button_define_as_rotation.setText('As a rotation')
        self.button_define_as_rotation.setToolTip('Define an angle to rotate by<br><b>(Alt + 3)</b>')
        self.button_define_as_rotation.clicked.connect(lambda: self.dialog_define_matrix(DefineAsARotationDialog))
        QShortcut(QKeySequence('Alt+3'), self).activated.connect(self.button_define_as_rotation.click)

        self.button_define_as_expression = QtWidgets.QPushButton(self)
        self.button_define_as_expression.setText('As an expression')
        self.button_define_as_expression.setToolTip('Define a matrix in terms of other matrices<br><b>(Alt + 4)</b>')
        self.button_define_as_expression.clicked.connect(lambda: self.dialog_define_matrix(DefineAsAnExpressionDialog))
        QShortcut(QKeySequence('Alt+4'), self).activated.connect(self.button_define_as_expression.click)

        # Disable buttons that aren't implemented yet
        # TODO: Implement these and enable buttons
        self.button_create_polygon.setEnabled(False)
        self.button_change_display_settings.setEnabled(False)
        self.button_define_visually.setEnabled(False)

        # Render buttons

        self.button_render = QtWidgets.QPushButton(self)
        self.button_render.setText('Render')
        self.button_render.setEnabled(False)
        self.button_render.clicked.connect(self.render_expression)
        self.button_render.setToolTip('Render the expression<br><b>(Ctrl + Enter)</b>')
        QShortcut(QKeySequence('Ctrl+Return'), self).activated.connect(self.button_render.click)

        self.button_animate = QtWidgets.QPushButton(self)
        self.button_animate.setText('Animate')
        self.button_animate.setEnabled(False)
        self.button_animate.clicked.connect(self.animate_expression)
        self.button_animate.setToolTip('Animate the expression<br><b>(Ctrl + Shift + Enter)</b>')
        QShortcut(QKeySequence('Ctrl+Shift+Return'), self).activated.connect(self.button_animate.click)

        # === Arrange widgets

        self.vlay_left = QVBoxLayout()
        self.vlay_left.addWidget(self.plot)
        self.vlay_left.addWidget(self.lineedit_expression_box)

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
        self.central_widget.setContentsMargins(10, 10, 10, 10)

        self.setCentralWidget(self.central_widget)

    def update_render_buttons(self) -> None:
        """Enable or disable the render and animate buttons according to whether the matrix expression is valid."""
        valid = self.matrix_wrapper.is_valid_expression(self.lineedit_expression_box.text())
        self.button_render.setEnabled(valid)
        self.button_animate.setEnabled(valid)

    def render_expression(self) -> None:
        """Render the expression in the input box, and then clear the box."""
        self.plot.visualize_matrix_transformation(
            self.matrix_wrapper.evaluate_expression(
                self.lineedit_expression_box.text()
            )
        )

    def animate_expression(self) -> None:
        """Animate the expression in the input box, and then clear the box."""
        self.button_render.setEnabled(False)
        self.button_animate.setEnabled(False)

        matrix = self.matrix_wrapper.evaluate_expression(self.lineedit_expression_box.text())
        matrix_move = matrix - self.matrix_wrapper['I']
        steps: int = 100

        for i in range(0, steps + 1):
            self.plot.visualize_matrix_transformation(
                self.matrix_wrapper['I'] + (i / steps) * matrix_move
            )

            self.repaint()

            time.sleep(0.01)

        self.button_render.setEnabled(False)
        self.button_animate.setEnabled(False)

    def dialog_define_matrix(self, dialog_class: Type[DefineDialog]) -> None:
        """Open a generic definition dialog to define a new matrix.

        The class for the desired dialog is passed as an argument. We create an
        instance of this class and the dialog is opened asynchronously and modally
        (meaning it blocks interaction with the main window) with the proper method
        connected to the ``dialog.finished`` slot.

        .. note:: ``dialog_class`` must subclass :class:`lintrans.gui.dialogs.define_new_matrix.DefineDialog`.

        :param dialog_class: The dialog class to instantiate
        :type dialog_class: Type[lintrans.gui.dialogs.define_new_matrix.DefineDialog]
        """
        # We create a dialog with a deepcopy of the current matrix_wrapper
        # This avoids the dialog mutating this one
        dialog = dialog_class(deepcopy(self.matrix_wrapper), self)

        # .open() is asynchronous and doesn't spawn a new event loop, but the dialog is still modal (blocking)
        dialog.open()

        # So we have to use the finished slot to call a method when the user accepts the dialog
        # If the user rejects the dialog, this matrix_wrapper will be the same as the current one, because we copied it
        # So we don't care, we just assign the wrapper anyway
        dialog.finished.connect(lambda: self._assign_matrix_wrapper(dialog.matrix_wrapper))

    def _assign_matrix_wrapper(self, matrix_wrapper: MatrixWrapper) -> None:
        """Assign a new value to self.matrix_wrapper.

        This is a little utility function that only exists because a lambda
        callback can't directly assign a value to a class attribute.

        :param matrix_wrapper: The new value of the matrix wrapper to assign
        :type matrix_wrapper: MatrixWrapper
        """
        self.matrix_wrapper = matrix_wrapper


def main(args: list[str]) -> None:
    """Run the GUI by creating and showing an instance of :class:`LintransMainWindow`.

    :param list[str] args: The args to pass to ``QApplication()`` (normally ``sys.argv``)
    """
    app = QApplication(args)
    window = LintransMainWindow()
    window.show()
    sys.exit(app.exec_())