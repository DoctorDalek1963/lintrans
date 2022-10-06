# lintrans - The linear transformation visualizer
# Copyright (C) 2022 D. Dyson (DoctorDalek1963)
#
# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""Test that the non-defintion dialogs work as expected."""

from typing import Type

import pytest
from conftest import get_open_widget, is_widget_class_open
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from pytestqt.qtbot import QtBot

from lintrans.gui.dialogs import DisplaySettingsDialog, InfoPanelDialog
from lintrans.gui.main_window import LintransMainWindow


@pytest.mark.parametrize(
    'button_attr,dialog_class',
    [
        ('_button_change_display_settings', DisplaySettingsDialog),
        ('_button_info_panel', InfoPanelDialog),
    ]
)
def test_dialogs_open(
    qtbot: QtBot,
    window: LintransMainWindow,
    button_attr: str,
    dialog_class: Type[QDialog]
) -> None:
    """Make sure the dialog opens properly."""
    qtbot.mouseClick(getattr(window, button_attr), Qt.LeftButton)
    assert is_widget_class_open(dialog_class)
    qtbot.addWidget(get_open_widget(dialog_class))
