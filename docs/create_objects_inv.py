#!/usr/bin/env python

# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""A simple script to convert my manually curated text file to an inventory file that intersphinx can use.

.. note:: The URIs in the text file must not have .html suffices
"""

import re
from glob import glob

import sphobjinv as soi


pattern = re.compile(r'^(\S+)\s+([^:\s]+):([^:\s]+)\s+(\d+)\s+(\S+)\s+(\S+)$')


def generate_objects_inv(prefix: str) -> None:
    """Generate the ``objects.inv`` file for PyQt5.

    We read from ``prefix-objects.txt`` and write to ``prefix-objects.inv``,
    so if you want to use ``pyqt5-objects.txt``, then the prefix should be ``pyqt5``.

    :param str prefix: The prefix for the object files
    """
    inv = soi.Inventory()
    inv.project = 'PyQt5'
    inv.version = '5.15'

    with open(prefix + '-objects.txt', 'r', encoding='utf-8') as f:
        text = f.read().splitlines()

    for line in text:
        if line == '' or line.lstrip().startswith('#'):
            continue

        if (match := re.match(pattern, line)) is None:
            raise ValueError(f'Every line in {prefix}-objects.txt must match the pattern')

        name, domain, role, priority, uri, disp_name = match.groups()

        inv.objects.append(soi.DataObjStr(
            name=name, domain=domain, role=role, priority=priority, uri=uri, dispname=disp_name
        ))

    compressed_text = soi.compress(inv.data_file(contract=True))
    soi.writebytes(f'source/{prefix}-objects.inv', compressed_text)


def main() -> None:
    """Call :func:`generate_objects_inv` for every file matching the glob pattern '*-objects.txt'."""
    for filename in glob('*-objects.txt'):
        prefix = filename[:-12]
        print(f'Generating {prefix}-objects.inv')
        generate_objects_inv(prefix)


if __name__ == '__main__':
    main()
