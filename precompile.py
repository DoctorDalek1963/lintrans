#!/usr/bin/env python

# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""A simple pre-compile script for the automated GitHub page compilation action."""

import re
import sys


def precompile_macos() -> None:
    """Run the pre-compile steps for macOS."""
    print('Pre-compile for macOS not implemented yet')


def precompile_windows(args: list[str]) -> None:
    """Run the pre-compile steps for Windows."""
    print('Pre-compiling for Windows')

    if len(args) < 1:
        raise ValueError('Windows pre-compile needs tag name argument')

    tag_name = args[0]

    if (m := re.match(r'v(\d+)\.(\d+)\.(\d+)(-alpha)?', tag_name)) is not None:
        major, minor, patch, alpha = m.groups()

    else:
        raise ValueError('Tag name must match format')

    if alpha is not None:
        flags = '0x2'
    else:
        flags = '0x0'

    version_tuple = f'{major}, {minor}, {patch}, 0'

    version_info = f'''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_tuple}),
    prodvers=({version_tuple}),
    mask=0x3f,
    flags={flags},
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          '040904B0',
          kids=[
            StringStruct('CompanyName', 'D. Dyson (DoctorDalek1963)'),
            StringStruct('FileDescription', 'Linear transformation visualizer'),
            StringStruct('FileVersion', '{tag_name}'),
            StringStruct('InternalName', 'lintrans'),
            StringStruct('LegalCopyright', '(C) D. Dyson (DoctorDalek1963) under GPLv3'),
            StringStruct('OriginalFilename', 'lintrans-Windows-{tag_name}.exe'),
            StringStruct('ProductName', 'lintrans'),
            StringStruct('ProductVersion', '{tag_name}')
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct('Translation', [2057, 1200])])
  ]
)
'''

    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)

    print('Version file written to version_info.txt')


def main(args: list[str]) -> None:
    """Evaluate the arguments and pre-compile accordingly."""
    if len(args) < 1:
        raise ValueError('Script must be supplied with the name of an operating system.')

    os_name = args[0].lower()

    if os_name == 'linux':
        print("Linux doesn't need any pre-compilation")

    elif os_name == 'macos':
        precompile_macos()

    elif os_name == 'windows':
        precompile_windows(args[1:])

    else:
        raise ValueError(f'Unsupported operating system "{os_name}"')


if __name__ == '__main__':
    main(sys.argv[1:])
