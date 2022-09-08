#!/usr/bin/env python

# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""A simple compile script for users to compile lintrans themselves, also used by the GitHub action."""

import argparse
import os
import re
import shlex
import shutil
import sys
from importlib import import_module
from importlib.util import find_spec
from textwrap import dedent
from typing import List


def check_dependencies() -> None:
    """Check that all dependencies are installed and if they're not, print an error and the command to install them."""
    # This list contains tuples of (import_name, package_name, version_attr)
    # We look for the import_name spec and if we can't find it, then we require the user to install package_name
    # PyQt5 seems to be a bit complicated, so we look for PyQt5.QtCore to make sure the pacakge is properly installed
    dependencies = [
        ('nptyping', 'nptyping==1.4.4', '__version__'),
        ('numpy', 'numpy==1.23.0', '__version__'),
        ('PIL', 'Pillow==9.2.0', '__version__'),
        ('PyInstaller', 'pyinstaller==5.3', '__version__'),
        ('PyQt5.QtCore', 'pyqt5==5.15.6', 'PYQT_VERSION_STR')
    ]
    unmet = []

    # Thanks to David Beazley for teaching me how Python imports work
    # https://www.youtube.com/watch?v=0oTh1CXRaQ0

    for import_name, package_name, version_attr in dependencies:
        # We don't have to import the module, we can just check if we COULD import it
        if find_spec(import_name) is None:
            unmet.append(shlex.quote(package_name))

        else:
            # Even if it's installed, we need the right version
            # (I'm looking at you, nptyping)
            expected_version = package_name.split('==')[1]

            # This line imports the module and checks its version attribute, all programmatically
            if getattr(import_module(import_name), version_attr) != expected_version:
                unmet.append(shlex.quote(package_name))

    lintrans_needed = find_spec('lintrans') is None

    if len(unmet) == 0 and not lintrans_needed:
        return

    command = f'{sys.executable} -m pip install {" ".join(unmet)}'

    if lintrans_needed:
        if command.endswith(' '):
            command = command[:-1]

        command += ' -e .'

    print(' ERROR: Unmet dependencies '.center(os.get_terminal_size().columns, '='))
    print()
    print('Please run the following command to install the needed dependencies:')
    print('  ' + command)
    print()
    print('Then run this script again to compile.')
    print()
    sys.exit(1)


check_dependencies()

from PyInstaller.__main__ import run as run_pyi

import lintrans


OS_NAME_DICT = {
    'darwin': 'macOS',
    'linux': 'Linux',
    'win32': 'Windows'
}


class Compiler:
    """A simple class to encapsulate compilation logic."""

    def __init__(
            self, *,
            fullname: bool,
            version_name: str
    ):
        """Create a Compiler object."""
        self.version_name = version_name
        self.platform = sys.platform

        if fullname:
            self.filename = f'lintrans-{OS_NAME_DICT[self.platform]}-{self.version_name}'
        else:
            self.filename = 'lintrans'

        print(f'Created {self!r}')

    def __repr__(self) -> str:
        """Return a simple repr of the object."""
        return f'Compiler(filename={self.filename}, version_name={self.version_name}, platform={self.platform})'

    def _windows_generate_version_info(self) -> None:
        """Generate version_info.txt for Windows."""
        if (m := re.match(r'v?(\d+)\.(\d+)\.(\d+)(-[^ ]+)?', self.version_name)) is not None:
            major, minor, patch, dev_part = m.groups()

        else:
            raise ValueError('Tag name must match format')

        if dev_part is not None:
            flags = '0x2'
        else:
            flags = '0x0'

        version_tuple = f'{major}, {minor}, {patch}, 0'

        print(f'Generating Windows version file with tuple=({version_tuple}) and dev_part={dev_part}')

        version_info = dedent(f'''
        VSVersionInfo(
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
                    StringStruct('FileDescription', 'lintrans'),
                    StringStruct('FileVersion', '{self.version_name}'),
                    StringStruct('InternalName', 'lintrans'),
                    StringStruct('LegalCopyright', '(C) D. Dyson (DoctorDalek1963) under GPLv3'),
                    StringStruct('OriginalFilename', '{self.filename}.exe'),
                    StringStruct('ProductName', 'lintrans'),
                    StringStruct('ProductVersion', '{self.version_name}')
                  ]
                )
              ]
            ),
            VarFileInfo([VarStruct('Translation', [2057, 1200])])
          ]
        )
        '''[1:])

        with open('version_info.txt', 'w', encoding='utf-8') as f:
            f.write(version_info)

        print('Version file written to version_info.txt')

    def _macos_replace_info_plist(self) -> None:
        """Replace the Info.plist file in the macOS app."""
        short_version_name = self.version_name

        if (m := re.match(r'v?(\d+\.\d+\.\d+)(-[^ ]+)?', short_version_name)) is not None:
            short_version_name = m.group(1)

        print(f'Generating macOS Info.plist with short_version_name={short_version_name}')

        new_info_plist = dedent(f'''
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"
        <plist version="1.0">
        <dict>
            <key>CFBundleDisplayName</key>
            <string>lintrans</string>
            <key>CFBundleExecutable</key>
            <string>lintrans</string>
            <key>CFBundleIconFile</key>
            <string>icon-windowed.icns</string>
            <key>CFBundleIdentifier</key>
            <string>lintrans</string>
            <key>CFBundleInfoDictionaryVersion</key>
            <string>6.0</string>
            <key>CFBundleName</key>
            <string>lintrans</string>
            <key>CFBundleType</key>
            <string>APPL</string>
            <key>CFBundleVersion</key>
            <string>{self.version_name}</string>
            <key>CFBundleShortVersionString</key>
            <string>{short_version_name}</string>
            <key>NSHighResolutionCapable</key>
            <true/>
            <key>NSHumanReadableCopyright</key>
            <string>(C) D. Dyson (DoctorDalek1963) under GPLv3</string>
        </dict>
        </plist>
        '''[1:])

        with open(os.path.join(self.filename + '.app', 'Contents', 'Info.plist'), 'w', encoding='utf-8') as f:
            f.write(new_info_plist)

        print(f'Info.plist replaced in {self.filename}.app')

    def _get_pyi_args(self) -> List[str]:
        """Return the common args for PyInstaller."""
        path_to_icon = os.path.join(os.path.dirname(__file__), 'src', 'lintrans', 'gui', 'assets', '32.xpm')
        icon_dest = os.path.join('.', 'lintrans', 'gui', 'assets')

        return [
            'src/lintrans/__main__.py',
            '--onefile',
            '--windowed',
            '--distpath=./dist',
            '--workpath=./build',
            '--noconfirm',
            '--clean',
            f'--name={self.filename}',
            '--icon',
            path_to_icon,
            '--add-data',
            os.pathsep.join([path_to_icon, icon_dest])
        ]

    def _compile_macos(self) -> None:
        """Compile for macOS."""
        run_pyi(self._get_pyi_args())

        os.rename(os.path.join('dist', self.filename + '.app'), self.filename + '.app')

        self._macos_replace_info_plist()

    def _compile_linux(self) -> None:
        """Compile for Linux."""
        run_pyi(self._get_pyi_args())

        os.rename(os.path.join('dist', self.filename), self.filename)

    def _compile_windows(self) -> None:
        """Compile for Windows."""
        self._windows_generate_version_info()

        assert os.path.isfile('version_info.txt'), 'version_info.txt must exist for Windows compilation'

        run_pyi([
            *self._get_pyi_args(),
            '--version-file',
            'version_info.txt'
        ])

        os.remove('version_info.txt')

        os.rename(os.path.join('dist', self.filename + '.exe'), self.filename + '.exe')

    def compile(self) -> None:
        """Compile for the appropriate operating system."""
        print(f'Compiling for platform={self.platform}')
        if self.platform == 'darwin':
            self._compile_macos()

        elif self.platform == 'linux':
            self._compile_linux()

        elif self.platform == 'win32':
            self._compile_windows()

        else:
            raise ValueError(f'Unsupported operating system "{self.platform}"')

        print('Compilation finished')

        shutil.rmtree('dist')
        shutil.rmtree('build')
        os.remove(self.filename + '.spec')

        print('Auxiliary files cleaned up')


def main() -> None:
    """Run any pre-compilation, and then compile."""
    parser = argparse.ArgumentParser(
        description='Compile this version of lintrans for your operating system',
        add_help=True
    )

    parser.add_argument(
        '-f', '--fullname',
        required=False,
        default=False,
        action='store_true',
        help='whether to use the fullname for compilation (lintrans-platform-version) or the short name (lintrans)'
    )

    args = parser.parse_args()

    compiler = Compiler(fullname=args.fullname, version_name=lintrans.__version__)
    compiler.compile()


if __name__ == '__main__':
    main()
