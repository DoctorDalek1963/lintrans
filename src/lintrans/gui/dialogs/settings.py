"""This module provides dialogs to edit settings within the app."""

from __future__ import annotations

import abc

from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator, QKeyEvent, QKeySequence
from PyQt5.QtWidgets import QCheckBox, QDialog, QGroupBox, QHBoxLayout, QShortcut, QSizePolicy, QSpacerItem, QVBoxLayout

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
        self.button_cancel.setToolTip('Revert these settings<br><b>(Escape)</b>')

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

        self.dict_checkboxes: dict[str, QCheckBox] = dict()

        # === Create the widgets

        # Animations

        self.checkbox_smoothen_determinant = QCheckBox(self)
        self.checkbox_smoothen_determinant.setText('&Smoothen determinant')
        self.checkbox_smoothen_determinant.setToolTip(
            'Smoothly animate the determinant transition during animation (if possible)'
        )
        self.dict_checkboxes['s'] = self.checkbox_smoothen_determinant

        self.checkbox_applicative_animation = QCheckBox(self)
        self.checkbox_applicative_animation.setText('&Applicative animation')
        self.checkbox_applicative_animation.setToolTip(
            'Animate the new transformation applied to the current one,\n'
            'rather than just that transformation on its own'
        )
        self.dict_checkboxes['a'] = self.checkbox_applicative_animation

        self.label_animation_pause_length = QtWidgets.QLabel(self)
        self.label_animation_pause_length.setText('Animation pause length (ms)')
        self.label_animation_pause_length.setToolTip(
            'How many milliseconds to pause for in comma-separated animations'
        )

        self.lineedit_animation_pause_length = QtWidgets.QLineEdit(self)
        self.lineedit_animation_pause_length.setValidator(QIntValidator(1, 999, self))

        # Matrix info

        self.checkbox_draw_determinant_parallelogram = QCheckBox(self)
        self.checkbox_draw_determinant_parallelogram.setText('Draw &determinant parallelogram')
        self.checkbox_draw_determinant_parallelogram.setToolTip(
            'Shade the parallelogram representing the determinant of the matrix'
        )
        self.checkbox_draw_determinant_parallelogram.clicked.connect(self.update_gui)
        self.dict_checkboxes['d'] = self.checkbox_draw_determinant_parallelogram

        self.checkbox_draw_determinant_text = QCheckBox(self)
        self.checkbox_draw_determinant_text.setText('Draw determinant &text')
        self.checkbox_draw_determinant_text.setToolTip(
            'Write the text value of the determinant inside the parallelogram'
        )
        self.dict_checkboxes['t'] = self.checkbox_draw_determinant_text

        self.checkbox_draw_eigenvectors = QCheckBox(self)
        self.checkbox_draw_eigenvectors.setText('Draw &eigenvectors')
        self.checkbox_draw_eigenvectors.setToolTip('Draw the eigenvectors of the transformations')
        self.dict_checkboxes['e'] = self.checkbox_draw_eigenvectors

        # === Arrange the widgets in QGroupBoxes

        # Animations

        self.hlay_animation_pause_length = QHBoxLayout()
        self.hlay_animation_pause_length.addWidget(self.label_animation_pause_length)
        self.hlay_animation_pause_length.addWidget(self.lineedit_animation_pause_length)

        self.vlay_groupbox_animations = QVBoxLayout()
        self.vlay_groupbox_animations.setSpacing(20)
        self.vlay_groupbox_animations.addWidget(self.checkbox_smoothen_determinant)
        self.vlay_groupbox_animations.addWidget(self.checkbox_applicative_animation)
        self.vlay_groupbox_animations.addLayout(self.hlay_animation_pause_length)

        self.groupbox_animations = QGroupBox('Animations', self)
        self.groupbox_animations.setLayout(self.vlay_groupbox_animations)

        # Matrix info

        self.vlay_groupbox_matrix_info = QVBoxLayout()
        self.vlay_groupbox_matrix_info.setSpacing(20)
        self.vlay_groupbox_matrix_info.addWidget(self.checkbox_draw_determinant_parallelogram)
        self.vlay_groupbox_matrix_info.addWidget(self.checkbox_draw_determinant_text)
        self.vlay_groupbox_matrix_info.addWidget(self.checkbox_draw_eigenvectors)

        self.groupbox_matrix_info = QGroupBox('Matrix info', self)
        self.groupbox_matrix_info.setLayout(self.vlay_groupbox_matrix_info)

        self.vlay_options.addWidget(self.groupbox_animations)
        self.vlay_options.addWidget(self.groupbox_matrix_info)

        # Finally, we load the current settings and update the GUI
        self.load_settings()
        self.update_gui()

    def load_settings(self) -> None:
        """Load the current display settings into the widgets."""
        # Animations
        self.checkbox_smoothen_determinant.setChecked(self.display_settings.smoothen_determinant)
        self.checkbox_applicative_animation.setChecked(self.display_settings.applicative_animation)
        self.lineedit_animation_pause_length.setText(str(self.display_settings.animation_pause_length))

        # Matrix info
        self.checkbox_draw_determinant_parallelogram.setChecked(self.display_settings.draw_determinant_parallelogram)
        self.checkbox_draw_determinant_text.setChecked(self.display_settings.draw_determinant_text)
        self.checkbox_draw_eigenvectors.setChecked(self.display_settings.draw_eigenvectors)

    def confirm_settings(self) -> None:
        """Build a :class:`lintrans.gui.settings.DisplaySettings` object and assign it."""
        # Animations
        self.display_settings.smoothen_determinant = self.checkbox_smoothen_determinant.isChecked()
        self.display_settings.applicative_animation = self.checkbox_applicative_animation.isChecked()
        self.display_settings.animation_pause_length = int(self.lineedit_animation_pause_length.text())

        # Matrix info
        self.display_settings.draw_determinant_parallelogram = self.checkbox_draw_determinant_parallelogram.isChecked()
        self.display_settings.draw_determinant_text = self.checkbox_draw_determinant_text.isChecked()
        self.display_settings.draw_eigenvectors = self.checkbox_draw_eigenvectors.isChecked()

        self.accept()

    def update_gui(self) -> None:
        """Update the GUI according to other widgets in the GUI.

        For example, this method updates which checkboxes are enabled based on the values of other checkboxes.
        """
        self.checkbox_draw_determinant_text.setEnabled(self.checkbox_draw_determinant_parallelogram.isChecked())

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle a ``QKeyEvent`` by manually activating toggling checkboxes.

        Qt handles these shortcuts automatically and allows the user to do ``Alt + Key``
        to activate a simple shortcut defined with ``&``. However, I like to be able to
        just hit ``Key`` and have the shortcut activate.
        """
        letter = event.text().lower()
        key = event.key()

        if letter in self.dict_checkboxes:
            self.dict_checkboxes[letter].animateClick()

        # Return or keypad enter
        elif key == 0x01000004 or key == 0x01000005:
            self.button_confirm.click()

        # Escape
        elif key == 0x01000000:
            self.button_cancel.click()

        else:
            event.ignore()
