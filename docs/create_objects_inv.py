#!/usr/bin/env python

# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""A simple script to convert my manually curated text file to an inventory file that intersphinx can use.

The file format for the text files is as follows:
   {name} {domain}:{role} {priority} {uri} {dispname}

The base URI is taken from the relevant element of the ``intersphinx_mapping`` configuration parameter in conf.py.
This is the element with the same key as the project name This is the element with the same key as the project name.

If the display name is ``-``, then it is the same as the reference name.

See https://sphobjinv.readthedocs.io/en/v2.2/syntax.html for details on restrictions.

Additionally, to define the project and version in the text file, the first two non-blank,
non-comment lines MUST be of the form:
   PROJECT=project_name
   VERSION=version_number

The version_name should not contain a leading ``v``.

.. note:: The URIs MUST have .html suffices
"""

import re
from glob import glob

import sphobjinv as soi


pattern = re.compile(r'^(\S+)\s+([^:\s]+):([^:\s]+)\s+(\d+)\s+(\S+)\s+(\S+)$')


def generate_objects_inv(prefix: str) -> None:
    """Generate the ``objects.inv`` file for the specified prefix.

    We read from ``prefix-objects.txt`` and write to ``prefix-objects.inv``,
    so if you want to use ``pyqt5-objects.txt``, then the prefix should be ``pyqt5``.

    :param str prefix: The prefix for the object files

    :raises ValueError: If the file doesn't match the format
    """
    inv = soi.Inventory()

    with open(prefix + '-objects.txt', 'r', encoding='utf-8') as f:
        text = f.read().splitlines()

    # Remove blank lines and comments
    text = [x for x in text if x != '' and not x.lstrip().startswith('#')]

    try:
        inv.project = re.match(r'^PROJECT=(.+)$', text[0]).group(1)
    except (AttributeError, IndexError):
        raise ValueError(f'The first line of {prefix}-objects.txt must be of the form "PROJECT=project_name"')

    try:
        inv.version = re.match(r'^VERSION=([^v][\d.]+)$', text[1]).group(1)
    except (AttributeError, IndexError):
        raise ValueError(f'The second line of {prefix}-objects.txt must be of the form "VERSION=version_number"')


    for line in text[2:]:
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
