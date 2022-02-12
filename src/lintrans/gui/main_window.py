"""This module provides the :class:`LintransMainWindow` class, which provides the main window for the GUI."""

from __future__ import annotations

import sys
import webbrowser
from copy import deepcopy
from typing import Type

import numpy as np
from numpy import linalg
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QMainWindow, QMessageBox,
                             QShortcut, QSizePolicy, QSpacerItem, QVBoxLayout)

from lintrans.matrices import MatrixWrapper
from lintrans.typing import MatrixType
from .dialogs import DefineAsAnExpressionDialog, DefineDialog, DefineNumericallyDialog, DefineVisuallyDialog
from .dialogs.settings import DisplaySettingsDialog
from .plots import VisualizeTransformationWidget
from .settings import DisplaySettings
from lintrans.gui.validate import MatrixExpressionValidator


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
        self.setMinimumSize(1000, 750)

        self.animating: bool = False
        self.animating_sequence: bool = False

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

        self.plot = VisualizeTransformationWidget(DisplaySettings(), self)

        self.lineedit_expression_box = QtWidgets.QLineEdit(self)
        self.lineedit_expression_box.setPlaceholderText('Enter matrix expression...')
        self.lineedit_expression_box.setValidator(MatrixExpressionValidator(self))
        self.lineedit_expression_box.textChanged.connect(self.update_render_buttons)

        # Right layout: all the buttons

        # Misc buttons

        self.button_create_polygon = QtWidgets.QPushButton(self)
        self.button_create_polygon.setText('Create polygon')
        # self.button_create_polygon.clicked.connect(self.create_polygon)
        self.button_create_polygon.setToolTip('Define a new polygon to view the transformation of')

        # TODO: Implement this and enable button
        self.button_create_polygon.setEnabled(False)

        self.button_change_display_settings = QtWidgets.QPushButton(self)
        self.button_change_display_settings.setText('Change\ndisplay settings')
        self.button_change_display_settings.clicked.connect(self.dialog_change_display_settings)
        self.button_change_display_settings.setToolTip(
            "Change which things are rendered and how they're rendered<br><b>(Ctrl + D)</b>"
        )
        QShortcut(QKeySequence('Ctrl+D'), self).activated.connect(self.button_change_display_settings.click)

        self.button_reset_zoom = QtWidgets.QPushButton(self)
        self.button_reset_zoom.setText('Reset zoom')
        self.button_reset_zoom.clicked.connect(self.reset_zoom)
        self.button_reset_zoom.setToolTip('Reset the zoom level back to normal<br><b>(Ctrl + Shift + R)</b>')
        QShortcut(QKeySequence('Ctrl+Shift+R'), self).activated.connect(self.button_reset_zoom.click)

        # Define new matrix buttons and their groupbox

        self.button_define_visually = QtWidgets.QPushButton(self)
        self.button_define_visually.setText('Visually')
        self.button_define_visually.setToolTip('Drag the basis vectors<br><b>(Alt + 1)</b>')
        self.button_define_visually.clicked.connect(lambda: self.dialog_define_matrix(DefineVisuallyDialog))
        QShortcut(QKeySequence('Alt+1'), self).activated.connect(self.button_define_visually.click)

        self.button_define_numerically = QtWidgets.QPushButton(self)
        self.button_define_numerically.setText('Numerically')
        self.button_define_numerically.setToolTip('Define a matrix just with numbers<br><b>(Alt + 2)</b>')
        self.button_define_numerically.clicked.connect(lambda: self.dialog_define_matrix(DefineNumericallyDialog))
        QShortcut(QKeySequence('Alt+2'), self).activated.connect(self.button_define_numerically.click)

        self.button_define_as_expression = QtWidgets.QPushButton(self)
        self.button_define_as_expression.setText('As an expression')
        self.button_define_as_expression.setToolTip('Define a matrix in terms of other matrices<br><b>(Alt + 3)</b>')
        self.button_define_as_expression.clicked.connect(lambda: self.dialog_define_matrix(DefineAsAnExpressionDialog))
        QShortcut(QKeySequence('Alt+3'), self).activated.connect(self.button_define_as_expression.click)

        self.vlay_define_new_matrix = QVBoxLayout()
        self.vlay_define_new_matrix.setSpacing(20)
        self.vlay_define_new_matrix.addWidget(self.button_define_visually)
        self.vlay_define_new_matrix.addWidget(self.button_define_numerically)
        self.vlay_define_new_matrix.addWidget(self.button_define_as_expression)

        self.groupbox_define_new_matrix = QtWidgets.QGroupBox('Define a new matrix', self)
        self.groupbox_define_new_matrix.setLayout(self.vlay_define_new_matrix)

        # Render buttons

        self.button_reset = QtWidgets.QPushButton(self)
        self.button_reset.setText('Reset')
        self.button_reset.clicked.connect(self.reset_transformation)
        self.button_reset.setToolTip('Reset the visualized transformation back to the identity<br><b>(Ctrl + R)</b>')
        QShortcut(QKeySequence('Ctrl+R'), self).activated.connect(self.button_reset.click)

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
        self.vlay_misc_buttons.addWidget(self.button_reset_zoom)

        self.vlay_render = QVBoxLayout()
        self.vlay_render.setSpacing(20)
        self.vlay_render.addWidget(self.button_reset)
        self.vlay_render.addWidget(self.button_animate)
        self.vlay_render.addWidget(self.button_render)

        self.vlay_right = QVBoxLayout()
        self.vlay_right.setSpacing(50)
        self.vlay_right.addLayout(self.vlay_misc_buttons)
        self.vlay_right.addItem(QSpacerItem(100, 2, hPolicy=QSizePolicy.Minimum, vPolicy=QSizePolicy.Expanding))
        self.vlay_right.addWidget(self.groupbox_define_new_matrix)
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
        text = self.lineedit_expression_box.text()

        if ',' in text:
            self.button_render.setEnabled(False)

            valid = all(self.matrix_wrapper.is_valid_expression(x) for x in text.split(','))
            self.button_animate.setEnabled(valid)

        else:
            valid = self.matrix_wrapper.is_valid_expression(text)
            self.button_render.setEnabled(valid)
            self.button_animate.setEnabled(valid)

    @pyqtSlot()
    def reset_zoom(self) -> None:
        """Reset the zoom level back to normal."""
        self.plot.grid_spacing = self.plot.default_grid_spacing
        self.plot.update()

    @pyqtSlot()
    def reset_transformation(self) -> None:
        """Reset the visualized transformation back to the identity."""
        self.plot.visualize_matrix_transformation(self.matrix_wrapper['I'])
        self.animating = False
        self.animating_sequence = False
        self.plot.update()

    @pyqtSlot()
    def render_expression(self) -> None:
        """Render the transformation given by the expression in the input box."""
        try:
            matrix = self.matrix_wrapper.evaluate_expression(self.lineedit_expression_box.text())

        except linalg.LinAlgError:
            self.show_error_message('Singular matrix', 'Cannot take inverse of singular matrix')
            return

        if self.is_matrix_too_big(matrix):
            self.show_error_message('Matrix too big', "This matrix doesn't fit on the canvas")
            return

        self.plot.visualize_matrix_transformation(matrix)
        self.plot.update()

    @pyqtSlot()
    def animate_expression(self) -> None:
        """Animate from the current matrix to the matrix in the expression box."""
        self.button_render.setEnabled(False)
        self.button_animate.setEnabled(False)

        matrix_start: MatrixType = np.array([
            [self.plot.point_i[0], self.plot.point_j[0]],
            [self.plot.point_i[1], self.plot.point_j[1]]
        ])

        text = self.lineedit_expression_box.text()

        # If there's commas in the expression, then we want to animate each part at a time
        if ',' in text:
            current_matrix = matrix_start
            self.animating_sequence = True

            # For each expression in the list, right multiply it by the current matrix,
            # and animate from the current matrix to that new matrix
            for expr in text.split(',')[::-1]:
                try:
                    new_matrix = self.matrix_wrapper.evaluate_expression(expr) @ current_matrix
                except linalg.LinAlgError:
                    self.show_error_message('Singular matrix', 'Cannot take inverse of singular matrix')
                    return

                if not self.animating_sequence:
                    break

                self.animate_between_matrices(current_matrix, new_matrix)
                current_matrix = new_matrix

                # Here we just redraw and allow for other events to be handled while we pause
                self.plot.update()
                QApplication.processEvents()
                QThread.msleep(self.plot.display_settings.animation_pause_length)

            self.animating_sequence = False

        # If there's no commas, then just animate directly from the start to the target
        else:
            # Get the target matrix and it's determinant
            try:
                matrix_target = self.matrix_wrapper.evaluate_expression(text)

            except linalg.LinAlgError:
                self.show_error_message('Singular matrix', 'Cannot take inverse of singular matrix')
                return

            # The concept of applicative animation is explained in /gui/settings.py
            if self.plot.display_settings.applicative_animation:
                matrix_target = matrix_target @ matrix_start

            # If we want a transitional animation and we're animating the same matrix, then restart the animation
            # We use this check rather than equality because of small floating point errors
            elif (abs(matrix_start - matrix_target) < 1e-12).all():
                matrix_start = self.matrix_wrapper['I']

                # We pause here for 200 ms to make the animation look a bit nicer
                self.plot.visualize_matrix_transformation(matrix_start)
                self.plot.update()
                QApplication.processEvents()
                QThread.msleep(200)

            self.animate_between_matrices(matrix_start, matrix_target)

        self.update_render_buttons()

    def animate_between_matrices(self, matrix_start: MatrixType, matrix_target: MatrixType, steps: int = 100) -> None:
        """Animate from the start matrix to the target matrix."""
        det_target = linalg.det(matrix_target)
        det_start = linalg.det(matrix_start)

        self.animating = True

        for i in range(0, steps + 1):
            if not self.animating:
                break

            # This proportion is how far we are through the loop
            proportion = i / steps

            # matrix_a is the start matrix plus some part of the target, scaled by the proportion
            # If we just used matrix_a, then things would animate, but the determinants would be weird
            matrix_a = matrix_start + proportion * (matrix_target - matrix_start)

            if self.plot.display_settings.smoothen_determinant and det_start * det_target > 0:
                # To fix the determinant problem, we get the determinant of matrix_a and use it to normalise
                det_a = linalg.det(matrix_a)

                # For a 2x2 matrix A and a scalar c, we know that det(cA) = c^2 det(A)
                # We want B = cA such that det(B) = det(S), where S is the start matrix,
                # so then we can scale it with the animation, so we get
                # det(cA) = c^2 det(A) = det(S) => c = sqrt(abs(det(S) / det(A)))
                # Then we scale A to get the determinant we want, and call that matrix_b
                if det_a == 0:
                    c = 0
                else:
                    c = np.sqrt(abs(det_start / det_a))

                matrix_b = c * matrix_a
                det_b = linalg.det(matrix_b)

                # matrix_to_render is the final matrix that we then render for this frame
                # It's B, but we scale it over time to have the target determinant

                # We want some C = dB such that det(C) is some target determinant T
                # det(dB) = d^2 det(B) = T => d = sqrt(abs(T / det(B))

                # We're also subtracting 1 and multiplying by the proportion and then adding one
                # This just scales the determinant along with the animation

                # That is all of course, if we can do that
                # We'll crash if we try to do this with det(B) == 0
                if det_b != 0:
                    scalar = 1 + proportion * (np.sqrt(abs(det_target / det_b)) - 1)
                    matrix_to_render = scalar * matrix_b

                else:
                    matrix_to_render = matrix_a

            else:
                matrix_to_render = matrix_a

            if self.is_matrix_too_big(matrix_to_render):
                self.show_error_message('Matrix too big', "This matrix doesn't fit on the canvas")
                return

            self.plot.visualize_matrix_transformation(matrix_to_render)

            # We schedule the plot to be updated, tell the event loop to
            # process events, and asynchronously sleep for 10ms
            # This allows for other events to be processed while animating, like zooming in and out
            self.plot.update()
            QApplication.processEvents()
            QThread.msleep(1000 // steps)

        self.animating = False

    @pyqtSlot(DefineDialog)
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
        dialog.finished.connect(self.assign_matrix_wrapper)

    @pyqtSlot()
    def assign_matrix_wrapper(self) -> None:
        """Assign a new value to ``self.matrix_wrapper`` and give the expression box focus."""
        self.matrix_wrapper = self.sender().matrix_wrapper
        self.lineedit_expression_box.setFocus()
        self.update_render_buttons()

    @pyqtSlot()
    def dialog_change_display_settings(self) -> None:
        """Open the dialog to change the display settings."""
        dialog = DisplaySettingsDialog(self.plot.display_settings, self)
        dialog.open()
        dialog.finished.connect(lambda: self.assign_display_settings(dialog.display_settings))

    @pyqtSlot(DisplaySettings)
    def assign_display_settings(self, display_settings: DisplaySettings) -> None:
        """Assign a new value to ``self.plot.display_settings`` and give the expression box focus."""
        self.plot.display_settings = display_settings
        self.plot.update()
        self.lineedit_expression_box.setFocus()
        self.update_render_buttons()

    def show_error_message(self, title: str, text: str, info: str | None = None) -> None:
        """Show an error message in a dialog box.

        :param str title: The window title of the dialog box
        :param str text: The simple error message
        :param info: The more informative error message
        :type info: Optional[str]
        """
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Critical)
        dialog.setWindowTitle(title)
        dialog.setText(text)

        if info is not None:
            dialog.setInformativeText(info)

        dialog.open()

        dialog.finished.connect(self.update_render_buttons)

    def is_matrix_too_big(self, matrix: MatrixType) -> bool:
        """Check if the given matrix will actually fit onto the canvas.

        Convert the elements of the matrix to canvas coords and make sure they fit within Qt's 32-bit integer limit.

        :param MatrixType matrix: The matrix to check
        :returns bool: Whether the matrix fits on the canvas
        """
        coords: list[tuple[int, int]] = [self.plot.canvas_coords(*vector) for vector in matrix.T]

        for x, y in coords:
            if not (-2147483648 <= x <= 2147483647 and -2147483648 <= y <= 2147483647):
                return True

        return False


def main(args: list[str]) -> None:
    """Run the GUI by creating and showing an instance of :class:`LintransMainWindow`.

    :param list[str] args: The args to pass to ``QApplication()`` (normally ``sys.argv``)
    """
    app = QApplication(args)
    window = LintransMainWindow()
    window.show()
    sys.exit(app.exec_())
