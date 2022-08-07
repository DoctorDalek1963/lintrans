#!/usr/bin/env python

# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides a :func:`main` function to interpret command line arguments and run the program."""

from argparse import ArgumentParser
from textwrap import dedent

from lintrans import __version__, gui
from lintrans.crash_reporting import set_excepthook, set_signal_handler


def main() -> None:
    """Interpret program-specific command line arguments and run the main window in most cases.

    If the user supplies --help or --version, then we simply respond to that and then return.
    If they don't supply either of these, then we run :func:`lintrans.gui.main_window.main`.

    :param List[str] args: The full argument list (including program name)
    """
    parser = ArgumentParser(add_help=False)

    parser.add_argument(
        'filename',
        nargs='?',
        type=str,
        default=None
    )

    parser.add_argument(
        '-h',
        '--help',
        default=False,
        action='store_true'
    )

    parser.add_argument(
        '-V',
        '--version',
        default=False,
        action='store_true'
    )

    parsed_args = parser.parse_args()

    if parsed_args.help:
        print(dedent('''
        Usage: lintrans [option] [filename]

        Arguments:
            filename         The name of a session file to open

        Options:
            -h, --help       Display this help text and exit
            -V, --version    Display the version information and exit'''[1:]))
        return

    if parsed_args.version:
        print(dedent(f'''
        lintrans (version {__version__})
        The linear transformation visualizer

        Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

        This program is licensed under GNU GPLv3, available here:
        <https://www.gnu.org/licenses/gpl-3.0.html>'''[1:]))
        return

    gui.main(parsed_args.filename)


if __name__ == '__main__':
    set_excepthook()
    set_signal_handler()
    main()
