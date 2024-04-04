#!/usr/bin/env python

# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This is a simple little script to generate the code appendices for the write-up from the source code."""

import io
import os

import git

HEADER = r"""% lintrans - The linear transformation visualizer
% Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

% This program is licensed under GNU GPLv3, available here:
% <https://www.gnu.org/licenses/gpl-3.0.html>

\documentclass[../../main.tex]{subfiles}

\begin{document}

"""

FOOTER = "\\end{document}\n"


def generate_files(directory: str, type_: str) -> None:
    """Generate the .tex files for the appendices."""
    print(f"Generating appendix for {type_}")

    tree = (
        git.Repo(os.environ["LINTRANS_DIR"])
        .commit("63f569328a1906976d725fa72da02e98e5d73afb")
        .tree
    )

    with open(f"sections/appendices/{type_}_code.tex", "w", encoding="utf-8") as f:
        f.write(HEADER)

        for item in tree.traverse():
            if (
                type(item) == git.objects.Blob
                and item.path.startswith(directory)
                and item.path.endswith(".py")
            ):
                with io.BytesIO(item.data_stream.read()) as blob:
                    content = blob.read().decode("utf-8")
            else:
                continue

            stripped_name = item.path[len(f"{directory}/") :]
            f.write(
                r"\subsection{\texttt{" + stripped_name.replace("_", r"\_") + "}"
                r"\label{appendix:" + type_ + "-code:" + stripped_name + "}}\n"
            )
            f.write("\\begin{minted}{python}\n")
            f.write(content)
            f.write("\\end{minted}\n\n")

        f.write(FOOTER)


def main() -> None:
    """Generate the appendices."""
    os.makedirs("sections/appendices", exist_ok=True)
    generate_files("src/lintrans", "project")
    generate_files("tests", "testing")


if __name__ == "__main__":
    main()
