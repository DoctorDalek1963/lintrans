#!/usr/bin/env python

# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This is a simple little script to generate the code appendices for the write-up from the source code."""

import os
from glob import glob


HEADER = r'''\documentclass[../../main.tex]{subfiles}

\begin{document}

'''

FOOTER = '\\end{document}\n'


def generate_files(directory: str, type_: str) -> None:
    """Generate the .tex files for the appendices."""
    filenames = glob(f'lintrans/{directory}/**/*.py', recursive=True)

    if not os.path.isdir('sections/appendices'):
        os.makedirs('sections/appendices')

    with open(f'sections/appendices/{type_}_code.tex', 'w', encoding='utf-8') as f:
        f.write(HEADER)

        for name in filenames:
            stripped_name = name[len(f'lintrans/{directory}/'):]
            f.write(r'\subsection{\texttt{' + stripped_name.replace('_', r'\_') + '}'
                    r'\label{appendix:' + type_ + '-code:' + stripped_name + '}}\n')
            f.write(r'\inputminted{python}{' + name + '}\n\n')

        f.write(FOOTER)


# def src_files() -> None:
    # """Generate the .tex files for the source code (no unit tests)."""
    # filenames = glob('lintrans/src/lintrans/**/*.py', recursive=True)

    # with open('sections/appendices/project_code.tex', 'w', encoding='utf-8') as f:
        # f.write(HEADER)

        # for name in filenames:
            # stripped_name = name[22:]
            # f.write(r'\subsection{\texttt{' + stripped_name.replace('_', r'\_') + '}'
                    # r'\label{appendix:project-code:' + stripped_name + '}}\n')
            # f.write(r'\inputminted{python}{' + name + '}\n\n')

        # f.write(FOOTER)


# def test_files() -> None:
    # """Generate the .tex files for the unit tests."""
    # filenames = glob('lintrans/tests/**/*.py', recursive=True)

    # with open('sections/appendices/testing_code.tex', 'w', encoding='utf-8') as f:
        # f.write(HEADER)

        # for name in filenames:
            # stripped_name = name[22:]
            # f.write(r'\subsection{\texttt{' + stripped_name.replace('_', r'\_') + '}'
                    # r'\label{appendix:testing-code:' + stripped_name + '}}\n')
            # f.write(r'\inputminted{python}{' + name + '}\n\n')

        # f.write(FOOTER)


if __name__ == '__main__':
    generate_files('src/lintrans', 'project')
    generate_files('tests', 'testing')
