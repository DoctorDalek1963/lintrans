# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This module provides functions for updating the lintrans executable in a proper installation.

If the user is using a standalone executable for lintrans, then we don't know where it is and
we therefore can't update it.
"""

from __future__ import annotations

import os
import re
import subprocess
from threading import Thread
from typing import Optional, Tuple
from urllib.error import URLError
from urllib.request import urlopen

from packaging import version

from lintrans.global_settings import GlobalSettings


def new_version_exists() -> Tuple[bool, Optional[str]]:
    """Check if the latest version of lintrans is newer than the current version.

    This function either returns (False, None) or (True, str) where the string is the new version.

    .. note::
       This function will default to False if it can't get the current or latest version, or if
       :meth:`~lintrans.global_settings.GlobalSettings.get_executable_path` returns ''
       (probablybecause lintrans is being run as a Python package)

       However, it will return True if the executable path is defined but the executable doesn't actually exist.

       This last behaviour is mostly to make testing easier by spoofing
       :meth:`~lintrans.global_settings.GlobalSettings.get_executable_path`.
    """
    executable_path = GlobalSettings().get_executable_path()
    if executable_path == '':
        return False, None

    try:
        html: str = urlopen('https://github.com/DoctorDalek1963/lintrans/releases/latest').read().decode()
    except (UnicodeDecodeError, URLError):
        return False, None

    match = re.search(
        r'(?<=DoctorDalek1963/lintrans/releases/tag/v)\d+\.\d+\.\d+(?=;)',
        html
    )
    if match is None:
        return False, None

    latest_version_str = match.group(0)
    latest_version = version.parse(latest_version_str)

    # If the executable doesn't exist, then we definitely want to update it
    if not os.path.isfile(executable_path):
        return True, latest_version_str

    # Now check the current version
    version_output = subprocess.run(
        [executable_path, '--version'],
        stdout=subprocess.PIPE,
        shell=(os.name == 'nt')
    ).stdout.decode()

    match = re.search(r'(?<=lintrans \(version )\d+\.\d+\.\d+(-\w+(-?\d+))?(?=\))', version_output)

    if match is None:
        return False, None

    current_version = version.parse(match.group(0))

    if latest_version > current_version:
        return True, latest_version_str

    return False, None


def update_lintrans() -> None:
    """Update the lintrans binary executable, failing silently.

    This function only makes sense if lintrans was installed, rather than being used as an executable.
    We ask the :class:`~lintrans.global_settings.GlobalSettings` singleton where the executable is and,
    if it exists, then we replace the old executable with the new one. This means that the next time
    lintrans gets run, it will use the most recent version.

    .. note::
       This function doesn't care if the latest version on GitHub is actually newer than the current
       version. Use :func:`new_version_exists` to check.
    """
    executable_path = GlobalSettings().get_executable_path()
    if executable_path == '':
        return

    try:
        html: str = urlopen('https://github.com/DoctorDalek1963/lintrans/releases/latest').read().decode()
    except (UnicodeDecodeError, URLError):
        return

    match = re.search(
        r'(?<=DoctorDalek1963/lintrans/releases/tag/v)\d+\.\d+\.\d+(?=;)',
        html
    )
    if match is None:
        return

    latest_version = version.parse(match.group(0))

    # We now know that the latest version is newer, and where the executable is,
    # so we can begin the replacement process
    url = 'https://github.com/DoctorDalek1963/lintrans/releases/download/'

    if os.name == 'posix':
        url += f'v{latest_version}/lintrans-Linux-{latest_version}'

    elif os.name == 'nt':
        url += f'v{latest_version}/lintrans-Windows-{latest_version}.exe'

    else:
        return

    temp_file = GlobalSettings().get_update_download_filename()

    # If the temp file already exists, then another instance of lintrans (probably
    # in a background thread) is currently updating, so we don't want to interfere
    if os.path.isfile(temp_file):
        return

    with open(temp_file, 'wb') as f:
        try:
            f.write(urlopen(url).read())
        except URLError:
            return

    if os.name == 'posix':
        os.rename(temp_file, executable_path)
        subprocess.run(['chmod', '+x', executable_path])

    elif os.name == 'nt':
        # On Windows, we need to leave a process running in the background to automatically
        # replace the exe file when lintrans stops running
        script = '@echo off\n' \
            ':loop\n\n' \
            'timeout 5 >nul\n' \
            'tasklist /fi "IMAGENAME eq lintrans.exe" /fo csv 2>nul | find /I "lintrans.exe" >nul\n' \
            'if "%ERRORLEVEL%"=="0" goto :loop\n\n' \
            f'del "{executable_path}"\n' \
            f'rename "{temp_file}" lintrans.exe\n\n' \
            'start /b "" cmd /c del "%~f0"&exit /b'

        replace_bat = GlobalSettings().get_update_replace_bat_filename()
        with open(replace_bat, 'w', encoding='utf-8') as f:
            f.write(script)

        subprocess.Popen(['start', '/min', replace_bat], shell=True)


def update_lintrans_in_background(*, check: bool) -> None:
    """Use multithreading to run :func:`update_lintrans` in the background."""
    def func() -> None:
        if check:
            if new_version_exists()[0]:
                update_lintrans()
        else:
            update_lintrans()

    p = Thread(target=func)
    p.start()
