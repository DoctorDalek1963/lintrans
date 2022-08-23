# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides the :class:`LintransMainWindow` class, which provides the main window for the GUI."""

from __future__ import annotations

import os
import re
import sys
import webbrowser
from copy import deepcopy
from pathlib import Path
from pickle import UnpicklingError
from typing import List, Optional, Tuple, Type

import numpy as np
from numpy import linalg
from numpy.linalg import LinAlgError
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QThread
from PyQt5.QtGui import QCloseEvent, QIcon, QKeySequence
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QHBoxLayout, QMainWindow, QMenu, QMessageBox,
                             QPushButton, QShortcut, QSizePolicy, QSpacerItem, QStyleFactory, QVBoxLayout)

import lintrans
from lintrans.global_settings import global_settings
from lintrans.matrices import MatrixWrapper
from lintrans.matrices.parse import validate_matrix_expression
from lintrans.matrices.utility import polar_coords, rotate_coord
from lintrans.typing_ import MatrixType, VectorType
from .dialogs import (AboutDialog, DefineAsExpressionDialog, DefineMatrixDialog,
                      DefineNumericallyDialog, DefinePolygonDialog, DefineVisuallyDialog,
                      DisplaySettingsDialog, FileSelectDialog, InfoPanelDialog)
from .plots import MainViewportWidget
from .session import Session
from .settings import DisplaySettings
from .utility import qapp
from .validate import MatrixExpressionValidator


class LintransMainWindow(QMainWindow):
    """This class provides a main window for the GUI using the Qt framework.

    This class should not be used directly, instead call :func:`main` to create the GUI.
    """

    def __init__(self):
        """Create the main window object, and create and arrange every widget in it.

        This doesn't show the window, it just constructs it. Use :func:`main` to show the GUI.
        """
        super().__init__()

        self._matrix_wrapper = MatrixWrapper()

        self.setWindowTitle('lintrans')
        self.setMinimumSize(1000, 750)

        path = Path(__file__).parent.absolute() / 'assets' / 'icon.jpg'
        self.setWindowIcon(QIcon(str(path)))

        self._animating: bool = False
        self._animating_sequence: bool = False
        self._reset_during_animation: bool = False

        self._save_filename: Optional[str] = None
        self._changed_since_save: bool = False

        # === Create menubar

        menubar = QtWidgets.QMenuBar(self)

        menu_file = QMenu(menubar)
        menu_file.setTitle('&File')

        menu_help = QMenu(menubar)
        menu_help.setTitle('&Help')

        action_reset_session = QAction(self)
        action_reset_session.setText('Reset session')
        action_reset_session.triggered.connect(self._reset_session)

        action_open = QAction(self)
        action_open.setText('&Open')
        action_open.setShortcut('Ctrl+O')
        action_open.triggered.connect(self._ask_for_session_file)

        action_save = QAction(self)
        action_save.setText('&Save')
        action_save.setShortcut('Ctrl+S')
        action_save.triggered.connect(self._save_session)

        action_save_as = QAction(self)
        action_save_as.setText('Save as...')
        action_save_as.setShortcut('Ctrl+Shift+S')
        action_save_as.triggered.connect(self._save_session_as)

        action_quit = QAction(self)
        action_quit.setText('&Quit')
        action_quit.triggered.connect(self.close)

        # If this is an old release, use the docs for this release. Else, use the latest docs
        # We use the latest because most use cases for non-stable releases will be in development and testing
        docs_link = 'https://lintrans.readthedocs.io/en/'

        if re.match(r'^\d+\.\d+\.\d+$', lintrans.__version__):
            docs_link += 'v' + lintrans.__version__
        else:
            docs_link += 'latest'

        action_tutorial = QAction(self)
        action_tutorial.setText('&Tutorial')
        action_tutorial.setShortcut('F1')
        action_tutorial.triggered.connect(
            lambda: webbrowser.open_new_tab(docs_link + '/tutorial/index.html')
        )

        action_docs = QAction(self)
        action_docs.setText('&Docs')
        action_docs.triggered.connect(
            lambda: webbrowser.open_new_tab(docs_link + '/backend/lintrans.html')
        )

        menu_feedback = QMenu(menu_help)
        menu_feedback.setTitle('Give feedback')

        action_bug_report = QAction(self)
        action_bug_report.setText('Report a bug')
        action_bug_report.triggered.connect(
            lambda: webbrowser.open_new_tab('https://forms.gle/Q82cLTtgPLcV4xQD6')
        )

        action_suggest_feature = QAction(self)
        action_suggest_feature.setText('Suggest a new feature')
        action_suggest_feature.triggered.connect(
            lambda: webbrowser.open_new_tab('https://forms.gle/mVWbHiMBw9Zq5Ze37')
        )

        menu_feedback.addAction(action_bug_report)
        menu_feedback.addAction(action_suggest_feature)

        action_about = QAction(self)
        action_about.setText('&About')
        action_about.triggered.connect(lambda: AboutDialog(self).open())

        menu_file.addAction(action_reset_session)
        menu_file.addAction(action_open)
        menu_file.addSeparator()
        menu_file.addAction(action_save)
        menu_file.addAction(action_save_as)
        menu_file.addSeparator()
        menu_file.addAction(action_quit)

        menu_help.addAction(action_tutorial)
        menu_help.addAction(action_docs)
        menu_help.addSeparator()
        menu_help.addMenu(menu_feedback)
        menu_help.addSeparator()
        menu_help.addAction(action_about)

        menubar.addAction(menu_file.menuAction())
        menubar.addAction(menu_help.menuAction())

        self.setMenuBar(menubar)

        # === Create widgets

        # Left layout: the plot and input box

        self._plot = MainViewportWidget(self, display_settings=DisplaySettings(), polygon_points=[])

        self._lineedit_expression_box = QtWidgets.QLineEdit(self)
        self._lineedit_expression_box.setPlaceholderText('Enter matrix expression...')
        self._lineedit_expression_box.setValidator(MatrixExpressionValidator(self))
        self._lineedit_expression_box.textChanged.connect(self._update_render_buttons)

        # Right layout: all the buttons

        # Misc buttons

        button_define_polygon = QPushButton(self)
        button_define_polygon.setText('Define polygon')
        button_define_polygon.clicked.connect(self._dialog_define_polygon)
        button_define_polygon.setToolTip('Define a polygon to view its transformation<br><b>(Ctrl + P)</b>')
        QShortcut(QKeySequence('Ctrl+P'), self).activated.connect(button_define_polygon.click)

        self._button_change_display_settings = QPushButton(self)
        self._button_change_display_settings.setText('Change\ndisplay settings')
        self._button_change_display_settings.clicked.connect(self._dialog_change_display_settings)
        self._button_change_display_settings.setToolTip(
            "Change which things are rendered and how they're rendered<br><b>(Ctrl + D)</b>"
        )
        QShortcut(QKeySequence('Ctrl+D'), self).activated.connect(self._button_change_display_settings.click)

        button_reset_zoom = QPushButton(self)
        button_reset_zoom.setText('Reset zoom')
        button_reset_zoom.clicked.connect(self._reset_zoom)
        button_reset_zoom.setToolTip('Reset the zoom level back to normal<br><b>(Ctrl + Shift + R)</b>')
        QShortcut(QKeySequence('Ctrl+Shift+R'), self).activated.connect(button_reset_zoom.click)

        # Define new matrix buttons and their groupbox

        self._button_define_visually = QPushButton(self)
        self._button_define_visually.setText('Visually')
        self._button_define_visually.setToolTip('Drag the basis vectors<br><b>(Alt + 1)</b>')
        self._button_define_visually.clicked.connect(lambda: self._dialog_define_matrix(DefineVisuallyDialog))
        QShortcut(QKeySequence('Alt+1'), self).activated.connect(self._button_define_visually.click)

        self._button_define_numerically = QPushButton(self)
        self._button_define_numerically.setText('Numerically')
        self._button_define_numerically.setToolTip('Define a matrix just with numbers<br><b>(Alt + 2)</b>')
        self._button_define_numerically.clicked.connect(lambda: self._dialog_define_matrix(DefineNumericallyDialog))
        QShortcut(QKeySequence('Alt+2'), self).activated.connect(self._button_define_numerically.click)

        self._button_define_as_expression = QPushButton(self)
        self._button_define_as_expression.setText('As an expression')
        self._button_define_as_expression.setToolTip('Define a matrix in terms of other matrices<br><b>(Alt + 3)</b>')
        self._button_define_as_expression.clicked.connect(
            lambda: self._dialog_define_matrix(DefineAsExpressionDialog)
        )
        QShortcut(QKeySequence('Alt+3'), self).activated.connect(self._button_define_as_expression.click)

        vlay_define_new_matrix = QVBoxLayout()
        vlay_define_new_matrix.setSpacing(20)
        vlay_define_new_matrix.addWidget(self._button_define_visually)
        vlay_define_new_matrix.addWidget(self._button_define_numerically)
        vlay_define_new_matrix.addWidget(self._button_define_as_expression)

        groupbox_define_new_matrix = QtWidgets.QGroupBox('Define a new matrix', self)
        groupbox_define_new_matrix.setLayout(vlay_define_new_matrix)

        # Info panel button

        self._button_info_panel = QPushButton(self)
        self._button_info_panel.setText('Show defined matrices')
        self._button_info_panel.clicked.connect(
            # We have to use a lambda instead of 'InfoPanelDialog(self.matrix_wrapper, self).open' here
            # because that would create an unnamed instance of InfoPanelDialog when LintransMainWindow is
            # constructed, but we need to create a new instance every time to keep self.matrix_wrapper up to date
            lambda: InfoPanelDialog(self._matrix_wrapper, self).open()
        )
        self._button_info_panel.setToolTip(
            'Open an info panel with all matrices that have been defined in this session<br><b>(Ctrl + M)</b>'
        )
        QShortcut(QKeySequence('Ctrl+M'), self).activated.connect(self._button_info_panel.click)

        # Render buttons

        button_reset = QPushButton(self)
        button_reset.setText('Reset')
        button_reset.clicked.connect(self._reset_transformation)
        button_reset.setToolTip('Reset the visualized transformation back to the identity<br><b>(Ctrl + R)</b>')
        QShortcut(QKeySequence('Ctrl+R'), self).activated.connect(button_reset.click)

        self._button_render = QPushButton(self)
        self._button_render.setText('Render')
        self._button_render.setEnabled(False)
        self._button_render.clicked.connect(self._render_expression)
        self._button_render.setToolTip('Render the expression<br><b>(Ctrl + Enter)</b>')
        QShortcut(QKeySequence('Ctrl+Return'), self).activated.connect(self._button_render.click)

        self._button_animate = QPushButton(self)
        self._button_animate.setText('Animate')
        self._button_animate.setEnabled(False)
        self._button_animate.clicked.connect(self._animate_expression)
        self._button_animate.setToolTip('Animate the expression<br><b>(Ctrl + Shift + Enter)</b>')
        QShortcut(QKeySequence('Ctrl+Shift+Return'), self).activated.connect(self._button_animate.click)

        # === Arrange widgets

        vlay_left = QVBoxLayout()
        vlay_left.addWidget(self._plot)
        vlay_left.addWidget(self._lineedit_expression_box)

        vlay_misc_buttons = QVBoxLayout()
        vlay_misc_buttons.setSpacing(20)
        vlay_misc_buttons.addWidget(button_define_polygon)
        vlay_misc_buttons.addWidget(self._button_change_display_settings)
        vlay_misc_buttons.addWidget(button_reset_zoom)

        vlay_info_buttons = QVBoxLayout()
        vlay_info_buttons.setSpacing(20)
        vlay_info_buttons.addWidget(self._button_info_panel)

        vlay_render = QVBoxLayout()
        vlay_render.setSpacing(20)
        vlay_render.addWidget(button_reset)
        vlay_render.addWidget(self._button_animate)
        vlay_render.addWidget(self._button_render)

        vlay_right = QVBoxLayout()
        vlay_right.setSpacing(50)
        vlay_right.addLayout(vlay_misc_buttons)
        vlay_right.addItem(QSpacerItem(100, 2, hPolicy=QSizePolicy.Minimum, vPolicy=QSizePolicy.Expanding))
        vlay_right.addWidget(groupbox_define_new_matrix)
        vlay_right.addItem(QSpacerItem(100, 2, hPolicy=QSizePolicy.Minimum, vPolicy=QSizePolicy.Expanding))
        vlay_right.addLayout(vlay_info_buttons)
        vlay_right.addItem(QSpacerItem(100, 2, hPolicy=QSizePolicy.Minimum, vPolicy=QSizePolicy.Expanding))
        vlay_right.addLayout(vlay_render)

        hlay_all = QHBoxLayout()
        hlay_all.setSpacing(15)
        hlay_all.addLayout(vlay_left)
        hlay_all.addLayout(vlay_right)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(hlay_all)
        central_widget.setContentsMargins(10, 10, 10, 10)

        self.setCentralWidget(central_widget)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle a :class:`QCloseEvent` by confirming if the user wants to save, and cancelling animation."""
        if self._save_filename is None or not self._changed_since_save:
            self._animating = False
            self._animating_sequence = False
            event.accept()
            return

        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Question)
        dialog.setWindowTitle('Save changes?')
        dialog.setText(f"If you don't save, then changes made to {self._save_filename} will be lost.")
        dialog.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        dialog.setDefaultButton(QMessageBox.Save)

        pressed_button = dialog.exec()

        if pressed_button == QMessageBox.Save:
            self._save_session()

        if pressed_button in (QMessageBox.Save, QMessageBox.Discard):
            self._animating = False
            self._animating_sequence = False
            event.accept()
        else:
            event.ignore()

    def _update_render_buttons(self) -> None:
        """Enable or disable the render and animate buttons according to whether the matrix expression is valid."""
        text = self._lineedit_expression_box.text()

        # Let's say that the user defines a non-singular matrix A, then defines B as A^-1
        # If they then redefine A and make it singular, then we get a LinAlgError when
        # trying to evaluate an expression with B in it
        # To fix this, we just do naive validation rather than aware validation
        if ',' in text:
            self._button_render.setEnabled(False)

            try:
                valid = all(self._matrix_wrapper.is_valid_expression(x) for x in text.split(','))
            except LinAlgError:
                valid = all(validate_matrix_expression(x) for x in text.split(','))

            self._button_animate.setEnabled(valid)

        else:
            try:
                valid = self._matrix_wrapper.is_valid_expression(text)
            except LinAlgError:
                valid = validate_matrix_expression(text)

            self._button_render.setEnabled(valid)
            self._button_animate.setEnabled(valid)

    @pyqtSlot()
    def _reset_zoom(self) -> None:
        """Reset the zoom level back to normal."""
        self._plot.grid_spacing = self._plot.DEFAULT_GRID_SPACING
        self._plot.update()

    @pyqtSlot()
    def _reset_transformation(self) -> None:
        """Reset the visualized transformation back to the identity."""
        if self._animating or self._animating_sequence:
            self._reset_during_animation = True

        self._animating = False
        self._animating_sequence = False

        self._plot.plot_matrix(self._matrix_wrapper['I'])
        self._plot.update()

    @pyqtSlot()
    def _render_expression(self) -> None:
        """Render the transformation given by the expression in the input box."""
        try:
            matrix = self._matrix_wrapper.evaluate_expression(self._lineedit_expression_box.text())

        except LinAlgError:
            self._show_error_message('Singular matrix', 'Cannot take inverse of singular matrix.')
            return

        if self._is_matrix_too_big(matrix):
            self._show_error_message('Matrix too big', "This matrix doesn't fit on the canvas.")
            return

        self._plot.plot_matrix(matrix)
        self._plot.update()

    @pyqtSlot()
    def _animate_expression(self) -> None:
        """Animate from the current matrix to the matrix in the expression box."""
        self._button_render.setEnabled(False)
        self._button_animate.setEnabled(False)

        matrix_start: MatrixType = np.array([
            [self._plot.point_i[0], self._plot.point_j[0]],
            [self._plot.point_i[1], self._plot.point_j[1]]
        ])

        text = self._lineedit_expression_box.text()

        # If there's commas in the expression, then we want to animate each part at a time
        if ',' in text:
            current_matrix = matrix_start
            self._animating_sequence = True

            # For each expression in the list, right multiply it by the current matrix,
            # and animate from the current matrix to that new matrix
            for expr in text.split(',')[::-1]:
                if not self._animating_sequence:
                    break

                try:
                    new_matrix = self._matrix_wrapper.evaluate_expression(expr)

                    if self._plot.display_settings.applicative_animation:
                        new_matrix = new_matrix @ current_matrix
                except LinAlgError:
                    self._show_error_message('Singular matrix', 'Cannot take inverse of singular matrix.')
                    return

                self._animate_between_matrices(current_matrix, new_matrix)
                current_matrix = new_matrix

                # Here we just redraw and allow for other events to be handled while we pause
                self._plot.update()
                QApplication.processEvents()
                QThread.msleep(self._plot.display_settings.animation_pause_length)

            self._animating_sequence = False

        # If there's no commas, then just animate directly from the start to the target
        else:
            # Get the target matrix and its determinant
            try:
                matrix_target = self._matrix_wrapper.evaluate_expression(text)

            except LinAlgError:
                self._show_error_message('Singular matrix', 'Cannot take inverse of singular matrix.')
                return

            # The concept of applicative animation is explained in /gui/settings.py
            if self._plot.display_settings.applicative_animation:
                matrix_target = matrix_target @ matrix_start

            # If we want a transitional animation and we're animating the same matrix, then restart the animation
            # We use this check rather than equality because of small floating point errors
            elif (abs(matrix_start - matrix_target) < 1e-12).all():
                matrix_start = self._matrix_wrapper['I']

                # We pause here for 200 ms to make the animation look a bit nicer
                self._plot.plot_matrix(matrix_start)
                self._plot.update()
                QApplication.processEvents()
                QThread.msleep(200)

            self._animate_between_matrices(matrix_start, matrix_target)

        self._update_render_buttons()

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
        # its vectors must be perpendicular, the same length, and at right angles
        # The checks for 'abs(value) < 1e-10' are to account for floating point error
        if matrix_application is not None \
                and self._plot.display_settings.smoothen_determinant \
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

        if not self._plot.display_settings.smoothen_determinant or det_start * det_target <= 0:
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

    def _animate_between_matrices(self, matrix_start: MatrixType, matrix_target: MatrixType) -> None:
        """Animate from the start matrix to the target matrix."""
        self._animating = True

        # Making steps depend on animation_time ensures a smooth animation without
        # massive overheads for small animation times
        steps = self._plot.display_settings.animation_time // 10

        for i in range(0, steps + 1):
            if not self._animating:
                break

            matrix_to_render = self._get_animation_frame(matrix_start, matrix_target, i / steps)

            if self._is_matrix_too_big(matrix_to_render):
                self._show_error_message('Matrix too big', "This matrix doesn't fit on the canvas.")
                self._animating = False
                self._animating_sequence = False
                return

            self._plot.plot_matrix(matrix_to_render)

            # We schedule the plot to be updated, tell the event loop to
            # process events, and asynchronously sleep for 10ms
            # This allows for other events to be processed while animating, like zooming in and out
            self._plot.update()
            QApplication.processEvents()
            QThread.msleep(self._plot.display_settings.animation_time // steps)

        if not self._reset_during_animation:
            self._plot.plot_matrix(matrix_target)
        else:
            self._plot.plot_matrix(self._matrix_wrapper['I'])

        self._plot.update()

        self._animating = False
        self._reset_during_animation = False

    @pyqtSlot(DefineMatrixDialog)
    def _dialog_define_matrix(self, dialog_class: Type[DefineMatrixDialog]) -> None:
        """Open a generic definition dialog to define a new matrix.

        The class for the desired dialog is passed as an argument. We create an
        instance of this class and the dialog is opened asynchronously and modally
        (meaning it blocks interaction with the main window) with the proper method
        connected to the :meth:`QDialog.accepted` signal.

        .. note:: ``dialog_class`` must subclass :class:`~lintrans.gui.dialogs.define_new_matrix.DefineMatrixDialog`.

        :param dialog_class: The dialog class to instantiate
        :type dialog_class: Type[lintrans.gui.dialogs.define_new_matrix.DefineMatrixDialog]
        """
        # We create a dialog with a deepcopy of the current matrix_wrapper
        # This avoids the dialog mutating this one
        dialog: DefineMatrixDialog

        if dialog_class == DefineVisuallyDialog:
            dialog = DefineVisuallyDialog(
                self,
                matrix_wrapper=deepcopy(self._matrix_wrapper),
                display_settings=self._plot.display_settings,
                polygon_points=self._plot.polygon_points
            )
        else:
            dialog = dialog_class(self, matrix_wrapper=deepcopy(self._matrix_wrapper))

        # .open() is asynchronous and doesn't spawn a new event loop, but the dialog is still modal (blocking)
        dialog.open()

        # So we have to use the accepted signal to call a method when the user accepts the dialog
        dialog.accepted.connect(self._assign_matrix_wrapper)

    @pyqtSlot()
    def _assign_matrix_wrapper(self) -> None:
        """Assign a new value to ``self._matrix_wrapper`` and give the expression box focus."""
        self._matrix_wrapper = self.sender().matrix_wrapper
        self._lineedit_expression_box.setFocus()
        self._update_render_buttons()

        self._changed_since_save = True
        self._update_window_title()

    @pyqtSlot()
    def _dialog_change_display_settings(self) -> None:
        """Open the dialog to change the display settings."""
        dialog = DisplaySettingsDialog(self, display_settings=self._plot.display_settings)
        dialog.open()
        dialog.accepted.connect(self._assign_display_settings)

    @pyqtSlot()
    def _assign_display_settings(self) -> None:
        """Assign a new value to ``self._plot.display_settings`` and give the expression box focus."""
        self._plot.display_settings = self.sender().display_settings
        self._plot.update()
        self._lineedit_expression_box.setFocus()
        self._update_render_buttons()

    @pyqtSlot()
    def _dialog_define_polygon(self) -> None:
        """Open the dialog to define a polygon."""
        dialog = DefinePolygonDialog(self, polygon_points=self._plot.polygon_points)
        dialog.open()
        dialog.accepted.connect(self._assign_polygon_points)

    @pyqtSlot()
    def _assign_polygon_points(self) -> None:
        """Assign a new value to ``self._plot.polygon_points`` and give the expression box focus."""
        self._plot.polygon_points = self.sender().polygon_points
        self._plot.update()
        self._lineedit_expression_box.setFocus()
        self._update_render_buttons()

        self._changed_since_save = True
        self._update_window_title()

    def _show_error_message(self, title: str, text: str, info: str | None = None, *, warning: bool = False) -> None:
        """Show an error message in a dialog box.

        :param str title: The window title of the dialog box
        :param str text: The simple error message
        :param info: The more informative error message
        :type info: Optional[str]
        """
        dialog = QMessageBox(self)
        dialog.setWindowTitle(title)
        dialog.setText(text)

        if warning:
            dialog.setIcon(QMessageBox.Warning)
        else:
            dialog.setIcon(QMessageBox.Critical)

        if info is not None:
            dialog.setInformativeText(info)

        dialog.open()

        # This is `finished` rather than `accepted` because we want to update the buttons no matter what
        dialog.finished.connect(self._update_render_buttons)

    def _is_matrix_too_big(self, matrix: MatrixType) -> bool:
        """Check if the given matrix will actually fit onto the canvas.

        Convert the elements of the matrix to canvas coords and make sure they fit within Qt's 32-bit integer limit.

        :param MatrixType matrix: The matrix to check
        :returns bool: Whether the matrix is too big to fit on the canvas
        """
        coords: List[Tuple[int, int]] = [self._plot.canvas_coords(*vector) for vector in matrix.T]

        for x, y in coords:
            if not (-2147483648 <= x <= 2147483647 and -2147483648 <= y <= 2147483647):
                return True

        return False

    def _update_window_title(self) -> None:
        """Update the window title to reflect whether the session has changed since it was last saved."""
        title = 'lintrans'

        if self._save_filename:
            title = os.path.split(self._save_filename)[-1] + ' - ' + title

            if self._changed_since_save:
                title = '*' + title

        self.setWindowTitle(title)

    def _reset_session(self) -> None:
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
            self._matrix_wrapper = MatrixWrapper()

            self._lineedit_expression_box.setText('I')
            self._render_expression()
            self._lineedit_expression_box.setText('')
            self._lineedit_expression_box.setFocus()
            self._update_render_buttons()

            self._save_filename = None
            self._changed_since_save = False
            self._update_window_title()

    def open_session_file(self, filename: str) -> None:
        """Open the given session file.

        If the selected file is not a valid lintrans session file, we just show an error message,
        but if it's valid, we load it and set it as the default filename for saving.
        """
        try:
            session, version, extra_attrs = Session.load_from_file(filename)

        # load_from_file() can raise errors if the contents is not a valid pickled Python object,
        # or if the pickled Python object is of the wrong type
        except (AttributeError, EOFError, FileNotFoundError, ValueError, UnpicklingError):
            self._show_error_message(
                'Invalid file contents',
                'This is not a valid lintrans session file.',
                'Not all .lt files are lintrans session files. This file was probably created by an unrelated '
                'program.'
            )
            return

        missing_parts = False

        if session.matrix_wrapper is not None:
            self._matrix_wrapper = session.matrix_wrapper
        else:
            missing_parts = True  # type: ignore[unreachable]

        if session.polygon_points is not None:
            self._plot.polygon_points = session.polygon_points
        else:
            missing_parts = True  # type: ignore[unreachable]

        if missing_parts:
            if version != lintrans.__version__:
                info = f"This may be a version conflict. This file was saved with lintrans v{version} " \
                       f"but you're running lintrans v{lintrans.__version__}."
            else:
                info = None

            self._show_error_message(
                'Session file missing parts',
                'This session file is missing certain elements. It may not work correctly.',
                info,
                warning=True
            )
        elif extra_attrs:
            if version != lintrans.__version__:
                info = f"This may be a version conflict. This file was saved with lintrans v{version} " \
                       f"but you're running lintrans v{lintrans.__version__}."
            else:
                info = None

            self._show_error_message(
                'Session file has extra parts',
                'This session file has more parts than expected. It will work correctly, '
                'but you might be missing some features.',
                info,
                warning=True
            )

        self._lineedit_expression_box.setText('I')
        self._render_expression()
        self._lineedit_expression_box.setText('')
        self._lineedit_expression_box.setFocus()
        self._update_render_buttons()

        # Set this as the default filename if we could read it properly
        self._save_filename = filename
        self._changed_since_save = False
        self._update_window_title()

    @pyqtSlot()
    def _ask_for_session_file(self) -> None:
        """Ask the user to select a session file, and then open it and load the session."""
        dialog = QFileDialog(
            self,
            'Open a session',
            global_settings.get_save_directory(),
            'lintrans sessions (*.lt)'
        )
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setViewMode(QFileDialog.List)

        if dialog.exec():
            self.open_session_file(dialog.selectedFiles()[0])

    @pyqtSlot()
    def _save_session(self) -> None:
        """Save the session to the given file.

        If ``self._save_filename`` is ``None``, then call :meth:`_save_session_as` and return.
        """
        if self._save_filename is None:
            self._save_session_as()
            return

        Session(
            matrix_wrapper=self._matrix_wrapper,
            polygon_points=self._plot.polygon_points
        ).save_to_file(self._save_filename)

        self._changed_since_save = False
        self._update_window_title()

    @pyqtSlot()
    def _save_session_as(self) -> None:
        """Ask the user for a file to save the session to, and then call :meth:`_save_session`.

        .. note::
           If the user doesn't select a file to save the session to, then the session
           just doesn't get saved, and :meth:`_save_session` is never called.
        """
        dialog = FileSelectDialog(
            self,
            'Save this session',
            global_settings.get_save_directory(),
            'lintrans sessions (*.lt)'
        )
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setViewMode(QFileDialog.List)
        dialog.setDefaultSuffix('.lt')

        if dialog.exec():
            filename = dialog.selectedFiles()[0]
            self._save_filename = filename
            self._save_session()


def main(filename: Optional[str]) -> None:
    """Run the GUI by creating and showing an instance of :class:`LintransMainWindow`.

    :param Optional[str] filename: A session file to optionally open at startup
    """
    app = QApplication([])
    app.setApplicationName('lintrans')
    app.setApplicationVersion(lintrans.__version__)

    qapp().setStyle(QStyleFactory.create('fusion'))

    window = LintransMainWindow()
    window.show()

    if filename:
        window.open_session_file(filename)

    sys.exit(app.exec_())
