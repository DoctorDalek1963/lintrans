# lintrans - The linear transformation visualizer
# Copyright (C) 2022 D. Dyson (DoctorDalek1963)
#
# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""Test that the display settings dialog works and the settings get changed.

We can't really test that the settings work in a unit test, because that requires visual inspection.
"""

from PyQt5.QtCore import Qt
from pytestqt.qtbot import QtBot

from lintrans.gui.dialogs import DisplaySettingsDialog
from lintrans.gui.main_window import LintransMainWindow

from conftest import get_open_widget, is_widget_class_open


def test_open_dialog(qtbot: QtBot, window: LintransMainWindow) -> None:
    """Make sure the dialog opens properly."""
    qtbot.mouseClick(window._button_change_display_settings, Qt.LeftButton)
    assert is_widget_class_open(DisplaySettingsDialog)
    qtbot.addWidget(get_open_widget(DisplaySettingsDialog))


def test_settings_change(qtbot: QtBot, window: LintransMainWindow) -> None:
    """Test that the display settings actually change when changed in the dialog."""
    qtbot.mouseClick(window._button_change_display_settings, Qt.LeftButton)
    dialog = get_open_widget(DisplaySettingsDialog)
    qtbot.addWidget(dialog)
    settings = window._plot.display_settings

    # These are the only checkboxes that seem to work, and I have absolutely no idea why
    smoothen_determinant = settings.smoothen_determinant
    draw_parallelogram = settings.draw_determinant_parallelogram

    qtbot.mouseClick(dialog._checkbox_smoothen_determinant, Qt.LeftButton)
    qtbot.mouseClick(dialog._checkbox_draw_determinant_parallelogram, Qt.LeftButton)

    qtbot.mouseClick(dialog._button_confirm, Qt.LeftButton)
    qtbot.wait(50)  # This is a bodge but `qtbot.waitActive(window)` doesn't work

    new_settings = window._plot.display_settings
    print(is_widget_class_open(DisplaySettingsDialog))
    assert not smoothen_determinant == new_settings.smoothen_determinant
    assert not draw_parallelogram == new_settings.draw_determinant_parallelogram
