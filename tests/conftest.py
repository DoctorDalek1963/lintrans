# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""A simple ``conftest.py`` containing some re-usable fixtures and functions."""

import os
from typing import List, Type, TypeVar

import numpy as np
import pytest
from _pytest.config import Config
from _pytest.python import Function
from PyQt5.QtWidgets import QApplication, QWidget
from pytestqt.qtbot import QtBot

from lintrans.gui.main_window import LintransMainWindow
from lintrans.matrices import MatrixWrapper

T = TypeVar('T', bound=QWidget)


def pytest_collection_modifyitems(config: Config, items: List[Function]) -> None:
    """Modify the collected tests so that we only run the GUI tests on Linux (because they need an X server).

    This function is called automatically during the pytest startup. See
    https://docs.pytest.org/en/latest/example/simple.html#control-skipping-of-tests-according-to-command-line-option
    for details.
    """
    skip_gui = pytest.mark.skip(reason='need X server (Linux only) to run GUI tests')
    for item in items:
        if 'gui' in item.location[0] and hasattr(os, 'uname') and os.uname().sysname != 'Linux':
            item.add_marker(skip_gui)


# === Backend stuff

def get_test_wrapper() -> MatrixWrapper:
    """Return a new MatrixWrapper object with some preset values."""
    wrapper = MatrixWrapper()

    root_two_over_two = np.sqrt(2) / 2

    wrapper['A'] = np.array([[1, 2], [3, 4]])
    wrapper['B'] = np.array([[6, 4], [12, 9]])
    wrapper['C'] = np.array([[-1, -3], [4, -12]])
    wrapper['D'] = np.array([[13.2, 9.4], [-3.4, -1.8]])
    wrapper['E'] = np.array([
        [root_two_over_two, -1 * root_two_over_two],
        [root_two_over_two, root_two_over_two]
    ])
    wrapper['F'] = np.array([[-1, 0], [0, 1]])
    wrapper['G'] = np.array([[np.pi, np.e], [1729, 743.631]])

    return wrapper


@pytest.fixture
def test_wrapper() -> MatrixWrapper:
    """Return a new MatrixWrapper object with some preset values."""
    return get_test_wrapper()


@pytest.fixture
def new_wrapper() -> MatrixWrapper:
    """Return a new MatrixWrapper with no initialized values."""
    return MatrixWrapper()


# === GUI stuff

def is_widget_class_open(widget_class: Type[QWidget]) -> bool:
    """Test if a widget with the given class is currently open."""
    return widget_class in [x.__class__ for x in QApplication.topLevelWidgets()]


@pytest.fixture
def window(qtbot: QtBot) -> LintransMainWindow:
    """Return an instance of :class:`LintransMainWindow`."""
    window = LintransMainWindow()
    qtbot.addWidget(window)
    return window


def get_open_widget(widget_class: Type[T]) -> T:
    """Get the open instance of the given :class:`QWidget` subclass.

    This method assumes that there is exactly 1 widget of the given
    class and will raise ``ValueError`` if there's not.

    :raises ValueError: If there is not exactly one widget of the given class
    """
    widgets = [
        x for x in QApplication.topLevelWidgets()
        if isinstance(x, widget_class)
    ]

    if len(widgets) != 1:
        raise ValueError(f'Expected 1 widget of type {widget_class} but found {len(widgets)}')

    return widgets[0]
