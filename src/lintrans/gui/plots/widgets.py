# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides the actual widgets that can be used to visualize transformations in the GUI."""

from __future__ import annotations

from math import ceil, dist, floor
from typing import List, Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent, QPainter, QPaintEvent

from lintrans.typing_ import MatrixType
from lintrans.gui.settings import DisplaySettings
from .classes import VectorGridPlot


class VisualizeTransformationWidget(VectorGridPlot):
    """This class is the widget that is used in the main window to visualize transformations.

    It handles all the rendering itself, and the only method that the user needs to
    worry about is :meth:`visualize_matrix_transformation`, which allows you to visualize
    the given matrix transformation.
    """

    def __init__(self, *args, display_settings: DisplaySettings, **kwargs):
        """Create the widget and assign its display settings, passing ``*args`` and ``**kwargs`` to super."""
        super().__init__(*args, **kwargs)

        self.display_settings = display_settings

    def visualize_matrix_transformation(self, matrix: MatrixType) -> None:
        """Transform the grid by the given matrix.

        .. warning:: This method does not call ``update()``. This must be done by the caller.

        .. note::
           This method transforms the background grid, not the basis vectors. This
           means that it cannot be used to compose transformations. Compositions
           should be done by the user.

        :param MatrixType matrix: The matrix to transform by
        """
        self.point_i = (matrix[0][0], matrix[1][0])
        self.point_j = (matrix[0][1], matrix[1][1])

    def paintEvent(self, event: QPaintEvent) -> None:
        """Handle a :class:`QPaintEvent` by drawing the background grid and the transformed grid.

        The transformed grid is defined by the basis vectors i and j, which can
        be controlled with the :meth:`visualize_matrix_transformation` method.
        """
        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)

        self.draw_background(painter, self.display_settings.draw_background_grid)

        if self.display_settings.draw_eigenlines:
            self.draw_eigenlines(painter)

        if self.display_settings.draw_eigenvectors:
            self.draw_eigenvectors(painter)

        if self.display_settings.draw_determinant_parallelogram:
            self.draw_determinant_parallelogram(painter)

            if self.display_settings.show_determinant_value:
                self.draw_determinant_text(painter)

        if self.display_settings.draw_transformed_grid:
            self.draw_transformed_grid(painter)

        if self.display_settings.draw_basis_vectors:
            self.draw_basis_vectors(painter)

        painter.end()
        event.accept()


class DefineVisuallyWidget(VisualizeTransformationWidget):
    """This class is the widget that allows the user to visually define a matrix.

    This is just the widget itself. If you want the dialog, use
    :class:`lintrans.gui.dialogs.define_new_matrix.DefineVisuallyDialog`.
    """

    def __init__(self, *args, display_settings: DisplaySettings, **kwargs):
        """Create the widget and enable mouse tracking. ``*args`` and ``**kwargs`` are passed to ``super()``."""
        super().__init__(*args, display_settings=display_settings, **kwargs)

        self.dragged_point: Tuple[float, float] | None = None

        # This is the distance that the cursor needs to be from the point to drag it
        self.epsilon: int = 5

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle a :class:`QMouseEvent` when the user presses a button."""
        mx = event.x()
        my = event.y()
        button = event.button()

        if button != Qt.LeftButton:
            event.ignore()
            return

        for point in (self.point_i, self.point_j):
            px, py = self.canvas_coords(*point)
            if abs(px - mx) <= self.epsilon and abs(py - my) <= self.epsilon:
                self.dragged_point = point[0], point[1]

        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle a :class:`QMouseEvent` when the user releases a button."""
        if event.button() == Qt.LeftButton:
            self.dragged_point = None
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle the mouse moving on the canvas."""
        mx = event.x()
        my = event.y()

        if self.dragged_point is None:
            event.ignore()
            return

        x, y = self.grid_coords(mx, my)

        possible_snaps: List[Tuple[int, int]] = [
            (floor(x), floor(y)),
            (floor(x), ceil(y)),
            (ceil(x), floor(y)),
            (ceil(x), ceil(y))
        ]

        snap_distances: List[Tuple[float, Tuple[int, int]]] = [
            (dist((x, y), coord), coord)
            for coord in possible_snaps
        ]

        for snap_dist, coord in snap_distances:
            if snap_dist < 0.1:
                x, y = coord

        if self.dragged_point == self.point_i:
            self.point_i = x, y

        elif self.dragged_point == self.point_j:
            self.point_j = x, y

        self.dragged_point = x, y

        self.update()

        event.accept()
