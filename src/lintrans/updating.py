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
import shlex
import shutil
import subprocess
import tempfile
from packaging import version
from urllib.request import urlopen

from lintrans.global_settings import global_settings


def update_lintrans() -> None:
    """Update the lintrans binary executable, failing silently.

    This function only makes sense if lintrans was installed, rather than being used as an executable.
    We ask the :attr:`~lintrans.global_settings.global_settings` object where the executable is and,
    if it exists, we check if a newer version is available. If it is, then we replace the old executable
    with the new one.

    This means that the next time lintrans gets run, it will use the most recent version.
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

    # If the executable doesn't exist, then we definitely want to update it
    if os.path.isfile(executable_path):
        version_output = subprocess.run(
            [shlex.quote(executable_path), '--version'],
            stdout=subprocess.PIPE
        ).stdout.decode()

        match = re.search(r'(?<=lintrans \(version )\d+\.\d+\.\d+(?=\))', version_output)

        if match is None:
            return

        current_version = version.parse(match.group(0))

        if latest_version <= current_version:
            return

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

    with open(temp_file, 'wb') as f:
        f.write(urlopen(url).read())

    # os.rename() can fail on POSIX systems if /tmp is in a different partition to that of the destination
    shutil.move(temp_file, executable_path)

    if os.name == 'posix':
        os.system('chmod +x ' + shlex.quote(executable_path))
