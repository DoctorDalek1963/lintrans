# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides superclasses for plotting transformations."""

from __future__ import annotations

from abc import abstractmethod
from math import ceil, dist, floor
from typing import Iterable, List, Optional, Tuple

import numpy as np
from PyQt5.QtCore import QPoint, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QMouseEvent, QPainter, QPainterPath, QPaintEvent, QPen, QWheelEvent
from PyQt5.QtWidgets import QWidget

from lintrans.typing_ import MatrixType, VectorType


class BackgroundPlot(QWidget):
    """This class provides a background for plotting, as well as setup for a Qt widget.

    This class provides a background (untransformed) plane, and all the backend
    details for a Qt application, but does not provide useful functionality. To
    be useful, this class must be subclassed and behaviour must be implemented
    by the subclass.

    .. warning:: This class should never be directly instantiated, only subclassed.

    .. note::
       I would make this class have ``metaclass=abc.ABCMeta``, but I can't because it subclasses :class:`QWidget`,
       and every superclass of a class must have the same metaclass, and :class:`QWidget` is not an abstract class.
    """

    DEFAULT_GRID_SPACING: int = 85
    """This is the starting spacing between grid lines (in pixels)."""

    _MINIMUM_GRID_SPACING: int = 5
    """This is the minimum spacing between grid lines (in pixels)."""

    _COLOUR_BACKGROUND_GRID: QColor = QColor('#808080')
    """This is the colour of the background grid lines."""

    _COLOUR_BACKGROUND_AXES: QColor = QColor('#000000')
    """This is the colour of the background axes."""

    _WIDTH_BACKGROUND_GRID: float = 0.3
    """This is the width of the background grid lines, as a multiple of the :class:`QPainter` line width."""

    _PEN_NONE: QPen = QPen(Qt.NoPen)
    """This is a pen with ``Qt::NoPen``. See :cpp:enum:`Qt::PenStyle`."""

    _PEN_POLYGON: QPen = QPen(QColor('#000000'), 1.5)
    """This is the pen used to draw the normal polygon."""

    _PEN_POLYGON_DASHED: QPen = QPen(QColor('#000000'), 1.2, Qt.DashLine)
    """This is the pen used to draw a dashed line for the untransformed polygon."""

    def __init__(self, *args, **kwargs):
        """Create the widget and setup backend stuff for rendering.

        .. note:: ``*args`` and ``**kwargs`` are passed the superclass constructor (:class:`QWidget`).
        """
        super().__init__(*args, **kwargs)

        self.setAutoFillBackground(True)

        # Set the background to white
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)

        self.grid_spacing = self.DEFAULT_GRID_SPACING

    @property
    def _canvas_origin(self) -> Tuple[int, int]:
        """Return the canvas coords of the grid origin.

        The return value is intended to be unpacked and passed to a :meth:`QPainter.drawLine:iiii` call.

        See :meth:`canvas_coords`.

        :returns: The canvas coordinates of the grid origin
        :rtype: Tuple[int, int]
        """
        return self.width() // 2, self.height() // 2

    def _canvas_x(self, x: float) -> int:
        """Convert an x coordinate from grid coords to canvas coords."""
        return int(self._canvas_origin[0] + x * self.grid_spacing)

    def _canvas_y(self, y: float) -> int:
        """Convert a y coordinate from grid coords to canvas coords."""
        return int(self._canvas_origin[1] - y * self.grid_spacing)

    def canvas_coords(self, x: float, y: float) -> Tuple[int, int]:
        """Convert a coordinate from grid coords to canvas coords.

        This method is intended to be used like

        .. code::

           painter.drawLine(*self.canvas_coords(x1, y1), *self.canvas_coords(x2, y2))

        or like

        .. code::

           painter.drawLine(*self._canvas_origin, *self.canvas_coords(x, y))

        See :attr:`_canvas_origin`.

        :param float x: The x component of the grid coordinate
        :param float y: The y component of the grid coordinate
        :returns: The resultant canvas coordinates
        :rtype: Tuple[int, int]
        """
        return self._canvas_x(x), self._canvas_y(y)

    def _grid_corner(self) -> Tuple[float, float]:
        """Return the grid coords of the top right corner."""
        return self.width() / (2 * self.grid_spacing), self.height() / (2 * self.grid_spacing)

    def _grid_coords(self, x: int, y: int) -> Tuple[float, float]:
        """Convert a coordinate from canvas coords to grid coords.

        :param int x: The x component of the canvas coordinate
        :param int y: The y component of the canvas coordinate
        :returns: The resultant grid coordinates
        :rtype: Tuple[float, float]
        """
        # We get the maximum grid coords and convert them into canvas coords
        return (x - self._canvas_origin[0]) / self.grid_spacing, (-y + self._canvas_origin[1]) / self.grid_spacing

    @abstractmethod
    def paintEvent(self, event: QPaintEvent) -> None:
        """Handle a :class:`QPaintEvent`.

        .. note:: This method is abstract and must be overridden by all subclasses.
        """

    def _draw_background(self, painter: QPainter, draw_grid: bool) -> None:
        """Draw the background grid.

        .. note:: This method is just a utility method for subclasses to use to render the background grid.

        :param QPainter painter: The painter to draw the background with
        :param bool draw_grid: Whether to draw the grid lines
        """
        if draw_grid:
            painter.setPen(QPen(self._COLOUR_BACKGROUND_GRID, self._WIDTH_BACKGROUND_GRID))

            # Draw equally spaced vertical lines, starting in the middle and going out
            # We loop up to half of the width. This is because we draw a line on each side in each iteration
            for x in range(self.width() // 2 + self.grid_spacing, self.width(), self.grid_spacing):
                painter.drawLine(x, 0, x, self.height())
                painter.drawLine(self.width() - x, 0, self.width() - x, self.height())

            # Same with the horizontal lines
            for y in range(self.height() // 2 + self.grid_spacing, self.height(), self.grid_spacing):
                painter.drawLine(0, y, self.width(), y)
                painter.drawLine(0, self.height() - y, self.width(), self.height() - y)

        # Now draw the axes
        painter.setPen(QPen(self._COLOUR_BACKGROUND_AXES, self._WIDTH_BACKGROUND_GRID))
        painter.drawLine(self.width() // 2, 0, self.width() // 2, self.height())
        painter.drawLine(0, self.height() // 2, self.width(), self.height() // 2)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle a :class:`QWheelEvent` by zooming in or our of the grid."""
        # angleDelta() returns a number of units equal to 8 times the number of degrees rotated
        degrees = event.angleDelta() / 8

        if degrees is not None:
            new_spacing = max(1, self.grid_spacing + degrees.y())

            if new_spacing >= self._MINIMUM_GRID_SPACING:
                self.grid_spacing = new_spacing

        event.accept()
        self.update()


class InteractivePlot(BackgroundPlot):
    """This class represents an interactive plot, which may allow the user to click and/or drag point(s)."""

    _CURSOR_EPSILON: int = 5
    """This is the distance (in pixels) that the cursor needs to be from the point to drag it."""

    _SNAP_DIST = 0.1
    """This is the distance (in grid coords) that the cursor needs to be from an integer point to snap to it."""

    def _round_to_int_coord(self, point: Tuple[float, float]) -> Tuple[float, float]:
        """Take a coordinate in grid coords and round it to an integer coordinate if it's within :attr:`_SNAP_DIST`.

        If the point is not close enough, we just return the original point.
        """
        x, y = point

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
            if snap_dist < self._SNAP_DIST:
                x, y = coord

        return x, y

    def _is_within_epsilon(self, cursor_pos: Tuple[float, float], point: Tuple[float, float]) -> bool:
        """Check if the cursor position (in canvas coords) is within range of the given point."""
        mx, my = cursor_pos
        px, py = self.canvas_coords(*point)
        return (abs(px - mx) <= self._CURSOR_EPSILON and abs(py - my) <= self._CURSOR_EPSILON)

    @abstractmethod
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle the mouse being pressed."""

    @abstractmethod
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle the mouse being released."""

    @abstractmethod
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle the mouse moving on the widget."""


class VectorGridPlot(BackgroundPlot):
    """This class represents a background plot, with vectors and their grid drawn on top.

    This class should be subclassed to be used for visualization and matrix definition widgets.
    All useful behaviour should be implemented by any subclass.

    .. warning:: This class should never be directly instantiated, only subclassed.
    """

    _COLOUR_I = QColor('#0808d8')
    """This is the colour of the `i` basis vector and associated transformed grid lines."""

    _COLOUR_J = QColor('#e90000')
    """This is the colour of the `j` basis vector and associated transformed grid lines."""

    _COLOUR_EIGEN = QColor('#13cf00')
    """This is the colour of the eigenvectors and eigenlines (the spans of the eigenvectors)."""

    _COLOUR_TEXT = QColor('#000000')
    """This is the colour of the text."""

    _WIDTH_VECTOR_LINE = 1.8
    """This is the width of the transformed basis vector lines, as a multiple of the :class:`QPainter` line width."""

    _WIDTH_TRANSFORMED_GRID = 0.8
    """This is the width of the transformed grid lines, as a multiple of the :class:`QPainter` line width."""

    _ARROWHEAD_LENGTH = 0.15
    """This is the minimum length (in grid coord size) of the arrowhead parts."""

    _MAX_PARALLEL_LINES = 150
    """This is the maximum number of parallel transformed grid lines that will be drawn.

    The user can zoom out further, but we will stop drawing grid lines beyond this number.
    """

    def __init__(self, *args, **kwargs):
        """Create the widget with ``point_i`` and ``point_j`` attributes.

        .. note:: ``*args`` and ``**kwargs`` are passed to the superclass constructor (:class:`BackgroundPlot`).
        """
        super().__init__(*args, **kwargs)

        self.point_i: Tuple[float, float] = (1., 0.)
        self.point_j: Tuple[float, float] = (0., 1.)

    @property
    def _matrix(self) -> MatrixType:
        """Return the assembled matrix of the basis vectors."""
        return np.array([
            [self.point_i[0], self.point_j[0]],
            [self.point_i[1], self.point_j[1]]
        ])

    @property
    def _det(self) -> float:
        """Return the determinant of the assembled matrix."""
        return float(np.linalg.det(self._matrix))

    @property
    def _eigs(self) -> 'Iterable[Tuple[float, VectorType]]':
        """Return the eigenvalues and eigenvectors zipped together to be iterated over.

        :rtype: Iterable[Tuple[float, VectorType]]
        """
        values, vectors = np.linalg.eig(self._matrix)
        return zip(values, vectors.T)

    @abstractmethod
    def paintEvent(self, event: QPaintEvent) -> None:
        """Handle a :class:`QPaintEvent`.

        .. note:: This method is abstract and must be overridden by all subclasses.
        """

    def _draw_parallel_lines(self, painter: QPainter, vector: Tuple[float, float], point: Tuple[float, float]) -> None:
        """Draw a set of evenly spaced grid lines parallel to ``vector`` intersecting ``point``.

        :param QPainter painter: The painter to draw the lines with
        :param vector: The vector to draw the grid lines parallel to
        :type vector: Tuple[float, float]
        :param point: The point for the lines to intersect with
        :type point: Tuple[float, float]
        """
        max_x, max_y = self._grid_corner()
        vector_x, vector_y = vector
        point_x, point_y = point

        # If the determinant is 0
        if abs(vector_x * point_y - vector_y * point_x) < 1e-12:
            rank = np.linalg.matrix_rank(
                np.array([
                    [vector_x, point_x],
                    [vector_y, point_y]
                ])
            )

            # If the matrix is rank 1, then we can draw the column space line
            if rank == 1:
                # If the vector does not have a 0 x or y component, then we can just draw the line
                if abs(vector_x) > 1e-12 and abs(vector_y) > 1e-12:
                    self._draw_oblique_line(painter, vector_y / vector_x, 0)

                # Otherwise, we have to draw lines along the axes
                elif abs(vector_x) > 1e-12 and abs(vector_y) < 1e-12:
                    painter.drawLine(0, self.height() // 2, self.width(), self.height() // 2)

                elif abs(vector_x) < 1e-12 and abs(vector_y) > 1e-12:
                    painter.drawLine(self.width() // 2, 0, self.width() // 2, self.height())

                # If the vector is (0, 0), then don't draw a line for it
                else:
                    return

            # If the rank is 0, then we don't draw any lines
            else:
                return

        elif abs(vector_x) < 1e-12 and abs(vector_y) < 1e-12:
            # If both components of the vector are practically 0, then we can't render any grid lines
            return

        # Draw vertical lines
        elif abs(vector_x) < 1e-12:
            painter.drawLine(self._canvas_x(0), 0, self._canvas_x(0), self.height())

            for i in range(min(abs(int(max_x / point_x)), self._MAX_PARALLEL_LINES)):
                painter.drawLine(
                    self._canvas_x((i + 1) * point_x),
                    0,
                    self._canvas_x((i + 1) * point_x),
                    self.height()
                )
                painter.drawLine(
                    self._canvas_x(-1 * (i + 1) * point_x),
                    0,
                    self._canvas_x(-1 * (i + 1) * point_x),
                    self.height()
                )

        # Draw horizontal lines
        elif abs(vector_y) < 1e-12:
            painter.drawLine(0, self._canvas_y(0), self.width(), self._canvas_y(0))

            for i in range(min(abs(int(max_y / point_y)), self._MAX_PARALLEL_LINES)):
                painter.drawLine(
                    0,
                    self._canvas_y((i + 1) * point_y),
                    self.width(),
                    self._canvas_y((i + 1) * point_y)
                )
                painter.drawLine(
                    0,
                    self._canvas_y(-1 * (i + 1) * point_y),
                    self.width(),
                    self._canvas_y(-1 * (i + 1) * point_y)
                )

        # If the line is oblique, then we can use y = mx + c
        else:
            m = vector_y / vector_x
            c = point_y - m * point_x

            self._draw_oblique_line(painter, m, 0)

            # We don't want to overshoot the max number of parallel lines,
            # but we should also stop looping as soon as we can't draw any more lines
            for i in range(1, self._MAX_PARALLEL_LINES + 1):
                if not self._draw_pair_of_oblique_lines(painter, m, i * c):
                    break

    def _draw_pair_of_oblique_lines(self, painter: QPainter, m: float, c: float) -> bool:
        """Draw a pair of oblique lines, using the equation y = mx + c.

        This method just calls :meth:`_draw_oblique_line` with ``c`` and ``-c``,
        and returns True if either call returned True.

        :param QPainter painter: The painter to draw the vectors and grid lines with
        :param float m: The gradient of the lines to draw
        :param float c: The y-intercept of the lines to draw. We use the positive and negative versions
        :returns bool: Whether we were able to draw any lines on the canvas
        """
        return any([
            self._draw_oblique_line(painter, m, c),
            self._draw_oblique_line(painter, m, -c)
        ])

    def _draw_oblique_line(self, painter: QPainter, m: float, c: float) -> bool:
        """Draw an oblique line, using the equation y = mx + c.

        We only draw the part of the line that fits within the canvas, returning True if
        we were able to draw a line within the boundaries, and False if we couldn't draw a line

        :param QPainter painter: The painter to draw the vectors and grid lines with
        :param float m: The gradient of the line to draw
        :param float c: The y-intercept of the line to draw
        :returns bool: Whether we were able to draw a line on the canvas
        """
        max_x, max_y = self._grid_corner()

        # These variable names are shortened for convenience
        # myi is max_y_intersection, mmyi is minus_max_y_intersection, etc.
        myi = (max_y - c) / m
        mmyi = (-max_y - c) / m
        mxi = max_x * m + c
        mmxi = -max_x * m + c

        # The inner list here is a list of coords, or None
        # If an intersection fits within the bounds, then we keep its coord,
        # else it is None, and then gets discarded from the points list
        # By the end, points is a list of two coords, or an empty list
        points: List[Tuple[float, float]] = [
            x for x in [
                (myi, max_y) if -max_x < myi < max_x else None,
                (mmyi, -max_y) if -max_x < mmyi < max_x else None,
                (max_x, mxi) if -max_y < mxi < max_y else None,
                (-max_x, mmxi) if -max_y < mmxi < max_y else None
            ] if x is not None
        ]

        # If no intersections fit on the canvas
        if len(points) < 2:
            return False

        # If we can, then draw the line
        else:
            painter.drawLine(
                *self.canvas_coords(*points[0]),
                *self.canvas_coords(*points[1])
            )
            return True

    def _draw_transformed_grid(self, painter: QPainter) -> None:
        """Draw the transformed version of the grid, given by the basis vectors.

        .. note:: This method draws the grid, but not the basis vectors. Use :meth:`_draw_basis_vectors` to draw them.

        :param QPainter painter: The painter to draw the grid lines with
        """
        # Draw all the parallel lines
        painter.setPen(QPen(self._COLOUR_I, self._WIDTH_TRANSFORMED_GRID))
        self._draw_parallel_lines(painter, self.point_i, self.point_j)
        painter.setPen(QPen(self._COLOUR_J, self._WIDTH_TRANSFORMED_GRID))
        self._draw_parallel_lines(painter, self.point_j, self.point_i)

    def _draw_arrowhead_away_from_origin(self, painter: QPainter, point: Tuple[float, float]) -> None:
        """Draw an arrowhead at ``point``, pointing away from the origin.

        :param QPainter painter: The painter to draw the arrowhead with
        :param point: The point to draw the arrowhead at, given in grid coords
        :type point: Tuple[float, float]
        """
        # This algorithm was adapted from a C# algorithm found at
        # http://csharphelper.com/blog/2014/12/draw-lines-with-arrowheads-in-c/

        # Get the x and y coords of the point, and then normalize them
        # We have to normalize them, or else the size of the arrowhead will
        # scale with the distance of the point from the origin
        x, y = point
        vector_length = np.sqrt(x * x + y * y)

        if vector_length < 1e-12:
            return

        nx = x / vector_length
        ny = y / vector_length

        # We choose a length and find the steps in the x and y directions
        length = min(
            self._ARROWHEAD_LENGTH * self.DEFAULT_GRID_SPACING / self.grid_spacing,
            vector_length
        )
        dx = length * (-nx - ny)
        dy = length * (nx - ny)

        # Then we just plot those lines
        painter.drawLine(*self.canvas_coords(x, y), *self.canvas_coords(x + dx, y + dy))
        painter.drawLine(*self.canvas_coords(x, y), *self.canvas_coords(x - dy, y + dx))

    def _draw_position_vector(self, painter: QPainter, point: Tuple[float, float], colour: QColor) -> None:
        """Draw a vector from the origin to the given point.

        :param QPainter painter: The painter to draw the position vector with
        :param point: The tip of the position vector in grid coords
        :type point: Tuple[float, float]
        :param QColor colour: The colour to draw the position vector in
        """
        painter.setPen(QPen(colour, self._WIDTH_VECTOR_LINE))
        painter.drawLine(*self._canvas_origin, *self.canvas_coords(*point))
        self._draw_arrowhead_away_from_origin(painter, point)

    def _draw_basis_vectors(self, painter: QPainter) -> None:
        """Draw arrowheads at the tips of the basis vectors.

        :param QPainter painter: The painter to draw the basis vectors with
        """
        self._draw_position_vector(painter, self.point_i, self._COLOUR_I)
        self._draw_position_vector(painter, self.point_j, self._COLOUR_J)

    def _draw_determinant_parallelogram(self, painter: QPainter) -> None:
        """Draw the parallelogram of the determinant of the matrix.

        :param QPainter painter: The painter to draw the parallelogram with
        """
        if self._det == 0:
            return

        path = QPainterPath()
        path.moveTo(*self._canvas_origin)
        path.lineTo(*self.canvas_coords(*self.point_i))
        path.lineTo(*self.canvas_coords(self.point_i[0] + self.point_j[0], self.point_i[1] + self.point_j[1]))
        path.lineTo(*self.canvas_coords(*self.point_j))

        color = (16, 235, 253) if self._det > 0 else (253, 34, 16)
        brush = QBrush(QColor(*color, alpha=128), Qt.SolidPattern)

        painter.fillPath(path, brush)

    def _draw_determinant_text(self, painter: QPainter) -> None:
        """Write the string value of the determinant in the middle of the parallelogram.

        :param QPainter painter: The painter to draw the determinant text with
        """
        painter.setPen(QPen(self._COLOUR_TEXT, self._WIDTH_VECTOR_LINE))

        # We're building a QRect that encloses the determinant parallelogram
        # Then we can center the text in this QRect
        coords: List[Tuple[float, float]] = [
            (0, 0),
            self.point_i,
            self.point_j,
            (
                self.point_i[0] + self.point_j[0],
                self.point_i[1] + self.point_j[1]
            )
        ]

        xs = [t[0] for t in coords]
        ys = [t[1] for t in coords]

        top_left = QPoint(*self.canvas_coords(min(xs), max(ys)))
        bottom_right = QPoint(*self.canvas_coords(max(xs), min(ys)))

        rect = QRectF(top_left, bottom_right)

        painter.drawText(
            rect,
            Qt.AlignHCenter | Qt.AlignVCenter,
            f'{self._det:.2f}'
        )

    def _draw_text_at_vector_tip(
        self,
        painter: QPainter,
        point: Tuple[float, float],
        text: str,
        font: Optional[QFont] = None
    ) -> None:
        """Draw the given text at the point as if it were the tip of a vector, using the custom font if given."""
        offset = 3
        top_left: QPoint
        bottom_right: QPoint
        alignment_flags: int
        x, y = point

        if x >= 0 and y >= 0:  # Q1
            top_left = QPoint(self._canvas_x(x) + offset, 0)
            bottom_right = QPoint(self.width(), self._canvas_y(y) - offset)
            alignment_flags = Qt.AlignLeft | Qt.AlignBottom

        elif x < 0 and y >= 0:  # Q2
            top_left = QPoint(0, 0)
            bottom_right = QPoint(self._canvas_x(x) - offset, self._canvas_y(y) - offset)
            alignment_flags = Qt.AlignRight | Qt.AlignBottom

        elif x < 0 and y < 0:  # Q3
            top_left = QPoint(0, self._canvas_y(y) + offset)
            bottom_right = QPoint(self._canvas_x(x) - offset, self.height())
            alignment_flags = Qt.AlignRight | Qt.AlignTop

        else:  # Q4
            top_left = QPoint(self._canvas_x(x) + offset, self._canvas_y(y) + offset)
            bottom_right = QPoint(self.width(), self.height())
            alignment_flags = Qt.AlignLeft | Qt.AlignTop

        original_font = painter.font()

        if font is not None:
            painter.setFont(font)

        painter.setPen(QPen(self._COLOUR_TEXT, 1))
        painter.drawText(QRectF(top_left, bottom_right), alignment_flags, text)

        painter.setFont(original_font)

    def _draw_eigenvectors(self, painter: QPainter) -> None:
        """Draw the eigenvectors of the displayed matrix transformation.

        :param QPainter painter: The painter to draw the eigenvectors with
        """
        for value, vector in self._eigs:
            x = value * vector[0]
            y = value * vector[1]

            if x.imag != 0 or y.imag != 0:
                continue

            self._draw_position_vector(painter, (x, y), self._COLOUR_EIGEN)
            self._draw_text_at_vector_tip(painter, (x, y), f'{value:.2f}')

    def _draw_eigenlines(self, painter: QPainter) -> None:
        """Draw the eigenlines. These are the invariant lines, or the spans of the eigenvectors.

        :param QPainter painter: The painter to draw the eigenlines with
        """
        painter.setPen(QPen(self._COLOUR_EIGEN, self._WIDTH_TRANSFORMED_GRID))

        for value, vector in self._eigs:
            if value.imag != 0:
                continue

            x, y = vector

            if x == 0:
                x_mid = int(self.width() / 2)
                painter.drawLine(x_mid, 0, x_mid, self.height())

            elif y == 0:
                y_mid = int(self.height() / 2)
                painter.drawLine(0, y_mid, self.width(), y_mid)

            else:
                self._draw_oblique_line(painter, y / x, 0)

    def _draw_basis_vector_labels(self, painter: QPainter) -> None:
        """Label the basis vectors with `i` and `j`."""
        font = self.font()
        font.setItalic(True)
        font.setStyleHint(QFont.Serif)

        self._draw_text_at_vector_tip(painter, self.point_i, 'i', font)
        self._draw_text_at_vector_tip(painter, self.point_j, 'j', font)
