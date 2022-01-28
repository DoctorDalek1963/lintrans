"""This module provides superclasses for plotting transformations."""

from __future__ import annotations

from abc import abstractmethod

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPaintEvent, QPen
from PyQt5.QtWidgets import QWidget


class BackgroundPlot(QWidget):
    """This class provides a background for plotting, as well as setup for a Qt widget.

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
        """Return the canvas coords of the origin.

        :returns: The canvas coordinates of the grid origin. Can be fed to a ``drawLine`` call when unpacked
        :rtype: tuple[int, int]
        """
        return self.width() // 2, self.height() // 2

    def trans_x(self, x: float) -> int:
        """Transform an x coordinate from grid coords to canvas coords, ready to feed to a ``drawLine`` call."""
        return int(self.origin[0] + x * self.grid_spacing)

    def trans_y(self, y: float) -> int:
        """Transform a y coordinate from grid coords to canvas coords, ready to feed to a ``drawLine`` call."""
        return int(self.origin[1] - y * self.grid_spacing)

    def trans_coords(self, x: float, y: float) -> tuple[int, int]:
        """Transform a coordinate from grid coords to canvas coords.

        This method is intended to be used like
        ``painter.drawLine(*self.trans_coords(x1, y1), *self.trans_coords(x2, y2))``.

        :param float x: The x component of the grid coordinate
        :param float y: The y component of the grid coordinate
        :returns: The resultant canvas coordinates
        :rtype: tuple[int, int]
        """
        return self.trans_x(x), self.trans_y(y)

    def grid_corner(self) -> tuple[float, float]:
        """Return the grid coords of the top right corner."""
        return self.width() / (2 * self.grid_spacing), self.height() / (2 * self.grid_spacing)

    @abstractmethod
    def paintEvent(self, event: QPaintEvent) -> None:
        """Handle a ``QPaintEvent``.

        .. note:: This method is abstract and must be overridden by all subclasses.
        """

    def draw_background(self, painter: QPainter) -> None:
        """Draw the background grid.

        .. note:: This method is just a utility method for subclasses to use to render the background grid.

        :param QPainter painter: The ``QPainter`` object to use for drawing the background
        """
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


class VectorGridPlot(BackgroundPlot):
    """This class represents a background plot, with vectors and their grid drawn on top.

    This class should be subclassed to be used for visualization and matrix definition widgets.
    All useful behaviour should be implemented by any subclass.

    .. warning:: This class should never be directly instantiated, only subclassed.
    """

    def __init__(self, *args, **kwargs):
        """Create the widget, passing ``*args`` and ``**kwargs`` to the superclass constructor.

        .. warning:: This class should not be instantiated directly, only subclassed.
        """
        super().__init__(*args, **kwargs)

        self.point_i: tuple[float, float] = (1., 0.)
        self.point_j: tuple[float, float] = (0., 1.)

        self.colour_i = QColor(37, 244, 15)
        self.colour_j = QColor(8, 8, 216)

        self.width_vector_line = 1.8
        self.width_transformed_grid = 0.6

    @abstractmethod
    def paintEvent(self, event: QPaintEvent) -> None:
        """Handle a ``QPaintEvent``.

        .. note:: This method is abstract and must be overridden by all subclasses.
        """

    def draw_parallel_lines(self, painter: QPainter, vector: tuple[float, float], point: tuple[float, float]) -> None:
        """Draw a set of evenly spaced grid lines parallel to ``vector`` intersecting ``point``.

        :param QPainter painter: The ``QPainter`` object to use to draw the lines with
        :param vector: The vector to draw the grid lines parallel to
        :type vector: tuple[float, float]
        :param point: The point for the lines to intersect with
        :type point: tuple[float, float]
        """
        max_x, max_y = self.grid_corner()
        vector_x, vector_y = vector
        point_x, point_y = point

        print(max_x, max_y, vector_x, vector_y, point_x, point_y)

        # We want to use y = mx + c but m = y / x and if either of those are 0, then this
        # equation is harder to work with, so we deal with these edge cases first
        if abs(vector_x) < 1e-12 and abs(vector_y) < 1e-12:
            # If both components of the vector are practically 0, then we can't render any grid lines
            return

        elif abs(vector_x) < 1e-12:
            painter.drawLine(self.trans_x(0), 0, self.trans_x(0), self.height())

            for i in range(abs(int(max_x / point_x))):
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

        elif abs(vector_y) < 1e-12:
            painter.drawLine(0, self.trans_y(0), self.width(), self.trans_y(0))

            for i in range(abs(int(max_y / point_y))):
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

        else:  # If the line is not horizontal or vertical, then we can use y = mx + c
            m = vector_y / vector_x
            c = point_y - m * point_x

            # For c = 0
            painter.drawLine(
                *self.trans_coords(
                    -1 * max_x,
                    m * -1 * max_x
                ),
                *self.trans_coords(
                    max_x,
                    m * max_x
                )
            )

            # Count up how many multiples of c we can have without wasting time rendering lines off screen
            multiples_of_c: int = 0
            ii: int = 1
            while True:
                y1 = m * max_x + ii * c
                y2 = -1 * m * max_x + ii * c

                if y1 < max_y or y2 < max_y:
                    multiples_of_c += 1
                    ii += 1

                else:
                    break

            # Once we know how many lines we can draw, we just draw them all
            for i in range(1, multiples_of_c + 1):
                painter.drawLine(
                    *self.trans_coords(
                        -1 * max_x,
                        m * -1 * max_x + i * c
                    ),
                    *self.trans_coords(
                        max_x,
                        m * max_x + i * c
                    )
                )
                painter.drawLine(
                    *self.trans_coords(
                        -1 * max_x,
                        m * -1 * max_x - i * c
                    ),
                    *self.trans_coords(
                        max_x,
                        m * max_x - i * c
                    )
                )

    def draw_transformed_grid(self, painter: QPainter) -> None:
        """Draw the transformed version of the grid, given by the unit vectors.

        This method simply draws the unit vectors and their parallel grid lines.

        :param QPainter painter: The ``QPainter`` object to use for drawing the vectors and grid lines
        """
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