# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides the :attr:`global_settings` attribute, which should be used to access global settings."""

from __future__ import annotations

import configparser
import os
import shlex
import subprocess
import sys
from typing import Literal

_DEFAULT_CONFIG = '''
[General]
# Valid options are "auto", "prompt", or "never"
# An unknown option will default to never
Updates = prompt
'''[1:]


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

        config_file = os.path.join(self._directory, 'settings.ini')
        config = configparser.ConfigParser()
        config.read(config_file)

        try:
            self._general_settings = config['General']
        except KeyError:
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(_DEFAULT_CONFIG)

            default_config = configparser.ConfigParser()
            default_config.read(config_file)

            self._general_settings = default_config['General']

    def get_save_directory(self) -> str:
        """Return the default directory for save files."""
        return os.path.join(self._directory, 'saves')

    def get_crash_reports_directory(self) -> str:
        """Return the default directory for crash reports."""
        return os.path.join(self._directory, 'crash_reports')

    def get_executable_path(self) -> str:
        """Return the path to the binary executable, or an empty string if lintrans is not installed standalone."""
        executable_path = sys.executable
        if os.path.isfile(executable_path):
            version_output = subprocess.run(
                [shlex.quote(executable_path), '--version'],
                stdout=subprocess.PIPE
            ).stdout.decode()

            if 'lintrans' in version_output:
                return executable_path

        return ''

    def get_update_type(self) -> Literal['auto', 'prompt', 'never']:
        """Return the update type defined in the settings file.

        The update type is guaranteed to be 'auto', 'prompt', or 'never'. I could've used
        an enum but then I'd have to import that enum type just to check the return value.
        """
        try:
            update_type = self._general_settings['Updates'].lower()
        except KeyError:
            return 'never'

        # This is just to satisfy mypy and ensure that we return the Literal
        if update_type == 'auto':
            return 'auto'

        if update_type == 'prompt':
            return 'prompt'

        return 'never'


global_settings = _GlobalSettings()
"""This attribute is the only way that global settings should be accessed.

For the private class, see :class:`_GlobalSettings`.
"""
