"""This module provides the basic classes for plotting transformations."""

from __future__ import annotations

from abc import abstractmethod

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPaintEvent, QPen
from PyQt5.QtWidgets import QWidget

from lintrans.typing import MatrixType


class TransformationPlotWidget(QWidget):
    """An abstract superclass for plot widgets.

    This class provides a background (untransformed) plane, and all the backend
    details for a Qt application, but does not provide useful functionality. To
    be useful, this class must be subclassed and behaviour must be implemented
    by the subclass.

    .. warning:: This class should never be directly instantiated, only subclassed.

    .. note::
       I would make this class have ``metaclass=abc.ABCMeta``, but I can't because it subclasses ``QWidget``,
       and a every superclass of a class must have the same metaclass, and ``QWidget`` is not an abstract class.
    """

    def __init__(self, *args, **kwargs):
        """Create the widget, passing ``*args`` and ``**kwargs`` to the superclass constructor (``QWidget``)."""
        super().__init__(*args, **kwargs)

        self.setAutoFillBackground(True)

        # Set the background to white
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)

        # Set the gird colour to grey and the axes colour to black
        self.colour_background_grid = QColor(128, 128, 128)
        self.colour_background_axes = QColor(0, 0, 0)

        self.grid_spacing: int = 50
        self.width_background_grid: float = 0.3

    @property
    def origin(self) -> tuple[int, int]:
        """Return the canvas coords of the origin."""
        return self.width() // 2, self.height() // 2

    def trans_x(self, x: float) -> int:
        """Transform an x coordinate from grid coords to canvas coords."""
        return int(self.origin[0] + x * self.grid_spacing)

    def trans_y(self, y: float) -> int:
        """Transform a y coordinate from grid coords to canvas coords."""
        return int(self.origin[1] - y * self.grid_spacing)

    def trans_coords(self, x: float, y: float) -> tuple[int, int]:
        """Transform a coordinate from grid coords to canvas coords."""
        return self.trans_x(x), self.trans_y(y)

    def grid_corner(self) -> tuple[float, float]:
        """Return the grid coords of the top right corner."""
        return self.width() / (2 * self.grid_spacing), self.height() / (2 * self.grid_spacing)

    @abstractmethod
    def paintEvent(self, event: QPaintEvent) -> None:
        """Handle a ``QPaintEvent``."""

    def draw_background(self, painter: QPainter) -> None:
        """Draw the grid and axes in the widget."""
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)

        # Draw the grid
        painter.setPen(QPen(self.colour_background_grid, self.width_background_grid))

        # We draw the background grid, centered in the middle
        # We deliberately exclude the axes - these are drawn separately
        for x in range(self.width() // 2 + self.grid_spacing, self.width(), self.grid_spacing):
            painter.drawLine(x, 0, x, self.height())
            painter.drawLine(self.width() - x, 0, self.width() - x, self.height())

        for y in range(self.height() // 2 + self.grid_spacing, self.height(), self.grid_spacing):
            painter.drawLine(0, y, self.width(), y)
            painter.drawLine(0, self.height() - y, self.width(), self.height() - y)

        # Now draw the axes
        painter.setPen(QPen(self.colour_background_axes, self.width_background_grid))
        painter.drawLine(self.width() // 2, 0, self.width() // 2, self.height())
        painter.drawLine(0, self.height() // 2, self.width(), self.height() // 2)


class ViewTransformationWidget(TransformationPlotWidget):
    """This class is used to visualise matrices as transformations."""

    def __init__(self, *args, **kwargs):
        """Create the widget, passing ``*args`` and ``**kwargs`` to the superclass constructor."""
        super().__init__(*args, **kwargs)

        self.point_i: tuple[float, float] = (1., 0.)
        self.point_j: tuple[float, float] = (0., 1.)

        self.colour_i = QColor(37, 244, 15)
        self.colour_j = QColor(8, 8, 216)

        self.width_vector_line = 1
        self.width_transformed_grid = 0.6

    def transform_by_matrix(self, matrix: MatrixType) -> None:
        """Transform the plane by the given matrix."""
        self.point_i = (matrix[0][0], matrix[1][0])
        self.point_j = (matrix[0][1], matrix[1][1])
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Handle a ``QPaintEvent`` by drawing the background."""
        painter = QPainter()
        painter.begin(self)
        self.draw_background(painter)
        self.draw_transformed_grid(painter)
        painter.end()

    def draw_parallel_lines(self, painter: QPainter, vector: tuple[float, float], point: tuple[float, float]) -> None:
        """Draw a set of grid lines parallel to ``vector`` intersecting ``point``."""
        max_x, max_y = self.grid_corner()
        vector_x, vector_y = vector
        point_x, point_y = point

        if vector_x == 0:
            painter.drawLine(self.trans_x(0), 0, self.trans_x(0), self.height())

            for i in range(int(max_x / point_x)):
                painter.drawLine(
                    self.trans_x((i + 1) * point_x),
                    0,
                    self.trans_x((i + 1) * point_x),
                    self.height()
                )
                painter.drawLine(
                    self.trans_x(-1 * (i + 1) * point_x),
                    0,
                    self.trans_x(-1 * (i + 1) * point_x),
                    self.height()
                )

        elif vector_y == 0:
            painter.drawLine(0, self.trans_y(0), self.width(), self.trans_y(0))

            for i in range(int(max_y / point_y)):
                painter.drawLine(
                    0,
                    self.trans_y((i + 1) * point_y),
                    self.width(),
                    self.trans_y((i + 1) * point_y)
                )
                painter.drawLine(
                    0,
                    self.trans_y(-1 * (i + 1) * point_y),
                    self.width(),
                    self.trans_y(-1 * (i + 1) * point_y)
                )

    def draw_transformed_grid(self, painter: QPainter) -> None:
        """Draw the transformed version of the grid, given by the unit vectors."""
        # Draw the unit vectors
        painter.setPen(QPen(self.colour_i, self.width_vector_line))
        painter.drawLine(*self.origin, *self.trans_coords(*self.point_i))
        painter.setPen(QPen(self.colour_j, self.width_vector_line))
        painter.drawLine(*self.origin, *self.trans_coords(*self.point_j))

        # Draw all the parallel lines
        painter.setPen(QPen(self.colour_i, self.width_transformed_grid))
        self.draw_parallel_lines(painter, self.point_i, self.point_j)
        painter.setPen(QPen(self.colour_j, self.width_transformed_grid))
        self.draw_parallel_lines(painter, self.point_j, self.point_i)
