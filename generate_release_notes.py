#!/usr/bin/env python

# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""A very simple script to generate release notes."""

import re
import sys

TEXT = '''DESCRIPTION

---

The Linux binary should work fine, but if you use the Windows `.exe` file, you will get a warning that the program may be unsafe. This is expected and you can just ignore it. This is caused by me not being able to afford a certificate from Microsoft, and there's no binary for macOS for the same reason.

If you're running macOS, then you will need to compile the program from source. This is also an option on Linux and Windows. Instructions can be found [here](https://doctordalek1963.github.io/lintrans/tutorial/compile/).

---

CHANGELOG
'''

# This RegEx is complicated because of the newlines
# It requires the current tag to have a header like
# ## [0.2.1] - 2022-03-22
# And all other tags to have similar headers
# It also won't work on the first tag, but that's fine
RE_PATTERN = r'''(?<=## \[TAG_NAME\] - \d{4}-\d{2}-\d{2}

).*?(?=

## \[\d+\.\d+\.\d+(-[\S]+)?\] - \d{4}-\d{2}-\d{2})'''


def main(args: list[str]) -> None:
    """Generate the release notes for this release and write them to `release_notes.md`."""
    if len(args) < 1:
        raise ValueError('Tag name is required to generate release notes')

    tag_name = args[0]

    print(f'Generating release notes for tag {tag_name}')

    with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
        changelog_text = f.read()

    if (m := re.search(
        RE_PATTERN.replace('TAG_NAME', re.escape(tag_name[1:])),
        changelog_text,
        flags=re.S
    )) is not None:
        text = TEXT.replace('CHANGELOG', m.group(0))

    else:
        raise ValueError('Error in searching for changelog notes. Bad format')

    with open('release_notes.md', 'w', encoding='utf-8') as f:
        f.write(text)


if __name__ == '__main__':
    main(sys.argv[1:])
