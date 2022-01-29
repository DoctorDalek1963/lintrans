"""This module provides the actual widgets that can be used to visualize transformations in the GUI."""

from __future__ import annotations

import numpy as np
from PyQt5.QtGui import QPainter, QPaintEvent, QPen

from .classes import VectorGridPlot
from lintrans.typing import MatrixType


class VisualizeTransformationWidget(VectorGridPlot):
    """This class is the widget that is used in the main window to visualize transformations.

    It handles all the rendering itself, and the only method that the user needs to
    worry about is :meth:`visualize_matrix_transformation`, which allows you to visualise
    the given matrix transformation.
    """

    def __init__(self, *args, **kwargs):
        """Create the widget, passing ``*args`` and ``**kwargs`` to the superclass constructor."""
        super().__init__(*args, **kwargs)

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
        self.draw_background(painter)
        self.draw_transformed_grid(painter)
        self.draw_vector_arrowheads(painter)
        painter.end()

    def draw_arrowhead_away_from_origin(self, painter: QPainter, point: tuple[float, float]) -> None:
        """Draw an arrowhead at ``point``, pointing away from the origin.

        :param QPainter painter: The ``QPainter`` object to use to draw the arrowheads with
        :param point: The point to draw the arrowhead at, given in grid coords
        :type point: tuple[float, float]
        """
        # This algorithm was adapted from a C# algorithm found at
        # http://csharphelper.com/blog/2014/12/draw-lines-with-arrowheads-in-c/

        # Get the x and y coords of the point, and then normalize them
        # We have to normalize them, or else the size of the arrowhead will
        # scale with the distance of the point from the origin
        x, y = point
        nx = x / np.sqrt(x * x + y * y)
        ny = y / np.sqrt(x * x + y * y)

        # We choose a length and do some magic to find the steps in the x and y directions
        length = 0.15
        dx = length * (-nx - ny)
        dy = length * (nx - ny)

        # Then we just plot those lines
        painter.drawLine(*self.trans_coords(x, y), *self.trans_coords(x + dx, y + dy))
        painter.drawLine(*self.trans_coords(x, y), *self.trans_coords(x - dy, y + dx))

    def draw_vector_arrowheads(self, painter: QPainter) -> None:
        """Draw arrowheads at the tips of the basis vectors.

        :param QPainter painter: The ``QPainter`` object to use to draw the arrowheads with
        """
        painter.setPen(QPen(self.colour_i, self.width_vector_line))
        self.draw_arrowhead_away_from_origin(painter, self.point_i)
        painter.setPen(QPen(self.colour_j, self.width_vector_line))
        self.draw_arrowhead_away_from_origin(painter, self.point_j)
