# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""Test the :class:`DefineDialog` boxes in :class:`LintransMainWindow`."""

import numpy as np
from _pytest.monkeypatch import MonkeyPatch
from PyQt5.QtCore import Qt
from pytestqt.qtbot import QtBot

from lintrans.gui.dialogs import DefineAsAnExpressionDialog, DefineNumericallyDialog, DefineVisuallyDialog
from lintrans.gui.main_window import LintransMainWindow

from conftest import get_open_widget, is_widget_class_open

ALPHABET_NO_I = 'ABCDEFGHJKLMNOPQRSTUVWXYZ'


def test_define_visually_dialog_opens(qtbot: QtBot, window: LintransMainWindow) -> None:
    """Test that the :class:`DefineVisuallyDialog` opens."""
    qtbot.mouseClick(window._button_define_visually, Qt.LeftButton)
    assert is_widget_class_open(DefineVisuallyDialog)
    qtbot.addWidget(get_open_widget(DefineVisuallyDialog))


def test_define_numerically_dialog_opens(qtbot: QtBot, window: LintransMainWindow) -> None:
    """Test that the :class:`DefineNumericallyDialog` opens."""
    qtbot.mouseClick(window._button_define_numerically, Qt.LeftButton)
    assert is_widget_class_open(DefineNumericallyDialog)
    qtbot.addWidget(get_open_widget(DefineNumericallyDialog))


def test_define_as_expression_dialog_opens(qtbot: QtBot, window: LintransMainWindow) -> None:
    """Test that the :class:`DefineAsAnExpressionDialog` opens."""
    qtbot.mouseClick(window._button_define_as_expression, Qt.LeftButton)
    assert is_widget_class_open(DefineAsAnExpressionDialog)
    qtbot.addWidget(get_open_widget(DefineAsAnExpressionDialog))


def test_define_numerically_dialog_works(qtbot: QtBot, monkeypatch: MonkeyPatch, window: LintransMainWindow) -> None:
    """Test that matrices can be defined numerically."""
    qtbot.mouseClick(window._button_define_numerically, Qt.LeftButton)
    dialog = get_open_widget(DefineNumericallyDialog)
    qtbot.addWidget(dialog)

    qtbot.keyClicks(dialog._element_tl, '-1')
    qtbot.keyClicks(dialog._element_tr, '3')
    qtbot.keyClicks(dialog._element_bl, '2')
    qtbot.keyClicks(dialog._element_br, '-0.5')

    qtbot.mouseClick(dialog._button_confirm, Qt.LeftButton)

    assert (window._matrix_wrapper['A'] == np.array([
        [-1, 3],
        [2, -0.5]
    ])).all()
