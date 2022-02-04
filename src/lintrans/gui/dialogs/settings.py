"""This module provides dialogs to edit settings within the app."""

from __future__ import annotations

import abc
import copy

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QKeySequence
from PyQt5.QtWidgets import QCheckBox, QDialog, QHBoxLayout, QShortcut, QSizePolicy, QSpacerItem, QVBoxLayout

from lintrans.gui.settings import DisplaySettings


class SettingsDialog(QDialog):
    """An abstract superclass for other simple dialogs."""

    def __init__(self, *args, **kwargs):
        """Create the widgets and layout of the dialog, passing ``*args`` and ``**kwargs`` to super."""
        super().__init__(*args, **kwargs)

        # === Create the widgets

        self.button_confirm = QtWidgets.QPushButton(self)
        self.button_confirm.setText('Confirm')
        self.button_confirm.clicked.connect(self.confirm_settings)
        self.button_confirm.setToolTip('Confirm these new settings<br><b>(Ctrl + Enter)</b>')
        QShortcut(QKeySequence('Ctrl+Return'), self).activated.connect(self.button_confirm.click)

        self.button_cancel = QtWidgets.QPushButton(self)
        self.button_cancel.setText('Cancel')
        self.button_cancel.clicked.connect(self.reject)
        self.button_cancel.setToolTip('Cancel this definition<br><b>(Escape)</b>')

        # === Arrange the widgets

        self.setContentsMargins(10, 10, 10, 10)

        self.hlay_buttons = QHBoxLayout()
        self.hlay_buttons.setSpacing(20)
        self.hlay_buttons.addItem(QSpacerItem(50, 5, hPolicy=QSizePolicy.Expanding, vPolicy=QSizePolicy.Minimum))
        self.hlay_buttons.addWidget(self.button_cancel)
        self.hlay_buttons.addWidget(self.button_confirm)

        self.vlay_options = QVBoxLayout()
        self.vlay_options.setSpacing(20)

        self.vlay_all = QVBoxLayout()
        self.vlay_all.setSpacing(20)
        self.vlay_all.addLayout(self.vlay_options)
        self.vlay_all.addLayout(self.hlay_buttons)

        self.setLayout(self.vlay_all)

    @abc.abstractmethod
    def load_settings(self) -> None:
        """Load the current settings into the widgets."""

    @abc.abstractmethod
    def confirm_settings(self) -> None:
        """Confirm the settings chosen in the dialog."""


class DisplaySettingsDialog(SettingsDialog):
    """The dialog to allow the user to edit the display settings."""

    def __init__(self, display_settings: DisplaySettings, *args, **kwargs):
        """Create the widgets and layout of the dialog.

        :param DisplaySettings display_settings: The :class:`lintrans.gui.settings.DisplaySettings` object to mutate
        """
        super().__init__(*args, **kwargs)

        self.display_settings = display_settings
        self.setWindowTitle('Change display settings')

        # === Create the widgets

        font_label = self.font()
        font_label.setUnderline(True)
        font_label.setPointSize(int(font_label.pointSize() * 1.2))

        self.label_animations = QtWidgets.QLabel(self)
        self.label_animations.setText('Animations')
        self.label_animations.setAlignment(Qt.AlignCenter)
        self.label_animations.setFont(font_label)

        self.checkbox_animate_determinant = QCheckBox(self)
        self.checkbox_animate_determinant.setText('Animate determinant')
        self.checkbox_animate_determinant.setToolTip('Smoothly animate the determinant during animation')

        self.checkbox_applicative_animation = QCheckBox(self)
        self.checkbox_applicative_animation.setText('Applicative animation')
        self.checkbox_applicative_animation.setToolTip(
            'Animate the new transformation applied to the current one,\n'
            'rather than just that transformation on its own'
        )

        self.label_animation_pause_length = QtWidgets.QLabel(self)
        self.label_animation_pause_length.setText('Animation pause length (ms)')
        self.label_animation_pause_length.setToolTip(
            'How many milliseconds to pause for in comma-separated animations'
        )

        self.lineedit_animation_pause_length = QtWidgets.QLineEdit(self)
        self.lineedit_animation_pause_length.setValidator(QIntValidator(1, 999, self))

        # === Arrange the widgets

        self.hlay_animation_pause_length = QHBoxLayout()
        self.hlay_animation_pause_length.addWidget(self.label_animation_pause_length)
        self.hlay_animation_pause_length.addWidget(self.lineedit_animation_pause_length)

        self.vlay_options.addWidget(self.label_animations)
        self.vlay_options.addWidget(self.checkbox_animate_determinant)
        self.vlay_options.addWidget(self.checkbox_applicative_animation)
        self.vlay_options.addLayout(self.hlay_animation_pause_length)

        # Finally, we load the current settings
        self.load_settings()

    def load_settings(self) -> None:
        """Load the current display settings into the widgets."""
        self.checkbox_animate_determinant.setChecked(self.display_settings.animate_determinant)
        self.checkbox_applicative_animation.setChecked(self.display_settings.applicative_animation)
        self.lineedit_animation_pause_length.setText(str(self.display_settings.animation_pause_length))

    def confirm_settings(self) -> None:
        """Build a :class:`lintrans.gui.settings.DisplaySettings` object and assign it."""
        self.display_settings.animate_determinant = self.checkbox_animate_determinant.isChecked()
        self.display_settings.applicative_animation = self.checkbox_applicative_animation.isChecked()
        self.display_settings.animation_pause_length = int(self.lineedit_animation_pause_length.text())

        self.accept()
