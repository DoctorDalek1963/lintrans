# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides the :attr:`global_settings` attribute, which should be used to access global settings."""

from __future__ import annotations

import os


class _GlobalSettings:
    """A class to provide global settings that can be shared throughout the app.

    The directory methods are split up into things like :meth:`get_save_directory` and
    :meth:`get_crash_reports_directory` to make sure the directories exist and discourage
    the use of other directories in the root one.

    .. warning::
       This class should never be directly used and should only be
       accessed through the :attr:`global_settings` attribute.
    """

    def __new__(cls) -> _GlobalSettings:
        """Override :meth:`__new__` to implement a singleton. This class will only be created once."""
        # Only create a new instance if we don't already have one
        if not hasattr(cls, '_instance'):
            cls._instance = super(_GlobalSettings, cls).__new__(cls)

        return cls._instance

    def __init__(self) -> None:
        """Create the global settings object and initialize state."""
        # The root directory is OS-dependent
        if os.name == 'posix':
            self._directory = os.path.join(
                os.path.expanduser('~'),
                '.lintrans'
            )

        elif os.name == 'nt':
            self._directory = os.path.join(
                os.path.expandvars('%APPDATA%'),
                'lintrans'
            )

        else:
            # This should be unreachable because the only other option for os.name is 'java'
            # for Jython, but Jython only supports Python 2.7, which has been EOL for a while
            # lintrans is only compatible with Python >= 3.8 anyway
            raise OSError(f'Unrecognised OS "{os.name}"')

        sub_directories = ['saves', 'crash_reports']

        os.makedirs(self._directory, exist_ok=True)
        for sub_directory in sub_directories:
            os.makedirs(os.path.join(self._directory, sub_directory), exist_ok=True)

    def get_save_directory(self) -> str:
        """Return the default directory for save files."""
        return os.path.join(self._directory, 'saves')

    def get_crash_reports_directory(self) -> str:
        """Return the default directory for crash reports."""
        return os.path.join(self._directory, 'crash_reports')

    def get_executable_path(self) -> str:
        """Return the path to the binary executable, or an empty string if lintrans is not technically installed."""
        # TODO: Implement a settings.conf file for this and the update method
        return '/home/dyson/.local/bin/lintrans'


global_settings = _GlobalSettings()
"""This attribute is the only way that global settings should be accessed.

For the private class, see :class:`_GlobalSettings`.
"""
