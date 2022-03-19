#!/usr/bin/env python

# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides a :func:`main` function to interpret command line arguments and run the program."""

import sys
from textwrap import dedent

from lintrans import __version__
from lintrans.gui import main_window


def main(prog_name: str, args: list[str]) -> None:
    """Interpret program-specific command line arguments and run the main window in most cases.

    If the user supplies --help or --version, then we simply respond to that and then return.
    If they don't supply either of these, then we run :func:`lintrans.gui.main_window.main`.

    ``prog_name`` is ``sys.argv[0]`` when this script is run with ``python -m lintrans``.

    :param str prog_name: The name of the program
    :param list[str] args: The other arguments to the program
    """
    if '-h' in args or '--help' in args:
        print(dedent(f'''
        Usage: {prog_name} [option]

        Options:
            -h, --help       Display this help text and exit
            -V, --version    Display the version information and exit

        Any other options will get passed to the QApplication constructor.
        If you don't know what that means, then don't provide any arguments and just the run the program.'''[1:]))

    elif '-V' in args or '--version' in args:
        print(dedent(f'''
        lintrans (version {__version__})
        The linear transformation visualizer

        Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

        This program is licensed under GNU GPLv3, available here:
        <https://www.gnu.org/licenses/gpl-3.0.html>'''[1:]))

    else:
        main_window.main(args)


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
