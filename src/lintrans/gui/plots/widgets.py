"""This module provides the actual widgets that can be used to visualize transformations in the GUI."""

from __future__ import annotations

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent, QPainter, QPaintEvent, QPen

from .classes import VectorGridPlot
from lintrans.typing import MatrixType


class VisualizeTransformationWidget(VectorGridPlot):
    """This class is the widget that is used in the main window to visualize transformations.

    It handles all the rendering itself, and the only method that the user needs to
    worry about is :meth:`visualize_matrix_transformation`, which allows you to visualise
    the given matrix transformation.
    """

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
        """Handle a ``QPaintEvent`` by drawing the background grid and the transformed grid.

        The transformed grid is defined by the basis vectors i and j, which can
        be controlled with the :meth:`visualize_matrix_transformation` method.
        """
        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)

        self.draw_background(painter)
        self.draw_transformed_grid(painter)
        self.draw_vector_arrowheads(painter)

        painter.end()
        event.accept()


class DefineVisuallyWidget(VisualizeTransformationWidget):
    """This class is the widget that allows the user to visually define a matrix.

    This is just the widget itself. If you want the dialog, use
    :class:`lintrans.gui.dialogs.define_new_matrix.DefineVisuallyDialog`.
    """

    def __init__(self, *args, **kwargs):
        """Create the widget and enable mouse tracking. ``*args`` and ``**kwargs`` are passed to ``super()``."""
        super().__init__(*args, **kwargs)

        # self.setMouseTracking(True)
        self.dragged_point: tuple[float, float] | None = None

        # This is the distance that the cursor needs to be from the point to drag it
        self.epsilon: int = 5

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle a QMouseEvent when the user pressed a button."""
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
        """Handle a QMouseEvent when the user release a button."""
        if event.button() == Qt.LeftButton:
            self.dragged_point = None
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle the mouse moving on the canvas."""
        mx = event.x()
        my = event.y()

        if self.dragged_point is not None:
            x, y = self.grid_coords(mx, my)

            if self.dragged_point == self.point_i:
                self.point_i = x, y

            elif self.dragged_point == self.point_j:
                self.point_j = x, y

            self.dragged_point = x, y

            self.update()

            print(self.dragged_point)
            print(self.point_i, self.point_j)

            event.accept()

        event.ignore()
