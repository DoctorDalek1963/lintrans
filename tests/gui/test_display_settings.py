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
