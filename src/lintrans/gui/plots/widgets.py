# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides the actual widgets that can be used to visualize transformations in the GUI."""

from __future__ import annotations

from typing import List, Optional, Tuple

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QBrush, QColor, QMouseEvent, QPainter, QPaintEvent, QPen, QPolygonF

from lintrans.typing_ import MatrixType
from lintrans.gui.settings import DisplaySettings
from .classes import BackgroundPlot, InteractivePlot, VectorGridPlot


class VisualizeTransformationWidget(VectorGridPlot):
    """This widget is used in the main window to visualize transformations.

    It handles all the rendering itself, and the only method that the user needs to care about
    is :meth:`plot_matrix`, which allows you to visualize the given matrix transformation.
    """

    def __init__(self, *args, display_settings: DisplaySettings, **kwargs):
        """Create the widget and assign its display settings, passing ``*args`` and ``**kwargs`` to super."""
        super().__init__(*args, **kwargs)

        self.display_settings = display_settings

    def plot_matrix(self, matrix: MatrixType) -> None:
        """Plot the given matrix on the grid by setting the basis vectors.

        .. warning:: This method does not call ``update()``. This must be done by the caller.

        :param MatrixType matrix: The matrix to plot
        """
        self.point_i = (matrix[0][0], matrix[1][0])
        self.point_j = (matrix[0][1], matrix[1][1])

    def paintEvent(self, event: QPaintEvent) -> None:
        """Handle a :class:`QPaintEvent` by drawing the background grid and the transformed grid.

        The transformed grid is defined by the basis vectors i and j, which can be controlled
        with the :meth:`plot_matrix` method.
        """
        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)

        self._draw_background(painter, self.display_settings.draw_background_grid)

        if self.display_settings.draw_eigenlines:
            self._draw_eigenlines(painter)

        if self.display_settings.draw_eigenvectors:
            self._draw_eigenvectors(painter)

        if self.display_settings.draw_determinant_parallelogram:
            self._draw_determinant_parallelogram(painter)

            if self.display_settings.show_determinant_value:
                self._draw_determinant_text(painter)

        if self.display_settings.draw_transformed_grid:
            self._draw_transformed_grid(painter)

        if self.display_settings.draw_basis_vectors:
            self._draw_basis_vectors(painter)

        if self.display_settings.label_basis_vectors:
            self._draw_basis_vector_labels(painter)

        painter.end()
        event.accept()


class DefineVisuallyWidget(VisualizeTransformationWidget, InteractivePlot):
    """This widget allows the user to visually define a matrix.

    This is just the widget itself. If you want the dialog, use
    :class:`lintrans.gui.dialogs.define_new_matrix.DefineVisuallyDialog`.
    """

    def __init__(self, *args, display_settings: DisplaySettings, **kwargs):
        """Create the widget and enable mouse tracking. ``*args`` and ``**kwargs`` are passed to ``super()``."""
        super().__init__(*args, display_settings=display_settings, **kwargs)

        self._dragged_point: Tuple[float, float] | None = None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Set the dragged point if the cursor is within :attr:`_CURSOR_EPSILON`."""
        cursor_pos = (event.x(), event.y())
        button = event.button()

        if button != Qt.LeftButton:
            event.ignore()
            return

        for point in (self.point_i, self.point_j):
            if self._is_within_epsilon(cursor_pos, point):
                self._dragged_point = point[0], point[1]

        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle the mouse click being released by unsetting the dragged point."""
        if event.button() == Qt.LeftButton:
            self._dragged_point = None
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle the mouse moving on the canvas."""
        if self._dragged_point is None:
            event.ignore()
            return

        x, y = self._round_to_int_coord(self._grid_coords(event.x(), event.y()))

        if self._dragged_point == self.point_i:
            self.point_i = x, y

        elif self._dragged_point == self.point_j:
            self.point_j = x, y

        self._dragged_point = x, y

        self.update()

        event.accept()


class DefinePolygonWidget(InteractivePlot, BackgroundPlot):
    """This widget allows the user to define a polygon by clicking and dragging points on the canvas."""

    def __init__(self, *args, **kwargs):
        """Create the widget with a list of points and a dragged point index."""
        super().__init__(*args, **kwargs)

        self._dragged_point_index: Optional[int] = None
        self.points: List[Tuple[float, float]] = []

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle the mouse being clicked by adding a point or setting the dragged point index to an existing point."""
        if event.button() not in (Qt.LeftButton, Qt.RightButton):
            event.ignore()
            return

        canvas_pos = (event.x(), event.y())
        grid_pos = self._grid_coords(*canvas_pos)

        if event.button() == Qt.LeftButton:
            for i, point in enumerate(self.points):
                if self._is_within_epsilon(canvas_pos, point):
                    self._dragged_point_index = i
                    event.accept()
                    return

            self.points.append(self._round_to_int_coord(grid_pos))
            self._dragged_point_index = -1

        elif event.button() == Qt.RightButton:
            for i, point in enumerate(self.points):
                if self._is_within_epsilon(canvas_pos, point):
                    self.points.pop(i)

        self.update()

        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle the mouse click being released by unsetting the dragged point index."""
        if event.button() == Qt.LeftButton:
            self._dragged_point_index = None
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse movement by dragging the selected point."""
        if self._dragged_point_index is None:
            event.ignore()
            return

        x, y = self._round_to_int_coord(self._grid_coords(event.x(), event.y()))

        self.points[self._dragged_point_index] = x, y

        self.update()

        event.accept()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Draw the polygon on the canvas."""
        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)

        self._draw_background(painter, True)

        pen_polygon = QPen(QColor('#000000'), 1.5)
        painter.setPen(pen_polygon)

        if len(self.points) > 2:
            painter.drawPolygon(QPolygonF(
                [QPointF(*self.canvas_coords(*p)) for p in self.points]
            ))

        for point in self.points:
            x, y = self.canvas_coords(*point)

            painter.setBrush(QBrush(QColor('#FFFFFF'), Qt.SolidPattern))
            painter.setPen(QPen(Qt.NoPen))
            painter.drawPie(
                x - self._CURSOR_EPSILON,
                y - self._CURSOR_EPSILON,
                2 * self._CURSOR_EPSILON,
                2 * self._CURSOR_EPSILON,
                0,
                16 * 360
            )

            painter.setPen(pen_polygon)
            painter.drawArc(
                x - self._CURSOR_EPSILON,
                y - self._CURSOR_EPSILON,
                2 * self._CURSOR_EPSILON,
                2 * self._CURSOR_EPSILON,
                0,
                16 * 360
            )

        painter.setBrush(QBrush(Qt.NoBrush))

        painter.end()
        event.accept()
