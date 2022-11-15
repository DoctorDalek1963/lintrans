# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides the :class:`GlobalSettings` class, which is used to access global settings."""

from __future__ import annotations

import os
import pathlib
import pickle
import subprocess
import sys
from copy import copy
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

from singleton_decorator import singleton

import lintrans

UpdateType = Enum('UpdateType', 'auto prompt never')
"""An enum of possible update prompt types."""


@dataclass(slots=True)
class GlobalSettingsData:
    """A simple dataclass to store the configurable data of the global settings."""

    update_type: UpdateType = UpdateType.prompt
    """This is the desired type of update prompting."""

    cursor_epsilon: int = 5
    """This is the distance in pixels that the cursor needs to be from the point to drag it."""

    snap_dist: float = 0.1
    """This is the distance in grid coords that the cursor needs to be from an integer point to snap to it."""

    def save_to_file(self, filename: str) -> None:
        """Save the global settings data to a file, creating parent directories as needed."""
        parent_dir = pathlib.Path(os.path.expanduser(filename)).parent.absolute()

        if not os.path.isdir(parent_dir):
            os.makedirs(parent_dir)

        data: Tuple[str, GlobalSettingsData] = (lintrans.__version__, self)

        with open(filename, 'wb') as f:
            pickle.dump(data, f, protocol=4)

    @classmethod
    def load_from_file(cls, filename: str) -> Tuple[str, GlobalSettingsData]:
        """Return the global settings data that was previously saved to ``filename`` along with some extra information.

        The tuple we return has the version of lintrans that was used to save the file, and the data itself.

        :raises EOFError: If the file doesn't contain a pickled Python object
        :raises FileNotFoundError: If the file doesn't exist
        :raises ValueError: If the file contains a pickled object of the wrong type
        """
        if not os.path.isfile(filename):
            return lintrans.__version__, cls()

        with open(filename, 'rb') as f:
            file_data = pickle.load(f)

        if not isinstance(file_data, tuple):
            raise ValueError(f'File {filename} contains pickled object of the wrong type (must be tuple)')

        # Create a default object and overwrite the fields that we have
        data = cls()
        for attr in file_data[1].__slots__:
            setattr(data, attr, getattr(file_data[1], attr))

        return file_data[0], data


@singleton
class GlobalSettings:
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
            # lintrans is only compatible with Python >= 3.10 anyway
            raise OSError(f'Unrecognised OS "{os.name}"')

        sub_directories = ['saves', 'crash_reports']

        os.makedirs(self._directory, exist_ok=True)
        for sub_directory in sub_directories:
            os.makedirs(os.path.join(self._directory, sub_directory), exist_ok=True)

        self._executable_path: Optional[str] = None

        self._settings_file = os.path.join(self._directory, 'settings.dat')
        self._display_settings_file = os.path.join(self._directory, 'display_settings.dat')

        try:
            self._data = GlobalSettingsData.load_from_file(self._settings_file)[1]
        except KeyError:
            self._data = GlobalSettingsData()
            self._data.save_to_file(self._settings_file)

    def get_executable_path(self) -> str:
        """Return the path to the binary executable, or an empty string if lintrans is not installed standalone.

        This method will call :attr:`sys.executable` to see if it's lintrans. If it is, then we cache the path for
        future use and return it. Otherwise, it's a Python interpreter, so we return an empty string instead.
        """
        if self._executable_path is None:
            executable_path = sys.executable
            if os.path.isfile(executable_path):
                version_output = subprocess.run(
                    [executable_path, '--version'],
                    stdout=subprocess.PIPE,
                    shell=(os.name == 'nt')
                ).stdout.decode()

                if 'lintrans' in version_output:
                    self._executable_path = executable_path
                else:
                    self._executable_path = ''

        return self._executable_path or ''

    def get_save_directory(self) -> str:
        """Return the default directory for save files."""
        return os.path.join(self._directory, 'saves')

    def get_crash_reports_directory(self) -> str:
        """Return the default directory for crash reports."""
        return os.path.join(self._directory, 'crash_reports')

    def get_settings_file(self) -> str:
        """Return the full path of the settings file."""
        return self._settings_file

    def save_display_settings(self, settings: lintrans.gui.settings.DisplaySettings) -> None:
        """Save the given display settings to the default file."""
        settings.save_to_file(self._display_settings_file)

    def get_display_settings(self) -> lintrans.gui.settings.DisplaySettings:
        """Get the display settings from the default file, using the defaults for anything that's not available."""
        return lintrans.gui.settings.DisplaySettings.load_from_file(self._display_settings_file)[1]

    def get_update_download_filename(self) -> str:
        """Return a name for a temporary file next to the executable.

        This method is used when downloading a new version of lintrans into a temporary file.
        This is needed to allow :func:`os.rename` instead of :func:`shutil.move`. The first
        requires the src and dest to be on the same partition, but also allows us to replace
        the running executable.
        """
        return str(Path(self.get_executable_path()).parent / 'lintrans-update-temp.dat')

    def get_update_replace_bat_filename(self) -> str:
        """Return the full path of the ``replace.bat`` file needed to update on Windows.

        See :meth:`get_update_download_filename`.
        """
        return str(Path(self.get_executable_path()).parent / 'replace.bat')

    def get_data(self) -> GlobalSettingsData:
        """Return a copy of the internal global settings data."""
        return copy(self._data)

    def set_data(self, data: GlobalSettingsData) -> None:
        """Set the internal global settings data and save it to a file."""
        self._data = data
        self._data.save_to_file(self._settings_file)

    def set_update_type(self, type_: UpdateType) -> None:
        """Set the internal data update type."""
        data = self.get_data()
        data.update_type = type_
        self.set_data(data)
