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

import os
import platform
import signal
import sys
from datetime import datetime
from signal import SIGABRT, SIGFPE, SIGILL, SIGSEGV, SIGTERM
from textwrap import indent
from types import FrameType, TracebackType
from typing import NoReturn, Type

from PyQt5.QtCore import PYQT_VERSION_STR, QT_VERSION_STR
from PyQt5.QtWidgets import QApplication

import lintrans
from lintrans.typing_ import is_matrix_type

from .global_settings import GlobalSettings
from .gui.main_window import LintransMainWindow


def _get_datetime_string() -> str:
    """Get the date and time as a string with a space in the middle."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def _get_main_window() -> LintransMainWindow:
    """Return the only instance of :class:`~lintrans.gui.main_window.LintransMainWindow`.

    :raises RuntimeError: If there is not exactly 1 instance of :class:`~lintrans.gui.main_window.LintransMainWindow`
    """
    widgets = [
        x for x in QApplication.topLevelWidgets()
        if isinstance(x, LintransMainWindow)
    ]

    if len(widgets) != 1:
        raise RuntimeError(f'Expected 1 widget of type LintransMainWindow but found {len(widgets)}')

    return widgets[0]


def _get_system_info() -> str:
    """Return a string of all the system we could gather."""
    info = 'SYSTEM INFO:\n'

    info += f'  lintrans: {lintrans.__version__}\n'
    info += f'  Python: {platform.python_version()}\n'
    info += f'  Qt5: {QT_VERSION_STR}\n'
    info += f'  PyQt5: {PYQT_VERSION_STR}\n'
    info += f'  Platform: {platform.platform()}\n'

    info += '\n'
    return info


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

        origin += f'  Exception "{exc_value}"\n  of type {exc_type.__name__} in call to {frame.f_code.co_name}()\n' \
            f'  on line {frame.f_lineno} of {frame.f_code.co_filename}'

    elif signal_number is not None and stack_frame is not None:
        origin += f'  Signal "{signal.strsignal(signal_number)}" received in call to {stack_frame.f_code.co_name}()\n' \
            f'  on line {stack_frame.f_lineno} of {stack_frame.f_code.co_filename}'

    else:
        origin += '  UNKNOWN (not exception or signal)'

    origin += '\n\n'

    return origin


def _get_display_settings() -> str:
    """Return a string representing all of the display settings."""
    raw_settings = _get_main_window()._plot.display_settings
    display_settings = {
        k: getattr(raw_settings, k)
        for k in raw_settings.__slots__
        if not k.startswith('_')
    }

    string = 'Display settings:\n'

    for setting, value in display_settings.items():
        string += f'  {setting}: {value}\n'

    return string


def _get_post_mortem() -> str:
    """Return whatever post mortem data we could gather from the window."""
    window = _get_main_window()

    try:
        matrix_wrapper = window._matrix_wrapper
        expression_history = window._expression_history
        exp_hist_index = window._expression_history_index
        plot = window._plot
        point_i = plot.point_i
        point_j = plot.point_j

    except (AttributeError, RuntimeError) as e:
        return f'UNABLE TO GET POST MORTEM DATA:\n  {e!r}\n'

    post_mortem = 'Matrix wrapper:\n'

    for matrix_name, matrix_value in matrix_wrapper.get_defined_matrices():
        post_mortem += f'  {matrix_name}: '

        if is_matrix_type(matrix_value):
            post_mortem += f'[{matrix_value[0][0]} {matrix_value[0][1]}; {matrix_value[1][0]} {matrix_value[1][1]}]'
        else:
            post_mortem += f'"{matrix_value}"'

        post_mortem += '\n'

    post_mortem += f'\nExpression box: "{window._lineedit_expression_box.text()}"'
    post_mortem += f'\nCurrently displayed: [{point_i[0]} {point_j[0]}; {point_i[1]} {point_j[1]}]'
    post_mortem += f'\nAnimating (sequence): {window._animating} ({window._animating_sequence})\n'

    post_mortem += f'\nExpression history (index={exp_hist_index}):'
    post_mortem += '\n  ['
    for item in expression_history:
        post_mortem += f'\n    {item!r},'
    post_mortem += '\n  ]\n'

    post_mortem += f'\nGrid spacing: {plot.grid_spacing}'
    post_mortem += f'\nWindow size: {window.width()} x {window.height()}'
    post_mortem += f'\nViewport size: {plot.width()} x {plot.height()}'
    post_mortem += f'\nGrid corner: {plot._grid_corner()}\n'

    post_mortem += '\n' + _get_display_settings()

    string = 'POST MORTEM:\n'
    string += indent(post_mortem, '  ')
    return string


def _get_crash_report(datetime_string: str, error_origin: str) -> str:
    """Return a string crash report, ready to be written to a file and stderr.

    :param str datetime_string: The datetime to use in the report; should be the same as the one in the filename
    :param str error_origin: The origin of the error. Get this by calling :func:`_get_error_origin`
    """
    report = f'CRASH REPORT at {datetime_string}\n\n'
    report += _get_system_info()
    report += error_origin
    report += _get_post_mortem()

    return report


def _report_crash(
    *,
    exc_type: Type[BaseException] | None = None,
    exc_value: BaseException | None = None,
    traceback: TracebackType | None = None,
    signal_number: int | None = None,
    stack_frame: FrameType | None = None
) -> NoReturn:
    """Generate a crash report and write it to a log file and stderr.

    See :func:`_get_error_origin` for an explanation of the arguments. Everything is
    handled internally if you just use the public functions :func:`set_excepthook` and
    :func:`set_signal_handler`.
    """
    datetime_string = _get_datetime_string()

    filename = os.path.join(
        GlobalSettings().get_crash_reports_directory(),
        datetime_string.replace(" ", "_") + '.log'
    )
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

    print('\n\n' + report, end='', file=sys.stderr)
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

    sys.excepthook = _custom_excepthook


def set_signal_handler() -> None:
    """Set the signal handlers to generate crash reports first."""
    def _handler(number, frame) -> None:
        _report_crash(signal_number=number, stack_frame=frame)

    for sig_num in (SIGABRT, SIGFPE, SIGILL, SIGSEGV, SIGTERM):
        if sig_num in signal.valid_signals():
            signal.signal(sig_num, _handler)

    try:
        from signal import SIGQUIT
        signal.signal(SIGQUIT, _handler)
    except ImportError:
        pass
