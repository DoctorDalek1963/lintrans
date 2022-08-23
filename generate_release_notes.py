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

I *highly* recommend reading the tutorial, available [here](https://lintrans.readthedocs.io/en/VERSION_RTD/tutorial/).

---

The Windows `.exe` file should work fine, but you might get a warning that the program might be unsafe. This is expected and it's safe to ignore it. The only way to get rid of it would be to pay Microsoft. On macOS, I would need to pay Apple to allow other people to run it at all.

If this warning bothers you or if you want to use `lintrans` on macOS, then you can compile the program from its source code. This is a relatively simple process and the tutorial for doing that is available [here](https://lintrans.readthedocs.io/en/VERSION_RTD/compilation/).

The Linux binary is a dynamically linked ELF compiled on Ubuntu 20.04 and may or may not work on other distros. Compiling is also an option for Linux. See the tutorial above.

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
        text = text.replace('VERSION_RTD', tag_name)

    else:
        raise ValueError('Error in searching for changelog notes. Bad format')

    with open('release_notes.md', 'w', encoding='utf-8') as f:
        f.write(text)


if __name__ == '__main__':
    main(sys.argv[1:])
