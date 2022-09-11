# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides the :class:`GlobalSettings` class, which is used to access global settings."""

from __future__ import annotations

import configparser
import os
import subprocess
import sys
from pathlib import Path
from typing import Literal

from singleton_decorator import singleton

_DEFAULT_CONFIG = '''
[General]
# Valid options are "auto", "prompt", or "never"
# An unknown option will default to "never"
Updates = prompt
'''[1:]


@singleton
class GlobalSettings():
    """A singleton class to provide global settings that can be shared throughout the app.

    .. note::
       This is a singleton class because we only want :meth:`__init__` to be called once
       to reduce processing time. We also can't cache it as a global variable because that
       would be created at import time, leading to infinite process recursion when lintrans
       tries to call its own executable to find out if it's compiled or interpreted.

    The directory methods are split up into things like :meth:`get_save_directory` and
    :meth:`get_crash_reports_directory` to make sure the directories exist and discourage
    the use of other directories in the root one.
    """

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

        self._executable_path = ''

        executable_path = sys.executable
        if os.path.isfile(executable_path):
            version_output = subprocess.run(
                [executable_path, '--version'],
                stdout=subprocess.PIPE,
                shell=(os.name == 'nt')
            ).stdout.decode()

            if 'lintrans' in version_output:
                self._executable_path = executable_path

        self._settings_file = os.path.join(self._directory, 'settings.ini')
        config = configparser.ConfigParser()
        config.read(self._settings_file)

        try:
            self._general_settings = config['General']
        except KeyError:
            with open(self._settings_file, 'w', encoding='utf-8') as f:
                f.write(_DEFAULT_CONFIG)

            default_config = configparser.ConfigParser()
            default_config.read(self._settings_file)

            self._general_settings = default_config['General']

    def get_save_directory(self) -> str:
        """Return the default directory for save files."""
        return os.path.join(self._directory, 'saves')

    def get_crash_reports_directory(self) -> str:
        """Return the default directory for crash reports."""
        return os.path.join(self._directory, 'crash_reports')

    def get_executable_path(self) -> str:
        """Return the path to the binary executable, or an empty string if lintrans is not installed standalone."""
        return self._executable_path

    def get_update_type(self) -> Literal['auto', 'prompt', 'never']:
        """Return the update type defined in the settings file.

        The update type is guaranteed to be ``'auto'``, ``'prompt'``, or ``'never'``. I could've
        used an enum but then I'd have to import that enum type just to check the return value.
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

    def set_update_type(self, type: Literal['auto', 'prompt', 'never']) -> None:
        """Set the update type in the settings file to the given type."""
        self._general_settings['Updates'] = type

        new_settings_file = _DEFAULT_CONFIG.replace(
            'Updates = prompt',
            f'Updates = {type}'
        )

        with open(self._settings_file, 'w', encoding='utf-8') as f:
            f.write(new_settings_file)

    def get_settings_file(self) -> str:
        """Return the full path of the settings file."""
        return self._settings_file

    def get_update_download_filename(self) -> str:
        """Return a name for a temporary file next to the executable.

        This method is used when downloading a new version of lintrans into a temporary file.
        This is needed to allow :func:`os.rename` instead of :func:`shutil.move`. The first
        requires the src and dest to be on the same partition, but also allows us to replace
        the running executable.
        """
        return str(Path(self._executable_path).parent / 'temp.dat')
