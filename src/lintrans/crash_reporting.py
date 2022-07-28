# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides functions to report crashes and log them.

The only functions you should be calling directly are :func:`set_excepthook`
and :func:`set_signal_handler` to setup handlers for unhandled exceptions
and unhandled operating system signals respectively.
"""

from __future__ import annotations

import sys
from datetime import datetime
from signal import signal, SIGABRT, SIGFPE, SIGILL, SIGSEGV, SIGTERM, strsignal
from types import FrameType, TracebackType
from typing import Type

from PyQt5.QtWidgets import QApplication

from lintrans.typing_ import is_matrix_type
from .gui.main_window import LintransMainWindow


def _get_datetime_string() -> str:
    """Get the date and time as a string with a space in the middle."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def _get_main_window() -> LintransMainWindow:
    """Return the only instance of :class:`lintrans.gui.main_window.LintransMainWindow`.

    :raises RuntimeError: If there is not exactly 1 instance of :class:`lintrans.gui.main_window.LintransMainWindow`
    """
    widgets = [
        x for x in QApplication.topLevelWidgets()
        if isinstance(x, LintransMainWindow)
    ]

    if len(widgets) != 1:
        raise RuntimeError(f'Expected 1 widget of type LintransMainWindow but found {len(widgets)}')

    return widgets[0]


def _get_error_origin(
    *,
    exc_type: Type[BaseException] | None,
    exc_value: BaseException | None,
    traceback: TracebackType | None,
    signal_number: int | None,
    stack_frame: FrameType | None
) -> str:
    """Return a string specifying the full origin of the error, as best as we can determine.

    This function has effectively two signatures. If the fatal error is caused by an exception,
    then the first 3 arguments will be used to match the signature of :func:`sys.excepthook`.
    If it's caused by a signal, then the last two will be used to match the signature of the
    handler in :func:`signal.signal`. This function should never be used outside this file, so
    we don't account for a mixture of arguments.

    :param exc_type: The type of the exception that caused the crash
    :param exc_value: The value of the exception itself
    :param traceback: The traceback object
    :param signal_number: The number of the signal that caused the crash
    :param stack_frame: The current stack frame object

    :type exc_type: Type[BaseException] | None
    :type exc_value: BaseException | None
    :type traceback: types.TracebackType | None
    :type signal_number: int | None
    :type stack_frame: types.FrameType | None
    """
    origin = 'CRASH ORIGIN:\n'

    if exc_type is not None and exc_value is not None and traceback is not None:
        # We want the frame where the exception actually occurred, so we have to descend the traceback
        # I don't know why we aren't given this traceback in the first place
        tb = traceback
        while tb.tb_next is not None:
            tb = tb.tb_next

        frame = tb.tb_frame

        origin += f'  Exception "{exc_value}" of type {exc_type.__name__} in call to {frame.f_code.co_name}() on' \
            f'line {frame.f_lineno} of {frame.f_code.co_filename}'

    elif signal_number is not None and stack_frame is not None:
        origin += f'  Signal "{strsignal(signal_number)}" received in call to {stack_frame.f_code.co_name}() on ' \
            f'line {stack_frame.f_lineno} of {stack_frame.f_code.co_filename}'

    else:
        origin += '  UNKNOWN (not exception or signal)'

    origin += '\n\n'

    return origin


def _get_crash_report(datetime_string: str, error_origin: str) -> str:
    """Return a string crash report, ready to be written to a file and stderr.

    :param str datetime_string: The datetime to use in the report; should be the same as the one in the filename
    :param str error_origin: The origin of the error. Get this by calling :func:`_get_error_origin`
    """
    report = f'CRASH REPORT at {datetime_string}\n\n'
    window = _get_main_window()
    matrix_wrapper = window._matrix_wrapper

    report += error_origin

    report += 'Matrix wrapper:\n'

    for matrix_name, matrix_value in matrix_wrapper.get_defined_matrices():
        report += f'  {matrix_name}: '

        if is_matrix_type(matrix_value):
            report += f'[{matrix_value[0][0]} {matrix_value[0][1]}; {matrix_value[1][0]} {matrix_value[1][1]}]'
        else:
            report += matrix_value

        report += '\n'

    return report


def _report_crash(
    *,
    exc_type: Type[BaseException] | None = None,
    exc_value: BaseException | None = None,
    traceback: TracebackType | None = None,
    signal_number: int | None = None,
    stack_frame: FrameType | None = None
) -> None:
    """Generate a crash report and write it to a log file and stderr.

    See :func:`_get_error_origin` for an explanation of the arguments. Everything is
    handled internally if you just use the public functions :func:`set_excepthook` and
    :func:`set_signal_handler`.
    """
    datetime_string = _get_datetime_string()

    filename = f'lintrans_crash_report_{datetime_string.replace(" ", "_")}.log'
    report = _get_crash_report(
        datetime_string,
        _get_error_origin(
            exc_type=exc_type,
            exc_value=exc_value,
            traceback=traceback,
            signal_number=signal_number,
            stack_frame=stack_frame
        )
    )

    print(report, end='', file=sys.stderr)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)

    sys.exit(255)


def set_excepthook() -> None:
    """Change :func:`sys.excepthook` to generate a crash report first."""
    def _custom_excepthook(
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType | None
    ) -> None:
        _report_crash(exc_type=exc_type, exc_value=exc_value, traceback=traceback)
        sys.__excepthook__(exc_type, exc_value, traceback)

    sys.excepthook = _custom_excepthook


def set_signal_handler() -> None:
    """Set the signal handlers to generate crash reports first."""
    def _handler(number, frame) -> None:
        _report_crash(signal_number=number, stack_frame=frame)

    for sig_num in (SIGABRT, SIGFPE, SIGILL, SIGSEGV, SIGTERM):
        signal(sig_num, _handler)
