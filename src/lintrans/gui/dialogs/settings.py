# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides dialogs to edit settings within the app."""

from __future__ import annotations

import abc
from typing import Dict

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (QDoubleValidator, QIntValidator, QKeyEvent,
                         QKeySequence)
from PyQt5.QtWidgets import (QCheckBox, QGroupBox, QHBoxLayout, QLabel,
                             QLayout, QLineEdit, QRadioButton, QShortcut,
                             QSizePolicy, QSpacerItem, QVBoxLayout)

from lintrans.global_settings import (GlobalSettings, GlobalSettingsData,
                                      UpdateType)
from lintrans.gui.dialogs.misc import FixedSizeDialog
from lintrans.gui.settings import DisplaySettings


class SettingsDialog(FixedSizeDialog):
    """An abstract superclass for other simple dialogs."""

    def __init__(self, *args, resettable: bool, **kwargs):
        """Create the widgets and layout of the dialog, passing ``*args`` and ``**kwargs`` to super."""
        super().__init__(*args, **kwargs)

        # === Create the widgets

        self._button_confirm = QtWidgets.QPushButton(self)
        self._button_confirm.setText('Confirm')
        self._button_confirm.clicked.connect(self._confirm_settings)
        self._button_confirm.setToolTip('Confirm these new settings<br><b>(Ctrl + Enter)</b>')
        QShortcut(QKeySequence('Ctrl+Return'), self).activated.connect(self._button_confirm.click)

        self._button_cancel = QtWidgets.QPushButton(self)
        self._button_cancel.setText('Cancel')
        self._button_cancel.clicked.connect(self.reject)
        self._button_cancel.setToolTip('Revert these settings<br><b>(Escape)</b>')

        if resettable:
            self._button_reset = QtWidgets.QPushButton(self)
            self._button_reset.setText('Reset to defaults')
            self._button_reset.clicked.connect(self._reset_settings)
            self._button_reset.setToolTip('Reset these settings to their defaults<br><b>(Ctrl + R)</b>')
            QShortcut(QKeySequence('Ctrl+R'), self).activated.connect(self._button_reset.click)

        # === Arrange the widgets

        self.setContentsMargins(10, 10, 10, 10)

        self._hlay_buttons = QHBoxLayout()
        self._hlay_buttons.setSpacing(20)

        if resettable:
            self._hlay_buttons.addWidget(self._button_reset)

        self._hlay_buttons.addItem(QSpacerItem(50, 5, hPolicy=QSizePolicy.Expanding, vPolicy=QSizePolicy.Minimum))
        self._hlay_buttons.addWidget(self._button_cancel)
        self._hlay_buttons.addWidget(self._button_confirm)

    def _setup_layout(self, options_layout: QLayout) -> None:
        """Set the layout of the settings widget.

        .. note:: This method must be called at the end of :meth:`__init__`
           in subclasses to setup the layout properly.
        """
        vlay_all = QVBoxLayout()
        vlay_all.setSpacing(20)
        vlay_all.addLayout(options_layout)
        vlay_all.addLayout(self._hlay_buttons)

        self.setLayout(vlay_all)

    @abc.abstractmethod
    def _load_settings(self) -> None:
        """Load the current settings into the widgets."""

    @abc.abstractmethod
    def _confirm_settings(self) -> None:
        """Confirm the settings chosen in the dialog."""

    def _reset_settings(self) -> None:
        """Reset the settings.

        .. note:: This method is empty but not abstract because not all subclasses will need to implement it.
        """


class DisplaySettingsDialog(SettingsDialog):
    """The dialog to allow the user to edit the display settings."""

    def __init__(self, *args, display_settings: DisplaySettings, **kwargs):
        """Create the widgets and layout of the dialog.

        :param DisplaySettings display_settings: The :class:`~lintrans.gui.settings.DisplaySettings` object to mutate
        """
        super().__init__(*args, resettable=True, **kwargs)

        self.display_settings = display_settings
        self.setWindowTitle('Change display settings')

        self._dict_checkboxes: Dict[str, QCheckBox] = {}

        # === Create the widgets

        # Basic stuff

        self._checkbox_draw_background_grid = QCheckBox(self)
        self._checkbox_draw_background_grid.setText('Draw &background grid')
        self._checkbox_draw_background_grid.setToolTip(
            'Draw the background grid (axes are always drawn)'
        )
        self._dict_checkboxes['b'] = self._checkbox_draw_background_grid

        self._checkbox_draw_transformed_grid = QCheckBox(self)
        self._checkbox_draw_transformed_grid.setText('Draw t&ransformed grid')
        self._checkbox_draw_transformed_grid.setToolTip(
            'Draw the transformed grid (vectors are handled separately)'
        )
        self._dict_checkboxes['r'] = self._checkbox_draw_transformed_grid

        self._checkbox_draw_basis_vectors = QCheckBox(self)
        self._checkbox_draw_basis_vectors.setText('Draw basis &vectors')
        self._checkbox_draw_basis_vectors.setToolTip(
            'Draw the transformed basis vectors'
        )
        self._checkbox_draw_basis_vectors.clicked.connect(self._update_gui)
        self._dict_checkboxes['v'] = self._checkbox_draw_basis_vectors

        self._checkbox_label_basis_vectors = QCheckBox(self)
        self._checkbox_label_basis_vectors.setText('Label the bas&is vectors')
        self._checkbox_label_basis_vectors.setToolTip(
            'Label the transformed i and j basis vectors'
        )
        self._dict_checkboxes['i'] = self._checkbox_label_basis_vectors

        # Animations

        self._checkbox_smoothen_determinant = QCheckBox(self)
        self._checkbox_smoothen_determinant.setText('&Smoothen determinant')
        self._checkbox_smoothen_determinant.setToolTip(
            'Smoothly animate the determinant transition during animation (if possible)'
        )
        self._dict_checkboxes['s'] = self._checkbox_smoothen_determinant

        self._checkbox_applicative_animation = QCheckBox(self)
        self._checkbox_applicative_animation.setText('&Applicative animation')
        self._checkbox_applicative_animation.setToolTip(
            'Animate the new transformation applied to the current one,\n'
            'rather than just that transformation on its own'
        )
        self._dict_checkboxes['a'] = self._checkbox_applicative_animation

        label_animation_time = QLabel(self)
        label_animation_time.setText('Total animation length (ms)')
        label_animation_time.setToolTip(
            'How long it takes for an animation to complete'
        )

        self._lineedit_animation_time = QLineEdit(self)
        self._lineedit_animation_time.setValidator(QIntValidator(1, 9999, self))
        self._lineedit_animation_time.textChanged.connect(self._update_gui)

        label_animation_pause_length = QLabel(self)
        label_animation_pause_length.setText('Animation pause length (ms)')
        label_animation_pause_length.setToolTip(
            'How many milliseconds to pause for in comma-separated animations'
        )

        self._lineedit_animation_pause_length = QLineEdit(self)
        self._lineedit_animation_pause_length.setValidator(QIntValidator(1, 999, self))

        # Matrix info

        self._checkbox_draw_determinant_parallelogram = QCheckBox(self)
        self._checkbox_draw_determinant_parallelogram.setText('Draw &determinant parallelogram')
        self._checkbox_draw_determinant_parallelogram.setToolTip(
            'Shade the parallelogram representing the determinant of the matrix'
        )
        self._checkbox_draw_determinant_parallelogram.clicked.connect(self._update_gui)
        self._dict_checkboxes['d'] = self._checkbox_draw_determinant_parallelogram

        self._checkbox_show_determinant_value = QCheckBox(self)
        self._checkbox_show_determinant_value.setText('Show de&terminant value')
        self._checkbox_show_determinant_value.setToolTip(
            'Show the value of the determinant inside the parallelogram'
        )
        self._dict_checkboxes['t'] = self._checkbox_show_determinant_value

        self._checkbox_draw_eigenvectors = QCheckBox(self)
        self._checkbox_draw_eigenvectors.setText('Draw &eigenvectors')
        self._checkbox_draw_eigenvectors.setToolTip('Draw the eigenvectors of the transformations')
        self._dict_checkboxes['e'] = self._checkbox_draw_eigenvectors

        self._checkbox_draw_eigenlines = QCheckBox(self)
        self._checkbox_draw_eigenlines.setText('Draw eigen&lines')
        self._checkbox_draw_eigenlines.setToolTip('Draw the eigenlines (invariant lines) of the transformations')
        self._dict_checkboxes['l'] = self._checkbox_draw_eigenlines

        # Polygon

        self._checkbox_draw_untransformed_polygon = QCheckBox(self)
        self._checkbox_draw_untransformed_polygon.setText('&Untransformed polygon')
        self._checkbox_draw_untransformed_polygon.setToolTip('Draw the untransformed version of the polygon')
        self._dict_checkboxes['u'] = self._checkbox_draw_untransformed_polygon

        self._checkbox_draw_transformed_polygon = QCheckBox(self)
        self._checkbox_draw_transformed_polygon.setText('Transformed &polygon')
        self._checkbox_draw_transformed_polygon.setToolTip('Draw the transformed version of the polygon')
        self._dict_checkboxes['p'] = self._checkbox_draw_transformed_polygon

        # Input/output vectors

        self._checkbox_draw_input_vector = QCheckBox(self)
        self._checkbox_draw_input_vector.setText('Draw the i&nput vector')
        self._checkbox_draw_input_vector.setToolTip('Draw the input vector (only in the viewport)')
        self._dict_checkboxes['n'] = self._checkbox_draw_input_vector

        self._checkbox_draw_output_vector = QCheckBox(self)
        self._checkbox_draw_output_vector.setText('Draw the &output vector')
        self._checkbox_draw_output_vector.setToolTip('Draw the output vector (only in the viewport)')
        self._dict_checkboxes['o'] = self._checkbox_draw_output_vector

        # === Arrange the widgets in QGroupBoxes

        # Basic stuff

        vlay_groupbox_basic_stuff = QVBoxLayout()
        vlay_groupbox_basic_stuff.setSpacing(20)
        vlay_groupbox_basic_stuff.addWidget(self._checkbox_draw_background_grid)
        vlay_groupbox_basic_stuff.addWidget(self._checkbox_draw_transformed_grid)
        vlay_groupbox_basic_stuff.addWidget(self._checkbox_draw_basis_vectors)
        vlay_groupbox_basic_stuff.addWidget(self._checkbox_label_basis_vectors)

        groupbox_basic_stuff = QGroupBox('Basic stuff', self)
        groupbox_basic_stuff.setLayout(vlay_groupbox_basic_stuff)

        # Animations

        hlay_animation_time = QHBoxLayout()
        hlay_animation_time.addWidget(label_animation_time)
        hlay_animation_time.addWidget(self._lineedit_animation_time)

        hlay_animation_pause_length = QHBoxLayout()
        hlay_animation_pause_length.addWidget(label_animation_pause_length)
        hlay_animation_pause_length.addWidget(self._lineedit_animation_pause_length)

        vlay_groupbox_animations = QVBoxLayout()
        vlay_groupbox_animations.setSpacing(20)
        vlay_groupbox_animations.addWidget(self._checkbox_smoothen_determinant)
        vlay_groupbox_animations.addWidget(self._checkbox_applicative_animation)
        vlay_groupbox_animations.addLayout(hlay_animation_time)
        vlay_groupbox_animations.addLayout(hlay_animation_pause_length)

        groupbox_animations = QGroupBox('Animations', self)
        groupbox_animations.setLayout(vlay_groupbox_animations)

        # Matrix info

        vlay_groupbox_matrix_info = QVBoxLayout()
        vlay_groupbox_matrix_info.setSpacing(20)
        vlay_groupbox_matrix_info.addWidget(self._checkbox_draw_determinant_parallelogram)
        vlay_groupbox_matrix_info.addWidget(self._checkbox_show_determinant_value)
        vlay_groupbox_matrix_info.addWidget(self._checkbox_draw_eigenvectors)
        vlay_groupbox_matrix_info.addWidget(self._checkbox_draw_eigenlines)

        groupbox_matrix_info = QGroupBox('Matrix info', self)
        groupbox_matrix_info.setLayout(vlay_groupbox_matrix_info)

        # Polygon

        vlay_groupbox_polygon = QVBoxLayout()
        vlay_groupbox_polygon.setSpacing(20)
        vlay_groupbox_polygon.addWidget(self._checkbox_draw_untransformed_polygon)
        vlay_groupbox_polygon.addWidget(self._checkbox_draw_transformed_polygon)

        groupbox_polygon = QGroupBox('Polygon', self)
        groupbox_polygon.setLayout(vlay_groupbox_polygon)

        # Input/output vectors

        vlay_groupbox_io_vectors = QVBoxLayout()
        vlay_groupbox_io_vectors.setSpacing(20)
        vlay_groupbox_io_vectors.addWidget(self._checkbox_draw_input_vector)
        vlay_groupbox_io_vectors.addWidget(self._checkbox_draw_output_vector)

        groupbox_io_vectors = QGroupBox('Input/output vectors', self)
        groupbox_io_vectors.setLayout(vlay_groupbox_io_vectors)

        # Now arrange the groupboxes
        vlay_left = QVBoxLayout()
        vlay_left.setSpacing(20)
        vlay_left.addWidget(groupbox_basic_stuff)
        vlay_left.addWidget(groupbox_animations)

        vlay_right = QVBoxLayout()
        vlay_right.setSpacing(20)
        vlay_right.addWidget(groupbox_matrix_info)
        vlay_right.addWidget(groupbox_polygon)
        vlay_right.addWidget(groupbox_io_vectors)

        options_layout = QHBoxLayout()
        options_layout.setSpacing(20)
        options_layout.addLayout(vlay_left)
        options_layout.addLayout(vlay_right)

        self._setup_layout(options_layout)

        # Finally, we load the current settings and update the GUI
        self._load_settings()
        self._update_gui()

    def _load_settings(self) -> None:
        """Load the current display settings into the widgets."""
        # Basic stuff
        self._checkbox_draw_background_grid.setChecked(self.display_settings.draw_background_grid)
        self._checkbox_draw_transformed_grid.setChecked(self.display_settings.draw_transformed_grid)
        self._checkbox_draw_basis_vectors.setChecked(self.display_settings.draw_basis_vectors)
        self._checkbox_label_basis_vectors.setChecked(self.display_settings.label_basis_vectors)

        # Animations
        self._checkbox_smoothen_determinant.setChecked(self.display_settings.smoothen_determinant)
        self._checkbox_applicative_animation.setChecked(self.display_settings.applicative_animation)
        self._lineedit_animation_time.setText(str(self.display_settings.animation_time))
        self._lineedit_animation_pause_length.setText(str(self.display_settings.animation_pause_length))

        # Matrix info
        self._checkbox_draw_determinant_parallelogram.setChecked(self.display_settings.draw_determinant_parallelogram)
        self._checkbox_show_determinant_value.setChecked(self.display_settings.show_determinant_value)
        self._checkbox_draw_eigenvectors.setChecked(self.display_settings.draw_eigenvectors)
        self._checkbox_draw_eigenlines.setChecked(self.display_settings.draw_eigenlines)

        # Polygon
        self._checkbox_draw_untransformed_polygon.setChecked(self.display_settings.draw_untransformed_polygon)
        self._checkbox_draw_transformed_polygon.setChecked(self.display_settings.draw_transformed_polygon)

        # Input/output vectors
        self._checkbox_draw_input_vector.setChecked(self.display_settings.draw_input_vector)
        self._checkbox_draw_output_vector.setChecked(self.display_settings.draw_output_vector)

    def _confirm_settings(self) -> None:
        """Build a :class:`~lintrans.gui.settings.DisplaySettings` object and assign it."""
        # Basic stuff
        self.display_settings.draw_background_grid = self._checkbox_draw_background_grid.isChecked()
        self.display_settings.draw_transformed_grid = self._checkbox_draw_transformed_grid.isChecked()
        self.display_settings.draw_basis_vectors = self._checkbox_draw_basis_vectors.isChecked()
        self.display_settings.label_basis_vectors = self._checkbox_label_basis_vectors.isChecked()

        # Animations
        self.display_settings.smoothen_determinant = self._checkbox_smoothen_determinant.isChecked()
        self.display_settings.applicative_animation = self._checkbox_applicative_animation.isChecked()
        self.display_settings.animation_time = int(self._lineedit_animation_time.text())
        self.display_settings.animation_pause_length = int(self._lineedit_animation_pause_length.text())

        # Matrix info
        self.display_settings.draw_determinant_parallelogram = self._checkbox_draw_determinant_parallelogram.isChecked()
        self.display_settings.show_determinant_value = self._checkbox_show_determinant_value.isChecked()
        self.display_settings.draw_eigenvectors = self._checkbox_draw_eigenvectors.isChecked()
        self.display_settings.draw_eigenlines = self._checkbox_draw_eigenlines.isChecked()

        # Polygon
        self.display_settings.draw_untransformed_polygon = self._checkbox_draw_untransformed_polygon.isChecked()
        self.display_settings.draw_transformed_polygon = self._checkbox_draw_transformed_polygon.isChecked()

        # Input/output vectors
        self.display_settings.draw_input_vector = self._checkbox_draw_input_vector.isChecked()
        self.display_settings.draw_output_vector = self._checkbox_draw_output_vector.isChecked()

        self.accept()

    def _reset_settings(self) -> None:
        """Reset the display settings to their defaults."""
        self.display_settings = DisplaySettings()
        self._load_settings()
        self._update_gui()

    def _update_gui(self) -> None:
        """Update the GUI according to other widgets in the GUI.

        For example, this method updates which checkboxes are enabled based on the values of other checkboxes.
        """
        self._checkbox_show_determinant_value.setEnabled(self._checkbox_draw_determinant_parallelogram.isChecked())
        self._checkbox_label_basis_vectors.setEnabled(self._checkbox_draw_basis_vectors.isChecked())

        try:
            self._button_confirm.setEnabled(int(self._lineedit_animation_time.text()) >= 10)
        except ValueError:
            self._button_confirm.setEnabled(False)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle a :class:`QKeyEvent` by manually activating toggling checkboxes.

        Qt handles these shortcuts automatically and allows the user to do ``Alt + Key``
        to activate a simple shortcut defined with ``&``. However, I like to be able to
        just hit ``Key`` and have the shortcut activate.
        """
        letter = event.text().lower()
        key = event.key()

        if letter in self._dict_checkboxes:
            self._dict_checkboxes[letter].animateClick()

        # Return or keypad enter
        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            self._button_confirm.click()

        # Escape
        elif key == Qt.Key_Escape:
            self._button_cancel.click()

        else:
            event.ignore()
            return

        event.accept()


class GlobalSettingsDialog(SettingsDialog):
    """The dialog to allow the user to edit the display settings."""

    def __init__(self, *args, **kwargs):
        """Create the widgets and layout of the dialog."""
        super().__init__(*args, resettable=True, **kwargs)

        self._data: GlobalSettingsData = GlobalSettings().get_data()
        self.setWindowTitle('Change global settings')

        # === Create the widgets

        groupbox_update_types = QGroupBox('Update prompt type', self)
        self._radio_button_auto = QRadioButton('Always update automatically', groupbox_update_types)
        self._radio_button_prompt = QRadioButton('Always ask to update', groupbox_update_types)
        self._radio_button_never = QRadioButton('Never update', groupbox_update_types)

        label_cursor_epsilon = QLabel(self)
        label_cursor_epsilon.setText('Cursor drag proximity (pixels)')
        label_cursor_epsilon.setToolTip(
            'The maximum distance (in pixels) from a draggable point before it will be dragged'
        )

        self._lineedit_cursor_epsilon = QLineEdit(self)
        self._lineedit_cursor_epsilon.setValidator(QIntValidator(1, 99, self))
        self._lineedit_cursor_epsilon.setText(str(self._data.cursor_epsilon))
        self._lineedit_cursor_epsilon.textChanged.connect(self._update_gui)

        self._checkbox_snap_to_int_coords = QCheckBox(self)
        self._checkbox_snap_to_int_coords.setText('Snap to integer coordinates')
        self._checkbox_snap_to_int_coords.setToolTip(
            'Whether vectors should snap the integer coordinates when dragging them'
        )
        self._checkbox_snap_to_int_coords.clicked.connect(self._update_gui)

        label_snap_dist = QLabel(self)
        label_snap_dist.setText('Snap distance (grid units)')
        label_snap_dist.setToolTip(
            'The minimum distacne (in grid units) that a draggable point '
            'must be from an integer coordinate to snap to it'
        )

        self._lineedit_snap_dist = QLineEdit(self)
        self._lineedit_snap_dist.setValidator(QDoubleValidator(0.0, 0.99, 2, self))
        self._lineedit_snap_dist.setText(str(self._data.snap_dist))
        self._lineedit_snap_dist.textChanged.connect(self._update_gui)

        # === Arrange the widgets

        vlay_update_type = QVBoxLayout()
        vlay_update_type.addWidget(self._radio_button_auto)
        vlay_update_type.addWidget(self._radio_button_prompt)
        vlay_update_type.addWidget(self._radio_button_never)
        groupbox_update_types.setLayout(vlay_update_type)

        hlay_cursor_epsilon = QHBoxLayout()
        hlay_cursor_epsilon.addWidget(label_cursor_epsilon)
        hlay_cursor_epsilon.addWidget(self._lineedit_cursor_epsilon)

        hlay_snap_dist = QHBoxLayout()
        hlay_snap_dist.addWidget(label_snap_dist)
        hlay_snap_dist.addWidget(self._lineedit_snap_dist)

        vlay_dist = QVBoxLayout()
        vlay_dist.setSpacing(20)
        vlay_dist.addLayout(hlay_cursor_epsilon)
        vlay_dist.addWidget(self._checkbox_snap_to_int_coords)
        vlay_dist.addLayout(hlay_snap_dist)

        groupbox_dist = QGroupBox('Distances', self)
        groupbox_dist.setLayout(vlay_dist)

        options_layout = QVBoxLayout()
        options_layout.setSpacing(20)
        options_layout.addWidget(groupbox_update_types)
        options_layout.addWidget(groupbox_dist)

        self._load_settings()
        self._update_gui()
        self._setup_layout(options_layout)

    def _update_gui(self) -> None:
        """Update the GUI according to other widgets in the GUI."""
        if self._lineedit_cursor_epsilon.text() == '':
            cursor_epsilon = False
        else:
            cursor_epsilon = 0 <= int(self._lineedit_cursor_epsilon.text()) <= 99

        if self._lineedit_snap_dist.text() == '':
            snap_dist = False
        else:
            snap_dist = 0.0 <= float(self._lineedit_snap_dist.text()) <= 1.0

        self._lineedit_snap_dist.setEnabled(self._checkbox_snap_to_int_coords.isChecked())
        self._button_confirm.setEnabled(cursor_epsilon and snap_dist)

    def _load_settings(self) -> None:
        """Load the current display settings into the widgets."""
        if self._data.update_type == UpdateType.auto:
            self._radio_button_auto.setChecked(True)
        elif self._data.update_type == UpdateType.prompt:
            self._radio_button_prompt.setChecked(True)
        elif self._data.update_type == UpdateType.never:
            self._radio_button_never.setChecked(True)

        self._lineedit_cursor_epsilon.setText(str(self._data.cursor_epsilon))
        self._checkbox_snap_to_int_coords.setChecked(self._data.snap_to_int_coords)
        self._lineedit_snap_dist.setText(str(self._data.snap_dist))

    def _confirm_settings(self) -> None:
        """Set the global settings."""
        if self._radio_button_auto.isChecked():
            self._data.update_type = UpdateType.auto
        elif self._radio_button_prompt.isChecked():
            self._data.update_type = UpdateType.prompt
        elif self._radio_button_never.isChecked():
            self._data.update_type = UpdateType.never

        self._data.cursor_epsilon = int(self._lineedit_cursor_epsilon.text())
        self._data.snap_to_int_coords = self._checkbox_snap_to_int_coords.isChecked()
        self._data.snap_dist = float(self._lineedit_snap_dist.text())

        GlobalSettings().set_data(self._data)

        self.accept()

    def _reset_settings(self) -> None:
        """Reset the internal data values to their defaults."""
        self._data = GlobalSettingsData()
        self._load_settings()
        self._update_gui()
