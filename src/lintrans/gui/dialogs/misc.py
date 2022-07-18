#  lintrans - The linear transformation visualizer
#  Copyright (C) 2022 D. Dyson (DoctorDalek1963)
#
#  This program is licensed under GNU GPLv3, available here:
#  <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides miscellaneous dialog classes like :class:`AboutDialog`."""

from __future__ import annotations

import platform

from PyQt5 import QtWidgets
from PyQt5.QtCore import PYQT_VERSION_STR, QT_VERSION_STR, Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout

import lintrans


class FixedSizeDialog(QDialog):
    """A simple superclass to create modal dialog boxes with fixed size.

    We override the :meth:`open` method to set the fixed size as soon as the dialog is opened modally.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Set the :cpp:enum:`Qt::WA_DeleteOnClose` attribute to ensure deletion of dialog."""
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_DeleteOnClose)

    def open(self) -> None:
        """Override :meth:`QDialog.open` to set the dialog to a fixed size."""
        super().open()
        self.setFixedSize(self.size())


class AboutDialog(FixedSizeDialog):
    """A simple dialog class to display information about the app to the user.

    It only has an :meth:`__init__` method because it only has label widgets, so no other methods are necessary here.
    """

    def __init__(self, *args, **kwargs):
        """Create an :class:`AboutDialog` object with all the label widgets."""
        super().__init__(*args, **kwargs)

        self.setWindowTitle('About lintrans')

        # === Create the widgets

        label_title = QtWidgets.QLabel(self)
        label_title.setText(f'lintrans (version {lintrans.__version__})')
        label_title.setAlignment(Qt.AlignCenter)

        font_title = label_title.font()
        font_title.setPointSize(font_title.pointSize() * 2)
        label_title.setFont(font_title)

        label_version_info = QtWidgets.QLabel(self)
        label_version_info.setText(
            f'With Python version {platform.python_version()}\n'
            f'Qt version {QT_VERSION_STR} and PyQt5 version {PYQT_VERSION_STR}\n'
            f'Running on {platform.platform()}'
        )
        label_version_info.setAlignment(Qt.AlignCenter)

        label_info = QtWidgets.QLabel(self)
        label_info.setText(
            'lintrans is a program designed to help visualise<br>'
            '2D linear transformations represented with matrices.<br><br>'
            "It's designed for teachers and students and any feedback<br>"
            'is greatly appreciated at <a href="https://github.com/DoctorDalek1963/lintrans" '
            'style="color: black;">my GitHub page</a><br>or via email '
            '(<a href="mailto:dyson.dyson@icloud.com" style="color: black;">dyson.dyson@icloud.com</a>).'
        )
        label_info.setAlignment(Qt.AlignCenter)
        label_info.setTextFormat(Qt.RichText)
        label_info.setOpenExternalLinks(True)

        label_copyright = QtWidgets.QLabel(self)
        label_copyright.setText(
            'This program is free software.<br>Copyright 2021-2022 D. Dyson (DoctorDalek1963).<br>'
            'This program is licensed under GPLv3, which can be found '
            '<a href="https://www.gnu.org/licenses/gpl-3.0.html" style="color: black;">here</a>.'
        )
        label_copyright.setAlignment(Qt.AlignCenter)
        label_copyright.setTextFormat(Qt.RichText)
        label_copyright.setOpenExternalLinks(True)

        # === Arrange the widgets

        self.setContentsMargins(10, 10, 10, 10)

        vlay = QVBoxLayout()
        vlay.setSpacing(20)
        vlay.addWidget(label_title)
        vlay.addWidget(label_version_info)
        vlay.addWidget(label_info)
        vlay.addWidget(label_copyright)

        self.setLayout(vlay)
