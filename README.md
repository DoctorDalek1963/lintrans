# lintrans

[![Documentation Status](https://readthedocs.org/projects/lintrans/badge/?version=latest)](https://lintrans.readthedocs.io/en/latest/)
![Tests](https://github.com/DoctorDalek1963/lintrans/actions/workflows/tests.yaml/badge.svg)
![Linting](https://github.com/DoctorDalek1963/lintrans/actions/workflows/linting.yaml/badge.svg)
![Type Checks](https://github.com/DoctorDalek1963/lintrans/actions/workflows/type-checks.yaml/badge.svg)
![Docstrings](https://github.com/DoctorDalek1963/lintrans/actions/workflows/docstrings.yaml/badge.svg)

![GPLv3 License](https://img.shields.io/github/license/DoctorDalek1963/lintrans?style=flat-square)
![Latest commit](https://img.shields.io/github/last-commit/DoctorDalek1963/lintrans?style=flat-square)
![Code size](https://img.shields.io/github/languages/code-size/DoctorDalek1963/lintrans?style=flat-square)
![Repo size](https://img.shields.io/github/repo-size/DoctorDalek1963/lintrans?style=flat-square)

---

This is the `lintrans` project. It is a Python package with a GUI. This project aims to provide an
easy way to visualize matrices as linear transformations. The user can define 2x2 matrices and
visualize them in 2D space. The user can also visualize compositions of defined matrices - addition
and multiplication - as well as inverses and transpositions.

This program is aimed at teachers teaching linear transformations, as well as students learning it
for the first time. The 3blue1brown series [Essence of Linear
Algebra](https://www.youtube.com/watch?v=fNk_zzaMoSs&list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab) is a
fantastic learning resource for this topic and I aim to provide an interactive supplement to that
series.

The Python source code can be found in `src/lintrans/` and the full documentation can be found on
[readthedocs.io](https://lintrans.readthedocs.io/en/stable/). I highly recommend reading the full
[tutorial](https://lintrans.readthedocs.io/en/stable/tutorial/).

This project is also my A Level Computer Science NEA (Non-Exam Assessment), which means I need to
provide a write-up of the development process. This write-up is written in LaTeX and can be found
in the [`write-up`](https://github.com/DoctorDalek1963/lintrans/tree/write-up) branch. The compiled
PDF can also be downloaded from [my GitHub pages site](https://doctordalek1963.github.io/lintrans).

---

## Usage

I recommend downloading a pre-built executable file from the [releases
page](https://github.com/DoctorDalek1963/lintrans/releases/latest).

You can also run the package directly by installing it in a virtual environment with `pip install
-e .` and then running `python -m lintrans`.

Compiling the package from source is also an option. Instructions are available
[here](https://lintrans.readthedocs.io/en/stable/compilation/).

---

## Info

This project is licensed under GNU GPL v3 and is copyright D. Dyson, 2021. That means that anyone
can use the project and view or edit the source code for free, but I provide no warranty and take
no liability. It also means that if you make any modifications to the source code, then it must
remain open source and licensed under GPL (v3 or later). It also means that no-one can close off
the source code or charge money for this program. It is provided for free and must always remain
free (as in freedom *and* price).

If you want to report a bug or suggest an improvement, please file an
[issue](https://github.com/DoctorDalek1963/lintrans/issues/new/choose) on GitHub or use the Google
Forms for anonymous [bug reports](https://forms.gle/Q82cLTtgPLcV4xQD6) and [feature
suggestions](https://forms.gle/mVWbHiMBw9Zq5Ze37).

Open source contributions are sadly not open at this time, because this is a school project, which
means I need to do it on my own. If you want to contribute to this project and make it better in
the future, just email me and I'll notify you when I can open the project to other contributors.
