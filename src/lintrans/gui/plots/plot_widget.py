"""This module provides the basic classes for plotting transformations."""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter, QPaintEvent, QPen
from PyQt5.QtWidgets import QWidget


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
        self.grid_colour = QColor(128, 128, 128)
        self.axes_colour = QColor(0, 0, 0)

        self.grid_spacing: int = 50
        self.line_width: float = 0.4

    @property
    def w(self) -> int:
        """Return the width of the widget."""
        return int(self.size().width())

    @property
    def h(self) -> int:
        """Return the height of the widget."""
        return int(self.size().height())

    def paintEvent(self, e: QPaintEvent):
        """Handle a ``QPaintEvent`` by drawing the widget."""
        qp = QPainter()
        qp.begin(self)
        self.draw_widget(qp)
        qp.end()

    def draw_widget(self, qp: QPainter):
        """Draw the grid and axes in the widget."""
        qp.setRenderHint(QPainter.Antialiasing)
        qp.setBrush(Qt.NoBrush)

        # Draw the grid
        qp.setPen(QPen(self.grid_colour, self.line_width))

        # We draw the background grid, centered in the middle
        # We deliberately exclude the axes - these are drawn separately
        for x in range(self.w // 2 + self.grid_spacing, self.w, self.grid_spacing):
            qp.drawLine(x, 0, x, self.h)
            qp.drawLine(self.w - x, 0, self.w - x, self.h)

        for y in range(self.h // 2 + self.grid_spacing, self.h, self.grid_spacing):
            qp.drawLine(0, y, self.w, y)
            qp.drawLine(0, self.h - y, self.w, self.h - y)

        # Now draw the axes
        qp.setPen(QPen(self.axes_colour, self.line_width))
        qp.drawLine(self.w // 2, 0, self.w // 2, self.h)
        qp.drawLine(0, self.h // 2, self.w, self.h // 2)


class ViewTransformationWidget(TransformationPlotWidget):
    """This class is used to visualise matrices as transformations."""

    def __init__(self, *args, **kwargs):
        """Create the widget, passing ``*args`` and ``**kwargs`` to the superclass constructor."""
        super().__init__(*args, **kwargs)
