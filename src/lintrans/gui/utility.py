# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides utility functions for the whole GUI, such as :func:`qapp`."""

from PyQt5.QtCore import QCoreApplication


def qapp() -> QCoreApplication:
    """Return the equivalent of the global :class:`qApp` pointer.

    :raises RuntimeError: If :meth:`QCoreApplication.instance` returns ``None``
    """
    instance = QCoreApplication.instance()

    if instance is None:
        raise RuntimeError('qApp undefined')

    return instance
