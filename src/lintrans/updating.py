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
import shutil
import subprocess
import tempfile
from multiprocessing import Process
from typing import Optional, Tuple
from packaging import version
from urllib.request import urlopen

from lintrans.global_settings import global_settings


def new_version_exists() -> Tuple[bool, Optional[str]]:
    """Check if the latest version of lintrans is newer than the current version.

    This function either returns (False, None) or (True, str) where the string is the new version.

    .. note::
       This function will default to False if it can't get the current or latest version, or if
       :meth:`~lintrans.global_settings._GlobalSettings.get_executable_path` returns ''
       (probablybecause lintrans is being run as a Python package)

       However, it will return True if the executable path is defined but the executable doesn't actually exist.

       This last behaviour is mostly to make testing easier by spoofing
       :meth:`~lintrans.global_settings._GlobalSettings.get_executable_path`.
    """
    executable_path = global_settings.get_executable_path()
    if executable_path == '':
        return False, None

    try:
        html: str = urlopen('https://github.com/DoctorDalek1963/lintrans/releases/latest').read().decode()
    except UnicodeDecodeError:
        return False, None

    match = re.search(
        r'(?<=/DoctorDalek1963/lintrans/releases/download/v)\d+\.\d+\.\d+(?=/lintrans)',
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

    match = re.search(r'(?<=lintrans \(version )\d+\.\d+\.\d+(?=\))', version_output)

    if match is None:
        return False, None

    current_version = version.parse(match.group(0))

    if latest_version > current_version:
        return True, latest_version_str

    return False, None


def update_lintrans() -> None:
    """Update the lintrans binary executable, failing silently.

    This function only makes sense if lintrans was installed, rather than being used as an executable.
    We ask the :attr:`~lintrans.global_settings.global_settings` object where the executable is and,
    if it exists, then we replace the old executable with the new one. This means that the next time
    lintrans gets run, it will use the most recent version.

    .. note::
       This function doesn't care if the latest version on GitHub is actually newer than the current
       version. Use :func:`new_version_exists` to check.
    """
    executable_path = global_settings.get_executable_path()
    if executable_path == '':
        return

    try:
        html: str = urlopen('https://github.com/DoctorDalek1963/lintrans/releases/latest').read().decode()
    except UnicodeDecodeError:
        return

    match = re.search(
        r'(?<=/DoctorDalek1963/lintrans/releases/download/v)\d+\.\d+\.\d+(?=/lintrans)',
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

    temp_file = os.path.join(tempfile.gettempdir(), 'lintrans-temp.dat')

    # If the temp file already exists, then another instance of lintrans (probably
    # in a background thread) is currently updating, so we don't want to interfere
    if os.path.isfile(temp_file):
        return

    with open(temp_file, 'wb') as f:
        f.write(urlopen(url).read())

    # os.rename() can fail on POSIX systems if /tmp is in a different partition to that of the destination
    shutil.move(temp_file, executable_path)

    if os.name == 'posix':
        subprocess.run(['chmod', '+x', executable_path])


def update_lintrans_in_background(*, check: bool) -> None:
    """Use multiprocessing to run :func:`update_lintrans` in the background."""
    def func() -> None:
        if check:
            if new_version_exists()[0]:
                update_lintrans()
        else:
            update_lintrans()

    p = Process(target=func)
    p.start()
