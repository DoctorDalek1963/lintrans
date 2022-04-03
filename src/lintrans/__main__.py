#!/usr/bin/env python

# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides a :func:`main` function to interpret command line arguments and run the program."""

import sys
from argparse import ArgumentParser
from textwrap import dedent

from lintrans import __version__
from lintrans.gui import main_window


def main(args: list[str]) -> None:
    """Interpret program-specific command line arguments and run the main window in most cases.

    If the user supplies --help or --version, then we simply respond to that and then return.
    If they don't supply either of these, then we run :func:`lintrans.gui.main_window.main`.

    :param list[str] args: The full argument list (including program name)
    """
    parser = ArgumentParser(add_help=False)

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

    parsed_args, unparsed_args = parser.parse_known_args()

    if parsed_args.help:
        print(dedent('''
        Usage: lintrans [option]

        Options:
            -h, --help       Display this help text and exit
            -V, --version    Display the version information and exit

        Any other options will get passed to the QApplication constructor.
        If you don't know what that means, then don't provide any arguments and just the run the program.'''[1:]))
        return

    if parsed_args.version:
        print(dedent(f'''
        lintrans (version {__version__})
        The linear transformation visualizer

        Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

        This program is licensed under GNU GPLv3, available here:
        <https://www.gnu.org/licenses/gpl-3.0.html>'''[1:]))
        return

    for arg in unparsed_args:
        print(f'Passing "{arg}" to QApplication. See --help for recognised args')

    main_window.main(args[:1] + unparsed_args)


if __name__ == '__main__':
    main(sys.argv)
