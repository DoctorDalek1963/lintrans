#!/usr/bin/env python

# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""A simple script to process code snippets included in .tex files.

Code snippets are written as TeX comments with a : following the %.

For example:

   %: 29ec1fedbf307e3b7ca731c4a381535fec899b0b
   %: src/lintrans/matrices/wrapper.py:10-20

Would reference lines 10-20 of the file src/lintrans/matrices/wrapper.py in commit
29ec1fedbf307e3b7ca731c4a381535fec899b0b on the main branch of lintrans. Line numbers
are optional. If omitted, the whole file is included.
"""

import io
import os
import re
from textwrap import dedent

import git

COMMENT_PATTERN = re.compile(r'(?<=\n)%: ([0-9a-f]+)\n%: ([^\s:]+)(:\d+-\d+)?( strip)?')

COPYRIGHT_COMMENT = '''# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

'''

LINE_NUMBER_HACK = r'''\renewcommand\theFancyVerbLine{
    \ttfamily
    \textcolor[rgb]{0.5,0.5,1}{
        \footnotesize
        \oldstylenums{
            \ifnum\value{FancyVerbLine}=-3 \else
            \ifnum\value{FancyVerbLine}=-2 \else
            \ifnum\value{FancyVerbLine}=-1
                \setcounter{FancyVerbLine}{NUM}
            \else
            \arabic{FancyVerbLine}
            \fi\fi\fi
        }
    }
}'''.replace('    ', '\t')


def process_snippets(filename: str) -> None:
    """Process code snippets in the given file."""
    if not os.path.isfile(filename):
        raise ValueError(f'"{filename}" is not a file')

    with open(filename, 'r', encoding='utf-8') as f:
        full_text = f.read()

    print(f'Processing {filename}')

    for commit_hash, snippet_file_name, lines, strip_flag in re.findall(COMMENT_PATTERN, full_text):
        print(f'  Processing snippet: {commit_hash} {snippet_file_name}{lines}')

        # Get the Repo object and get the desired commit
        repo = git.repo.Repo('lintrans')
        file_blob = repo.commit(commit_hash).tree / snippet_file_name

        # Read the file blob from that commit
        with io.BytesIO(file_blob.data_stream.read()) as f:
            snippet_file_text = f.read().decode('utf-8')

        # If we've got line numbers, use them. If not, use the whole file
        if lines:
            first, last = [int(x) for x in lines[1:].split('-')]
            snippet = '\n'.join(snippet_file_text.splitlines()[first - 1:last])

        else:
            first = 1
            snippet = snippet_file_text

        snippet = snippet.replace(COPYRIGHT_COMMENT, '')

        if snippet.endswith('\n'):
            snippet = snippet[:-1]

        if strip_flag:
            snippet = dedent(snippet)

        # Wrap the snippet from the file in the necessary stuff for LaTeX
        snippet = f'''{{
{LINE_NUMBER_HACK.replace('NUM', str(first - 1))}
\\begin{{minted}}[firstnumber=-3]{{python}}
# {commit_hash}
# {snippet_file_name}

{snippet}
\\end{{minted}}
}}'''

        # Then replace the comments with the actual snippet
        full_text = full_text.replace(
            f'%: {commit_hash}\n%: {snippet_file_name}{lines}{strip_flag}',
            snippet
        )

    # Then just write the file back under a different name
    direc, file = os.path.split(filename)
    with open(os.path.join(direc, 'processed_' + file), 'w', encoding='utf-8') as f:
        f.write(full_text)


if __name__ == '__main__':
    process_snippets('sections/development.tex')
