# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""Test the :class:`DefineDialog` boxes in :class:`LintransMainWindow`."""
from typing import Type

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from pytestqt.qtbot import QtBot

from lintrans.gui.dialogs import DefineAsAnExpressionDialog, DefineDialog, DefineNumericallyDialog, DefineVisuallyDialog
from lintrans.gui.main_window import LintransMainWindow


def is_dialog_class_open(dialog: Type[DefineDialog]) -> bool:
    """Test if a dialog with the given class is currently open."""
    return dialog in [x.__class__ for x in QApplication.topLevelWidgets()]


@pytest.fixture
def window(qtbot: QtBot) -> LintransMainWindow:
    """Return an instance of :class:`LintransMainWindow`."""
    window = LintransMainWindow()
    qtbot.addWidget(window)
    return window


def test_define_visually_dialog_opens(qtbot: QtBot, window: LintransMainWindow) -> None:
    """Test that the :class:`DefineVisuallyDialog` opens."""
    qtbot.mouseClick(window.button_define_visually, Qt.LeftButton)
    assert is_dialog_class_open(DefineVisuallyDialog)


def test_define_numerically_dialog_opens(qtbot: QtBot, window: LintransMainWindow) -> None:
    """Test that the :class:`DefineNumericallyDialog` opens."""
    qtbot.mouseClick(window.button_define_numerically, Qt.LeftButton)
    assert is_dialog_class_open(DefineNumericallyDialog)


def test_define_as_expression_dialog_opens(qtbot: QtBot, window: LintransMainWindow) -> None:
    """Test that the :class:`DefineAsAnExpressionDialog` opens."""
    qtbot.mouseClick(window.button_define_as_expression, Qt.LeftButton)
    assert is_dialog_class_open(DefineAsAnExpressionDialog)
