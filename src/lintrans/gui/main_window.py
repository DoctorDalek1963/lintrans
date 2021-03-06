# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides the :class:`LintransMainWindow` class, which provides the main window for the GUI."""

from __future__ import annotations

import os
import pkgutil
import re
import sys
import webbrowser
from copy import deepcopy
from typing import List, Optional, Tuple, Type

import numpy as np
from numpy import linalg
from numpy.linalg import LinAlgError
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QCoreApplication, QThread
from PyQt5.QtGui import QCloseEvent, QIcon, QImage, QKeySequence, QPixmap
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QMainWindow, QMessageBox,
                             QShortcut, QSizePolicy, QSpacerItem, QStyleFactory, QVBoxLayout)

import lintrans
from lintrans.matrices import MatrixWrapper
from lintrans.matrices.parse import validate_matrix_expression
from lintrans.matrices.utility import polar_coords, rotate_coord
from lintrans.typing_ import MatrixType, VectorType
from .dialogs import (AboutDialog, DefineAsAnExpressionDialog, DefineDialog, DefineNumericallyDialog,
                      DefineVisuallyDialog, FileSelectDialog, InfoPanelDialog)
from .dialogs.settings import DisplaySettingsDialog
from .plots import VisualizeTransformationWidget
from .session import Session
from .settings import DisplaySettings
from .validate import MatrixExpressionValidator


class LintransMainWindow(QMainWindow):
    """This class provides a main window for the GUI using the Qt framework.

    This class should not be used directly, instead call :func:`lintrans.gui.main_window.main` to create the GUI.
    """

    def __init__(self):
        """Create the main window object, and create and arrange every widget in it.

        This doesn't show the window, it just constructs it.
        Use :func:`lintrans.gui.main_window.main` to show the GUI.
        """
        super().__init__()

        self.matrix_wrapper = MatrixWrapper()

        self.setWindowTitle('lintrans')
        self.setMinimumSize(1000, 750)

        # pkgutil.get_data is needed because it's more portable with the package
        # See https://stackoverflow.com/a/58941536/12985838
        # However, it returns the raw bytes of the jpg, so we have to construct a QImage
        # from that data, a QPixmap from the QImage, and then a QIcon from the QPixmap
        self.setWindowIcon(QIcon(QPixmap.fromImage(QImage.fromData(
                        pkgutil.get_data(__name__, 'assets/icon.jpg')
        ))))

        self.animating: bool = False
        self.animating_sequence: bool = False

        self.save_filename: Optional[str] = None
        self.changed_since_save: bool = False

        # === Create menubar

        self.menubar = QtWidgets.QMenuBar(self)

        self.menu_file = QtWidgets.QMenu(self.menubar)
        self.menu_file.setTitle('&File')

        self.menu_help = QtWidgets.QMenu(self.menubar)
        self.menu_help.setTitle('&Help')

        self.action_reset_session = QtWidgets.QAction(self)
        self.action_reset_session.setText('Reset session')
        self.action_reset_session.triggered.connect(self.reset_session)

        self.action_open = QtWidgets.QAction(self)
        self.action_open.setText('&Open')
        self.action_open.setShortcut('Ctrl+O')
        self.action_open.triggered.connect(self.ask_for_session_file)

        self.action_save = QtWidgets.QAction(self)
        self.action_save.setText('&Save')
        self.action_save.setShortcut('Ctrl+S')
        self.action_save.triggered.connect(self.save_session)

        self.action_save_as = QtWidgets.QAction(self)
        self.action_save_as.setText('Save as...')
        self.action_save_as.setShortcut('Ctrl+Shift+S')
        self.action_save_as.triggered.connect(self.save_session_as)

        self.action_tutorial = QtWidgets.QAction(self)
        self.action_tutorial.setText('&Tutorial')
        self.action_tutorial.setShortcut('F1')
        self.action_tutorial.triggered.connect(lambda: print('tutorial'))

        self.action_docs = QtWidgets.QAction(self)
        self.action_docs.setText('&Docs')

        # If this is an old release, use the docs for this release. Else, use the latest docs
        # We use the latest because most use cases for non-stable releases will be in development and testing
        docs_link = 'https://lintrans.readthedocs.io/en/'

        if re.match(r'^\d+\.\d+\.\d+$', lintrans.__version__):
            docs_link += 'v' + lintrans.__version__
        else:
            docs_link += 'latest'

        self.action_docs.triggered.connect(
            lambda: webbrowser.open_new_tab(docs_link)
        )

        self.action_about = QtWidgets.QAction(self)
        self.action_about.setText('&About')
        self.action_about.triggered.connect(lambda: AboutDialog(self).open())

        # TODO: Implement these actions and enable them
        self.action_tutorial.setEnabled(False)

        self.menu_file.addAction(self.action_reset_session)
        self.menu_file.addAction(self.action_open)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_save)
        self.menu_file.addAction(self.action_save_as)

        self.menu_help.addAction(self.action_tutorial)
        self.menu_help.addAction(self.action_docs)
        self.menu_help.addSeparator()
        self.menu_help.addAction(self.action_about)

        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_help.menuAction())

        self.setMenuBar(self.menubar)

        # === Create widgets

        # Left layout: the plot and input box

        self.plot = VisualizeTransformationWidget(self, display_settings=DisplaySettings())

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

        # Info panel button

        self.button_info_panel = QtWidgets.QPushButton(self)
        self.button_info_panel.setText('Show defined matrices')
        self.button_info_panel.clicked.connect(
            # We have to use a lambda instead of 'InfoPanelDialog(self.matrix_wrapper, self).open' here
            # because that would create an unnamed instance of InfoPanelDialog when LintransMainWindow is
            # constructed, but we need to create a new instance every time to keep self.matrix_wrapper up to date
            lambda: InfoPanelDialog(self.matrix_wrapper, self).open()
        )
        self.button_info_panel.setToolTip(
            'Open an info panel with all matrices that have been defined in this session<br><b>(Ctrl + M)</b>'
        )
        QShortcut(QKeySequence('Ctrl+M'), self).activated.connect(self.button_info_panel.click)

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

        self.vlay_info_buttons = QVBoxLayout()
        self.vlay_info_buttons.setSpacing(20)
        self.vlay_info_buttons.addWidget(self.button_info_panel)

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
        self.vlay_right.addLayout(self.vlay_info_buttons)
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

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle a :class:`QCloseEvent` by confirming if the user wants to save, and cancelling animation."""
        if self.save_filename is None or not self.changed_since_save:
            self.animating = False
            event.accept()
            return

        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Question)
        dialog.setWindowTitle('Save changes?')
        dialog.setText(f"If you don't save, then changes made to {self.save_filename} will be lost.")
        dialog.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        dialog.setDefaultButton(QMessageBox.Save)

        pressed_button = dialog.exec()

        if pressed_button == QMessageBox.Save:
            self.save_session()

        if pressed_button in (QMessageBox.Save, QMessageBox.Discard):
            self.animating = False
            event.accept()
        else:
            event.ignore()

    def update_render_buttons(self) -> None:
        """Enable or disable the render and animate buttons according to whether the matrix expression is valid."""
        text = self.lineedit_expression_box.text()

        # Let's say that the user defines a non-singular matrix A, then defines B as A^-1
        # If they then redefine A and make it singular, then we get a LinAlgError when
        # trying to evaluate an expression with B in it
        # To fix this, we just do naive validation rather than aware validation
        if ',' in text:
            self.button_render.setEnabled(False)

            try:
                valid = all(self.matrix_wrapper.is_valid_expression(x) for x in text.split(','))
            except LinAlgError:
                valid = all(validate_matrix_expression(x) for x in text.split(','))

            self.button_animate.setEnabled(valid)

        else:
            try:
                valid = self.matrix_wrapper.is_valid_expression(text)
            except LinAlgError:
                valid = validate_matrix_expression(text)

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

        except LinAlgError:
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
                    new_matrix = self.matrix_wrapper.evaluate_expression(expr)

                    if self.plot.display_settings.applicative_animation:
                        new_matrix = new_matrix @ current_matrix
                except LinAlgError:
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

            except LinAlgError:
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

    def _get_animation_frame(self, start: MatrixType, target: MatrixType, proportion: float) -> MatrixType:
        """Get the matrix to render for this frame of the animation.

        This method will smoothen the determinant if that setting in enabled and if the determinant is positive.
        It also animates rotation-like matrices using a logarithmic spiral to rotate around and scale continuously.
        Essentially, it just makes things look good when animating.

        :param MatrixType start: The starting matrix
        :param MatrixType start: The target matrix
        :param float proportion: How far we are through the loop
        """
        det_target = linalg.det(target)
        det_start = linalg.det(start)

        # This is the matrix that we're applying to get from start to target
        # We want to check if it's rotation-like
        if linalg.det(start) == 0:
            matrix_application = None
        else:
            matrix_application = target @ linalg.inv(start)

        # For a matrix to represent a rotation, it must have a positive determinant,
        # its vectors must be perpendicular, and its vectors must be the same length
        # The checks for 'abs(value) < 1e-10' are to account for floating point error
        if matrix_application is not None \
                and self.plot.display_settings.smoothen_determinant \
                and linalg.det(matrix_application) > 0 \
                and abs(np.dot(matrix_application.T[0], matrix_application.T[1])) < 1e-10 \
                and abs(np.hypot(*matrix_application.T[0]) - np.hypot(*matrix_application.T[1])) < 1e-10:
            rotation_vector: VectorType = matrix_application.T[0]  # Take the i column
            radius, angle = polar_coords(*rotation_vector)

            # We want the angle to be in [-pi, pi), so we have to subtract 2pi from it if it's too big
            if angle > np.pi:
                angle -= 2 * np.pi

            i: VectorType = start.T[0]
            j: VectorType = start.T[1]

            # Scale the coords with a list comprehension
            # It's a bit janky, but rotate_coords() will always return a 2-tuple,
            # so new_i and new_j will always be lists of length 2
            scale = (radius - 1) * proportion + 1
            new_i = [scale * c for c in rotate_coord(i[0], i[1], angle * proportion)]
            new_j = [scale * c for c in rotate_coord(j[0], j[1], angle * proportion)]

            return np.array(
                [
                    [new_i[0], new_j[0]],
                    [new_i[1], new_j[1]]
                ]
            )

        # matrix_a is the start matrix plus some part of the target, scaled by the proportion
        # If we just used matrix_a, then things would animate, but the determinants would be weird
        matrix_a = start + proportion * (target - start)

        if not self.plot.display_settings.smoothen_determinant or det_start * det_target <= 0:
            return matrix_a

        # To fix the determinant problem, we get the determinant of matrix_a and use it to normalize
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

        # We want to return B, but we have to scale it over time to have the target determinant

        # We want some C = dB such that det(C) is some target determinant T
        # det(dB) = d^2 det(B) = T => d = sqrt(abs(T / det(B))

        # We're also subtracting 1 and multiplying by the proportion and then adding one
        # This just scales the determinant along with the animation

        # That is all of course, if we can do that
        # We'll crash if we try to do this with det(B) == 0
        if det_b == 0:
            return matrix_a

        scalar = 1 + proportion * (np.sqrt(abs(det_target / det_b)) - 1)
        return scalar * matrix_b

    def animate_between_matrices(self, matrix_start: MatrixType, matrix_target: MatrixType) -> None:
        """Animate from the start matrix to the target matrix."""
        self.animating = True

        # Making steps depend on animation_time ensures a smooth animation without
        # massive overheads for small animation times
        steps = self.plot.display_settings.animation_time // 10

        for i in range(0, steps + 1):
            if not self.animating:
                break

            matrix_to_render = self._get_animation_frame(matrix_start, matrix_target, i / steps)

            if self.is_matrix_too_big(matrix_to_render):
                self.show_error_message('Matrix too big', "This matrix doesn't fit on the canvas")
                self.animating = False
                return

            self.plot.visualize_matrix_transformation(matrix_to_render)

            # We schedule the plot to be updated, tell the event loop to
            # process events, and asynchronously sleep for 10ms
            # This allows for other events to be processed while animating, like zooming in and out
            self.plot.update()
            QApplication.processEvents()
            QThread.msleep(self.plot.display_settings.animation_time // steps)

        self.animating = False

    @pyqtSlot(DefineDialog)
    def dialog_define_matrix(self, dialog_class: Type[DefineDialog]) -> None:
        """Open a generic definition dialog to define a new matrix.

        The class for the desired dialog is passed as an argument. We create an
        instance of this class and the dialog is opened asynchronously and modally
        (meaning it blocks interaction with the main window) with the proper method
        connected to the :meth:`QDialog.accepted` signal.

        .. note:: ``dialog_class`` must subclass :class:`lintrans.gui.dialogs.define_new_matrix.DefineDialog`.

        :param dialog_class: The dialog class to instantiate
        :type dialog_class: Type[lintrans.gui.dialogs.define_new_matrix.DefineDialog]
        """
        # We create a dialog with a deepcopy of the current matrix_wrapper
        # This avoids the dialog mutating this one
        dialog: DefineDialog

        if dialog_class == DefineVisuallyDialog:
            dialog = DefineVisuallyDialog(
                self,
                matrix_wrapper=deepcopy(self.matrix_wrapper),
                display_settings=self.plot.display_settings
            )
        else:
            dialog = dialog_class(self, matrix_wrapper=deepcopy(self.matrix_wrapper))

        # .open() is asynchronous and doesn't spawn a new event loop, but the dialog is still modal (blocking)
        dialog.open()

        # So we have to use the accepted signal to call a method when the user accepts the dialog
        dialog.accepted.connect(self.assign_matrix_wrapper)

    @pyqtSlot()
    def assign_matrix_wrapper(self) -> None:
        """Assign a new value to ``self.matrix_wrapper`` and give the expression box focus."""
        self.matrix_wrapper = self.sender().matrix_wrapper
        self.lineedit_expression_box.setFocus()
        self.update_render_buttons()

        self.changed_since_save = True
        self.update_window_title()

    @pyqtSlot()
    def dialog_change_display_settings(self) -> None:
        """Open the dialog to change the display settings."""
        dialog = DisplaySettingsDialog(self, display_settings=self.plot.display_settings)
        dialog.open()
        dialog.accepted.connect(lambda: self.assign_display_settings(dialog.display_settings))

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

        # This is `finished` rather than `accepted` because we want to update the buttons no matter what
        dialog.finished.connect(self.update_render_buttons)

    def is_matrix_too_big(self, matrix: MatrixType) -> bool:
        """Check if the given matrix will actually fit onto the canvas.

        Convert the elements of the matrix to canvas coords and make sure they fit within Qt's 32-bit integer limit.

        :param MatrixType matrix: The matrix to check
        :returns bool: Whether the matrix is too big to fit on the canvas
        """
        coords: List[Tuple[int, int]] = [self.plot.canvas_coords(*vector) for vector in matrix.T]

        for x, y in coords:
            if not (-2147483648 <= x <= 2147483647 and -2147483648 <= y <= 2147483647):
                return True

        return False

    def update_window_title(self) -> None:
        """Update the window title to reflect whether the session has changed since it was last saved."""
        title = 'lintrans'

        if self.save_filename:
            title = os.path.split(self.save_filename)[-1] + ' - ' + title

            if self.changed_since_save:
                title = '*' + title

        self.setWindowTitle(title)

    def reset_session(self) -> None:
        """Ask the user if they want to reset the current session.

        Resetting the session means setting the matrix wrapper to a new instance, and rendering I.
        """
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Question)
        dialog.setWindowTitle('Reset the session?')
        dialog.setText('Are you sure you want to reset the current session?')
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dialog.setDefaultButton(QMessageBox.No)

        if dialog.exec() == QMessageBox.Yes:
            self.matrix_wrapper = MatrixWrapper()

            self.lineedit_expression_box.setText('I')
            self.render_expression()
            self.lineedit_expression_box.setText('')
            self.lineedit_expression_box.setFocus()
            self.update_render_buttons()

            self.save_filename = None
            self.changed_since_save = False
            self.update_window_title()

    def open_session_file(self, filename: str) -> None:
        """Open the given session file.

        If the selected file is not a valid lintrans session file, we just show an error message,
        but if it's valid, we load it and set it as the default filename for saving.
        """
        try:
            session = Session.load_from_file(filename)

        # load_from_file() can raise errors if the contents is not a valid pickled Python object,
        # or if the pickled Python object is of the wrong type
        except (EOFError, FileNotFoundError, ValueError):
            self.show_error_message(
                'Invalid file contents',
                'This is not a valid lintrans session file',
                'Not all .lt files are lintrans session files. This file was probably created by an unrelated '
                'program.'
            )
            return

        self.matrix_wrapper = session.matrix_wrapper

        self.lineedit_expression_box.setText('I')
        self.render_expression()
        self.lineedit_expression_box.setText('')
        self.lineedit_expression_box.setFocus()
        self.update_render_buttons()

        # Set this as the default filename if we could read it properly
        self.save_filename = filename
        self.changed_since_save = False
        self.update_window_title()

    @pyqtSlot()
    def ask_for_session_file(self) -> None:
        """Ask the user to select a session file, and then open it and load the session."""
        dialog = QFileDialog(
            self,
            'Open a session',
            '.',
            'lintrans sessions (*.lt)'
        )
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setViewMode(QFileDialog.List)

        if dialog.exec():
            self.open_session_file(dialog.selectedFiles()[0])

    @pyqtSlot()
    def save_session(self) -> None:
        """Save the session to the given file.

        If ``self.save_filename`` is ``None``, then call :meth:`save_session_as` and return.
        """
        if self.save_filename is None:
            self.save_session_as()
            return

        Session(self.matrix_wrapper).save_to_file(self.save_filename)

        self.changed_since_save = False
        self.update_window_title()

    @pyqtSlot()
    def save_session_as(self) -> None:
        """Ask the user for a file to save the session to, and then call :meth:`save_session`.

        .. note::
           If the user doesn't select a file to save the session to, then the session
           just doesn't get saved, and :meth:`save_session` is never called.
        """
        dialog = FileSelectDialog(
            self,
            'Save this session',
            '.',
            'lintrans sessions (*.lt)'
        )
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setViewMode(QFileDialog.List)
        dialog.setDefaultSuffix('.lt')

        if dialog.exec():
            filename = dialog.selectedFiles()[0]
            self.save_filename = filename
            self.save_session()


def qapp() -> QCoreApplication:
    """Return the equivalent of the global :class:`qApp` pointer.

    :raises RuntimeError: If :meth:`QCoreApplication.instance` returns ``None``
    """
    instance = QCoreApplication.instance()

    if instance is None:
        raise RuntimeError('qApp undefined')

    return instance


def main(filename: Optional[str]) -> None:
    """Run the GUI by creating and showing an instance of :class:`LintransMainWindow`.

    :param Optional[str] filename: A session file to optionally open at startup
    """
    app = QApplication([])
    app.setApplicationName('lintrans')
    app.setApplicationVersion(lintrans.__version__)

    qapp().setStyle(QStyleFactory.create('fusion'))

    window = LintransMainWindow()

    if filename:
        window.open_session_file(filename)

    window.show()

    sys.exit(app.exec_())
