# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides the actual widgets that can be used to visualize transformations in the GUI."""

from __future__ import annotations

import operator
from math import dist
from typing import List, Optional, Tuple

import numpy as np
from PyQt5.QtCore import Qt, QPointF, pyqtSlot
from PyQt5.QtGui import QBrush, QColor, QMouseEvent, QPainter, QPaintEvent, QPen, QPolygonF

from lintrans.typing_ import MatrixType
from lintrans.gui.settings import DisplaySettings
from .classes import InteractivePlot, VectorGridPlot


class VisualizeTransformationWidget(VectorGridPlot):
    """This widget is used in the main window to visualize transformations.

    It handles all the rendering itself, and the only method that the user needs to care about
    is :meth:`plot_matrix`, which allows you to visualize the given matrix transformation.
    """

    def __init__(self, *args, display_settings: DisplaySettings, polygon_points: List[Tuple[float, float]], **kwargs):
        """Create the widget and assign its display settings, passing ``*args`` and ``**kwargs`` to super."""
        super().__init__(*args, **kwargs)

        self.display_settings = display_settings
        self.polygon_points = polygon_points

    def plot_matrix(self, matrix: MatrixType) -> None:
        """Plot the given matrix on the grid by setting the basis vectors.

        .. warning:: This method does not call ``update()``. This must be done by the caller.

        :param MatrixType matrix: The matrix to plot
        """
        self.point_i = (matrix[0][0], matrix[1][0])
        self.point_j = (matrix[0][1], matrix[1][1])

    def _draw_polygon_from_points(self, painter: QPainter, points: List[Tuple[float, float]]) -> None:
        """Draw a polygon from a given list of points.

        This is a helper method for :meth:`_draw_untransformed_polygon` and :meth:`_draw_transformed_polygon`.
        """
        if len(points) > 2:
            painter.drawPolygon(QPolygonF(
                [QPointF(*self.canvas_coords(*p)) for p in points]
            ))
        elif len(points) == 2:
            painter.drawLine(
                *self.canvas_coords(*points[0]),
                *self.canvas_coords(*points[1])
            )

    def _draw_untransformed_polygon(self, painter: QPainter) -> None:
        """Draw the original untransformed polygon with a dashed line."""
        pen = QPen(self._PEN_POLYGON)
        pen.setDashPattern([4, 4])
        painter.setPen(pen)

        self._draw_polygon_from_points(painter, self.polygon_points)

    def _draw_transformed_polygon(self, painter: QPainter) -> None:
        """Draw the transformed version of the polygon."""
        if len(self.polygon_points) == 0:
            return

        painter.setPen(self._PEN_POLYGON)

        # This transpose trick lets us do one matrix multiplication to transform every point in the polygon
        # I learned this from Phil. Thanks Phil
        self._draw_polygon_from_points(
            painter,
            (self._matrix @ np.array(self.polygon_points).T).T
        )

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

        if self.display_settings.draw_untransformed_polygon:
            self._draw_untransformed_polygon(painter)

        if self.display_settings.draw_transformed_polygon:
            self._draw_transformed_polygon(painter)

        painter.end()
        event.accept()


class DefineMatrixVisuallyWidget(VisualizeTransformationWidget, InteractivePlot):
    """This widget allows the user to visually define a matrix.

    This is just the widget itself. If you want the dialog, use
    :class:`lintrans.gui.dialogs.define_new_matrix.DefineVisuallyDialog`.
    """

    def __init__(self, *args, display_settings: DisplaySettings, polygon_points: List[Tuple[float, float]], **kwargs):
        """Create the widget and enable mouse tracking. ``*args`` and ``**kwargs`` are passed to ``super()``."""
        super().__init__(*args, display_settings=display_settings, polygon_points=polygon_points, **kwargs)

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


class DefinePolygonWidget(InteractivePlot):
    """This widget allows the user to define a polygon by clicking and dragging points on the canvas."""

    _BRUSH_NONE: QBrush = QBrush(Qt.NoBrush)
    """This is a brush with ``Qt::NoBrush``. See :cpp:enum:`Qt::BrushStyle`."""

    _BRUSH_DEFINE_POLYGON_VERTEX: QBrush = QBrush(QColor('#FFFFFF'), Qt.SolidPattern)
    """This is the brush used to draw the inside of the vertices when defining a polygon."""

    def __init__(self, *args, polygon_points: List[Tuple[float, float]], **kwargs):
        """Create the widget with a list of points and a dragged point index."""
        super().__init__(*args, **kwargs)

        self._dragged_point_index: Optional[int] = None
        self.points = polygon_points.copy()

    @pyqtSlot()
    def reset_polygon(self) -> None:
        """Reset the polygon and update the widget."""
        self.points = []
        self.update()

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

            new_point = self._round_to_int_coord(grid_pos)

            if len(self.points) < 2:
                self.points.append(new_point)
                self._dragged_point_index = -1
            else:
                # FIXME: This algorithm doesn't work very well when the new point is far away
                # from the existing polygon; it just picks the longest side

                # Get a list of line segments and a list of their lengths
                line_segments = list(zip(self.points, self.points[1:])) + [(self.points[-1], self.points[0])]
                segment_lengths = map(lambda t: dist(*t), line_segments)

                # Get the distance from each point in the polygon to the new point
                distances_to_point = [dist(p, new_point) for p in self.points]

                # For each pair of list-adjacent points, zip their distances to
                # the new point into a tuple, and add them together
                # This gives us the lengths of the catheti of the triangles that
                # connect the new point to each pair of adjacent points
                dist_to_point_pairs = list(zip(distances_to_point, distances_to_point[1:])) + \
                    [(distances_to_point[-1], distances_to_point[0])]

                # mypy doesn't like the use of sum for some reason. Just ignore it
                point_triangle_lengths = map(sum, dist_to_point_pairs)  # type: ignore[arg-type]

                # The normalized distance is the sum of the distances to the ends of the line segment
                # (point_triangle_lengths) divided by the length of the segment
                normalized_distances = list(map(operator.truediv, point_triangle_lengths, segment_lengths))

                # Get the best distance and insert this new point just after the point with that index
                # This will put it in the middle of the closest line segment
                best_distance = min(normalized_distances)
                index = 1 + normalized_distances.index(best_distance)

                self.points.insert(index, new_point)
                self._dragged_point_index = index

        elif event.button() == Qt.RightButton:
            for i, point in enumerate(self.points):
                if self._is_within_epsilon(canvas_pos, point):
                    self.points.pop(i)
                    break

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

        painter.setPen(self._PEN_POLYGON)

        if len(self.points) > 2:
            painter.drawPolygon(QPolygonF(
                [QPointF(*self.canvas_coords(*p)) for p in self.points]
            ))
        elif len(self.points) == 2:
            painter.drawLine(
                *self.canvas_coords(*self.points[0]),
                *self.canvas_coords(*self.points[1])
            )

        painter.setBrush(self._BRUSH_DEFINE_POLYGON_VERTEX)

        for point in self.points:
            x, y = self.canvas_coords(*point)

            painter.setPen(self._PEN_NONE)
            painter.drawPie(
                x - self._CURSOR_EPSILON,
                y - self._CURSOR_EPSILON,
                2 * self._CURSOR_EPSILON,
                2 * self._CURSOR_EPSILON,
                0,
                16 * 360
            )

            painter.setPen(self._PEN_POLYGON)
            painter.drawArc(
                x - self._CURSOR_EPSILON,
                y - self._CURSOR_EPSILON,
                2 * self._CURSOR_EPSILON,
                2 * self._CURSOR_EPSILON,
                0,
                16 * 360
            )

        painter.setBrush(self._BRUSH_NONE)

        painter.end()
        event.accept()
