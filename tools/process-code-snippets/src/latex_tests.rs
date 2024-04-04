use crate::{get_repo, snippet::Comment};
use pretty_assertions::assert_eq;

#[test]
fn get_latex_test() {
    let repo = get_repo();

    const LATEX_1: &str = r#"{
\renewcommand\theFancyVerbLine{ \ttfamily
	\textcolor[rgb]{0.5,0.5,1}{
		\footnotesize
		\oldstylenums{
			\ifnum\value{FancyVerbLine}=-3 \else
			\ifnum\value{FancyVerbLine}=-2 \else
			\ifnum\value{FancyVerbLine}=-1\setcounter{FancyVerbLine}{117}\else
			\ifnum\value{FancyVerbLine}=119\setcounter{FancyVerbLine}{149}... \else
			\ifnum\value{FancyVerbLine}=151\setcounter{FancyVerbLine}{202}... \else
				\arabic{FancyVerbLine}
			\fi\fi\fi\fi\fi
		}
	}
}
\begin{minted}[firstnumber=-3]{python}
# cf05e09e5ebb6ea7a96db8660d0d8de6b946490a
# src/lintrans/gui/plots/classes.py

class VectorGridPlot(BackgroundPlot):

    def draw_parallel_lines(self, painter: QPainter, vector: tuple[float, float], point: tuple[float, float]) -> None:

        else:  # If the line is not horizontal or vertical, then we can use y = mx + c
            m = vector_y / vector_x
            c = point_y - m * point_x

            # For c = 0
            painter.drawLine(
                *self.trans_coords(
                    -1 * max_x,
                    m * -1 * max_x
                ),
                *self.trans_coords(
                    max_x,
                    m * max_x
                )
            )

            # We keep looping and increasing the multiple of c until we stop drawing lines on the canvas
            multiple_of_c = 1
            while self.draw_pair_of_oblique_lines(painter, m, multiple_of_c * c):
                multiple_of_c += 1
\end{minted}
}"#;
    assert_eq!(
        Comment::from_latex_comment(concat!(
            "%: cf05e09e5ebb6ea7a96db8660d0d8de6b946490a\n",
            "%: src/lintrans/gui/plots/classes.py:203-222"
        ))
        .unwrap()
        .get_text(&repo)
        .unwrap()
        .get_latex(),
        LATEX_1,
        "Testing simple LaTeX generation"
    );

    const LATEX_2: &str = r#"{
\renewcommand\theFancyVerbLine{ \ttfamily
	\textcolor[rgb]{0.5,0.5,1}{
		\footnotesize
		\oldstylenums{
			\ifnum\value{FancyVerbLine}=-3 \else
			\ifnum\value{FancyVerbLine}=-2 \else
			\ifnum\value{FancyVerbLine}=-1\setcounter{FancyVerbLine}{6}\else
				\arabic{FancyVerbLine}
			\fi\fi\fi
		}
	}
}
\begin{minted}[firstnumber=-3]{python}
# 31220464635f6f889195d3dd5a1c38dd4cd13d3e
# src/lintrans/__init__.py

"""This is the top-level ``lintrans`` package, which contains all the subpackages of the project."""

from . import crash_reporting, global_settings, gui, matrices, typing_, updating

__version__ = '0.3.1-alpha'

__all__ = ['crash_reporting', 'global_settings', 'gui', 'matrices', 'typing_', 'updating', '__version__']
\end{minted}
}"#;
    assert_eq!(
        Comment::from_latex_comment(concat!(
            "%: 31220464635f6f889195d3dd5a1c38dd4cd13d3e\n",
            "%: src/lintrans/__init__.py"
        ))
        .unwrap()
        .get_text(&repo)
        .unwrap()
        .get_latex(),
        LATEX_2,
        "Testing removal of copyright comment"
    );

    const LATEX_3: &str = r#"{
\renewcommand\theFancyVerbLine{ \ttfamily
	\textcolor[rgb]{0.5,0.5,1}{
		\footnotesize
		\oldstylenums{
			\ifnum\value{FancyVerbLine}=-3 \else
			\ifnum\value{FancyVerbLine}=-2 \else
			\ifnum\value{FancyVerbLine}=-1\setcounter{FancyVerbLine}{0}\else
				\arabic{FancyVerbLine}
			\fi\fi\fi
		}
	}
}
\begin{minted}[firstnumber=-3]{python}
# 31220464635f6f889195d3dd5a1c38dd4cd13d3e
# src/lintrans/__init__.py

# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>

"""This is the top-level ``lintrans`` package, which contains all the subpackages of the project."""

from . import crash_reporting, global_settings, gui, matrices, typing_, updating

__version__ = '0.3.1-alpha'

__all__ = ['crash_reporting', 'global_settings', 'gui', 'matrices', 'typing_', 'updating', '__version__']
\end{minted}
}"#;
    assert_eq!(
        Comment::from_latex_comment(concat!(
            "%: 31220464635f6f889195d3dd5a1c38dd4cd13d3e\n",
            "%: src/lintrans/__init__.py keep_copyright_comment"
        ))
        .unwrap()
        .get_text(&repo)
        .unwrap()
        .get_latex(),
        LATEX_3,
        "Testing keeping of copyright comment"
    );

    const LATEX_4: &str = r#"{
\renewcommand\theFancyVerbLine{ \ttfamily
	\textcolor[rgb]{0.5,0.5,1}{
		\footnotesize
		\oldstylenums{
			\ifnum\value{FancyVerbLine}=-3 \else
			\ifnum\value{FancyVerbLine}=-2 \else
			\ifnum\value{FancyVerbLine}=-1\setcounter{FancyVerbLine}{139}\else
			\ifnum\value{FancyVerbLine}=141\setcounter{FancyVerbLine}{173}... \else
			\ifnum\value{FancyVerbLine}=175\setcounter{FancyVerbLine}{187}... \else
			\ifnum\value{FancyVerbLine}=189\setcounter{FancyVerbLine}{195}... \else
				\arabic{FancyVerbLine}
			\fi\fi\fi\fi\fi\fi
		}
	}
}
\begin{minted}[firstnumber=-3]{python}
# 40bee6461d477a5c767ed132359cd511c0051e3b
# src/lintrans/gui/plots/classes.py

class VectorGridPlot(BackgroundPlot):

    def draw_parallel_lines(self, painter: QPainter, vector: tuple[float, float], point: tuple[float, float]) -> None:

        if abs(vector_x * point_y - vector_y * point_x) < 1e-12:

            # If the matrix is rank 1, then we can draw the column space line
            if rank == 1:
                if abs(vector_x) < 1e-12:
                    painter.drawLine(self.width() // 2, 0, self.width() // 2, self.height())
                elif abs(vector_y) < 1e-12:
                    painter.drawLine(0, self.height() // 2, self.width(), self.height() // 2)
                else:
                    self.draw_oblique_line(painter, vector_y / vector_x, 0)

            # If the rank is 0, then we don't draw any lines
            else:
                return
\end{minted}
}"#;
    assert_eq!(
        Comment::from_latex_comment(concat!(
            "%: 40bee6461d477a5c767ed132359cd511c0051e3b\n",
            "%: src/lintrans/gui/plots/classes.py:196-207"
        ))
        .unwrap()
        .get_text(&repo)
        .unwrap()
        .get_latex(),
        LATEX_4,
        "Testing for linear scopes, so that no greater indents appear before the first indent"
    );

    const LATEX_5: &str = r#"{
\renewcommand\theFancyVerbLine{ \ttfamily
	\textcolor[rgb]{0.5,0.5,1}{
		\footnotesize
		\oldstylenums{
			\ifnum\value{FancyVerbLine}=-3 \else
			\ifnum\value{FancyVerbLine}=-2 \else
			\ifnum\value{FancyVerbLine}=-1\setcounter{FancyVerbLine}{332}\else
				\arabic{FancyVerbLine}
			\fi\fi\fi
		}
	}
}
\begin{minted}[firstnumber=-3]{python}
# 3c490c48a0f4017ab8ee9cf471a65c251817b00e
# src/lintrans/gui/main_window.py

            elif (abs(matrix_start - matrix_target) < 1e-12).all():
\end{minted}
}"#;
    assert_eq!(
        Comment::from_latex_comment(concat!(
            "%: 3c490c48a0f4017ab8ee9cf471a65c251817b00e\n",
            "%: src/lintrans/gui/main_window.py:333 noscopes"
        ))
        .unwrap()
        .get_text(&repo)
        .unwrap()
        .get_latex(),
        LATEX_5,
        "Testing noscopes option"
    );

    const LATEX_6: &str = r#"{
\renewcommand\theFancyVerbLine{ \ttfamily
	\textcolor[rgb]{0.5,0.5,1}{
		\footnotesize
		\oldstylenums{
			\ifnum\value{FancyVerbLine}=-3 \else
			\ifnum\value{FancyVerbLine}=-2 \else
			\ifnum\value{FancyVerbLine}=-1\setcounter{FancyVerbLine}{26}\else
			\ifnum\value{FancyVerbLine}=28\setcounter{FancyVerbLine}{433}... \else
			\ifnum\value{FancyVerbLine}=442\setcounter{FancyVerbLine}{448}... \else
				\arabic{FancyVerbLine}
			\fi\fi\fi\fi\fi
		}
	}
}
\begin{minted}[firstnumber=-3]{python}
# ba88521abd4e46048575a30330db4ed13821ecb0
# src/lintrans/gui/main_window.py

class LintransMainWindow(QMainWindow):

    def assign_matrix_wrapper(self, matrix_wrapper: MatrixWrapper) -> None:
        """Assign a new value to ``self.matrix_wrapper`` and give the expression box focus.

        :param matrix_wrapper: The new value of the matrix wrapper to assign
        :type matrix_wrapper: MatrixWrapper
        """
        self.matrix_wrapper = matrix_wrapper
        self.lineedit_expression_box.setFocus()

    def assign_display_settings(self, display_settings: DisplaySettings) -> None:
        """Assign a new value to ``self.plot.display_settings`` and give the expression box focus."""
        self.plot.display_settings = display_settings
        self.plot.update()
        self.lineedit_expression_box.setFocus()
\end{minted}
}"#;
    assert_eq!(
        Comment::from_latex_comment(concat!(
            "%: ba88521abd4e46048575a30330db4ed13821ecb0\n",
            "%: src/lintrans/gui/main_window.py:434-441,449-453"
        ))
        .unwrap()
        .get_text(&repo)
        .unwrap()
        .get_latex(),
        LATEX_6,
        "Testing multiple snippet bodies"
    );

    const LATEX_7: &str = r#"{
\renewcommand\theFancyVerbLine{ \ttfamily
	\textcolor[rgb]{0.5,0.5,1}{
		\footnotesize
		\oldstylenums{
			\ifnum\value{FancyVerbLine}=-3 \else
			\ifnum\value{FancyVerbLine}=-2 \else
			\ifnum\value{FancyVerbLine}=-1\setcounter{FancyVerbLine}{26}\else
			\ifnum\value{FancyVerbLine}=28\setcounter{FancyVerbLine}{433}... \else
			\ifnum\value{FancyVerbLine}=442\setcounter{FancyVerbLine}{445}... \else
			\ifnum\value{FancyVerbLine}=447\setcounter{FancyVerbLine}{448}... \else
				\arabic{FancyVerbLine}
			\fi\fi\fi\fi\fi\fi
		}
	}
}
\begin{minted}[firstnumber=-3]{python}
# ba88521abd4e46048575a30330db4ed13821ecb0
# src/lintrans/gui/main_window.py

class LintransMainWindow(QMainWindow):

    def assign_matrix_wrapper(self, matrix_wrapper: MatrixWrapper) -> None:
        """Assign a new value to ``self.matrix_wrapper`` and give the expression box focus.

        :param matrix_wrapper: The new value of the matrix wrapper to assign
        :type matrix_wrapper: MatrixWrapper
        """
        self.matrix_wrapper = matrix_wrapper
        self.lineedit_expression_box.setFocus()

        dialog.open()

    def assign_display_settings(self, display_settings: DisplaySettings) -> None:
        """Assign a new value to ``self.plot.display_settings`` and give the expression box focus."""
        self.plot.display_settings = display_settings
        self.plot.update()
        self.lineedit_expression_box.setFocus()
\end{minted}
}"#;
    assert_eq!(
        Comment::from_latex_comment(concat!(
            "%: ba88521abd4e46048575a30330db4ed13821ecb0\n",
            "%: src/lintrans/gui/main_window.py:434-441,446,449-453"
        ))
        .unwrap()
        .get_text(&repo)
        .unwrap()
        .get_latex(),
        LATEX_7,
        "Testing multiple snippet bodies with single line body in the middle"
    );

    const LATEX_8: &str = r#"{
\renewcommand\theFancyVerbLine{ \ttfamily
	\textcolor[rgb]{0.5,0.5,1}{
		\footnotesize
		\oldstylenums{
			\ifnum\value{FancyVerbLine}=-3 \else
			\ifnum\value{FancyVerbLine}=-2 \else
			\ifnum\value{FancyVerbLine}=-1\setcounter{FancyVerbLine}{62}\else
			\ifnum\value{FancyVerbLine}=64\setcounter{FancyVerbLine}{65}... \else
			\ifnum\value{FancyVerbLine}=67\setcounter{FancyVerbLine}{106}... \else
			\ifnum\value{FancyVerbLine}=108\setcounter{FancyVerbLine}{172}... \else
				\arabic{FancyVerbLine}
			\fi\fi\fi\fi\fi\fi
		}
	}
}
\begin{minted}[firstnumber=-3]{python}
# 517773e1ace0dc4485c425134cd36ba482ba65df
# src/lintrans/gui/dialogs/settings.py

class DisplaySettingsDialog(SettingsDialog):

    def __init__(self, display_settings: DisplaySettings, *args, **kwargs):

        self.checkbox_draw_determinant_parallelogram.clicked.connect(self.update_gui)

    def update_gui(self) -> None:
        """Update the GUI according to other widgets in the GUI.

        For example, this method updates which checkboxes are enabled based on the values of other checkboxes.
        """
        self.checkbox_draw_determinant_text.setEnabled(self.checkbox_draw_determinant_parallelogram.isChecked())
\end{minted}
}"#;
    assert_eq!(
        Comment::from_latex_comment(concat!(
            "%: 517773e1ace0dc4485c425134cd36ba482ba65df\n",
            "%: src/lintrans/gui/dialogs/settings.py:107,173-178"
        ))
        .unwrap()
        .get_text(&repo)
        .unwrap()
        .get_latex(),
        LATEX_8,
        "Testing multiple snippet bodies with scopes"
    );

    const LATEX_9: &str = r#"{
\renewcommand\theFancyVerbLine{ \ttfamily
	\textcolor[rgb]{0.5,0.5,1}{
		\footnotesize
		\oldstylenums{
			\ifnum\value{FancyVerbLine}=-3 \else
			\ifnum\value{FancyVerbLine}=-2 \else
			\ifnum\value{FancyVerbLine}=-1\setcounter{FancyVerbLine}{0}\else
				\arabic{FancyVerbLine}
			\fi\fi\fi
		}
	}
}
\begin{minted}[firstnumber=-3]{yaml}
# 39a3727fca69ea65571a15c55741578abce1e763
# .github/workflows/compile-docs.yaml

name: Compile docs for gh-pages

on:
  push:
    branches: [ main ]

jobs:
  compile-docs:
    runs-on: ubuntu-latest

    concurrency:
      group: ${{ github.workflow }}-${{ github.ref }}

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python 3.10
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install --upgrade pip
        pip install -r requirements.txt -r docs/docs_requirements.txt
        pip install -e .
        pip install pylint
        sudo apt-get install -y graphviz

    - name: Create pylint import graphs
      run: |
        shopt -s globstar
        pylint --rcfile=/dev/null --exit-zero --reports=y --disable=all --enable=imports,RP0402 --int-import-graph=docs/source/int-imports.png src/lintrans/**/*.py

    - name: Build docs
      run: cd docs/ && make html && cd ..

    - name: Deploy
      uses: peaceiris/actions-gh-pages@v3.8.0
      if: ${{ github.ref == 'refs/heads/main' }}
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./docs/build/html/
        keep_files: true
        destination_dir: docs
        user_name: 'github-actions[bot]'
        user_email: 'github-actions[bot]@users.noreply.github.com'
        commit_message: 'compile docs:'
\end{minted}
}"#;

    assert_eq!(
        Comment::from_latex_comment(concat!(
            "%: 39a3727fca69ea65571a15c55741578abce1e763\n",
            "%: .github/workflows/compile-docs.yaml language=yaml"
        ))
        .unwrap()
        .get_text(&repo)
        .unwrap()
        .get_latex(),
        LATEX_9,
        "Testing a YAML file"
    );

    const LATEX_10: &str = r#"{
\renewcommand\theFancyVerbLine{ \ttfamily
	\textcolor[rgb]{0.5,0.5,1}{
		\footnotesize
		\oldstylenums{
			\ifnum\value{FancyVerbLine}=-3 \else
			\ifnum\value{FancyVerbLine}=-2 \else
			\ifnum\value{FancyVerbLine}=-1\setcounter{FancyVerbLine}{0}\else
				\arabic{FancyVerbLine}
			\fi\fi\fi
		}
	}
}
\begin{minted}[firstnumber=-3]{lexers.py:SphObjInvTextLexer -x}
# 5455265a51666e29ab976152c1a758a422e1004a
# docs/pyqt5-objects.txt

# This format is:
# <reference name> <domain>:<role> <priority> <URI> <display name>
# Sphinx handles the prefix for the URI
# If the display name is '-', then it's the same as the reference name

# === Classes

QApplication py:class 1 qapplication.html -
QDialog      py:class 1 qdialog.html      -
QKeyEvent    py:class 1 qkeyevent.html    -
QPainter     py:class 1 qpainter.html     -
QPaintEvent  py:class 1 qpaintevent.html  -
QWheelEvent  py:class 1 qwheelevent.html  -
QWidget      py:class 1 qwidget.html      -

# === Methods

# This signature doesn't include the `QPainter.` at the start just to save on line length
drawLine:iiii py:method 1 qpainter.html#drawLine-2 drawLine()

# === Signals

QComboBox.activated py:method 1 qcombobox.html#activated -
QDialog.accepted    py:method 1 qdialog.html#accepted    -

# These are in full form so that autodoc can reference base classes and param types

PyQt5.QtGui.QKeyEvent   py:class 1 qkeyevent.html   -
PyQt5.QtGui.QPainter    py:class 1 qpainter.html    -
PyQt5.QtGui.QPaintEvent py:class 1 qpaintevent.html -
PyQt5.QtGui.QWheelEvent py:class 1 qwheelevent.html -
PyQt5.QtWidgets.QDialog py:class 1 qdialog.html     -
PyQt5.QtWidgets.QWidget py:class 1 qwidget.html     -
\end{minted}
}"#;

    assert_eq!(
        Comment::from_latex_comment(concat!(
            "%: 5455265a51666e29ab976152c1a758a422e1004a\n",
            "%: docs/pyqt5-objects.txt language='lexers.py:SphObjInvTextLexer -x'"
        ))
        .unwrap()
        .get_text(&repo)
        .unwrap()
        .get_latex(),
        LATEX_10,
        "Testing a custom lexer (with single quotes)"
    );
    assert_eq!(
        Comment::from_latex_comment(concat!(
            "%: 5455265a51666e29ab976152c1a758a422e1004a\n",
            "%: docs/pyqt5-objects.txt language=\"lexers.py:SphObjInvTextLexer -x\""
        ))
        .unwrap()
        .get_text(&repo)
        .unwrap()
        .get_latex(),
        LATEX_10,
        "Testing a custom lexer (with double quotes)"
    );

    const LATEX_11: &str = r#"{
\renewcommand\theFancyVerbLine{ \ttfamily
	\textcolor[rgb]{0.5,0.5,1}{
		\footnotesize
		\oldstylenums{
			\ifnum\value{FancyVerbLine}=-3 \else
			\ifnum\value{FancyVerbLine}=-2 \else
			\ifnum\value{FancyVerbLine}=-1\setcounter{FancyVerbLine}{6}\else
				\arabic{FancyVerbLine}
			\fi\fi\fi
		}
	}
}
\begin{minted}[firstnumber=-3]{python}
# 7423fff72f09b5f5a3253c734d42c4e7c3182efe
# src/lintrans/gui/dialogs/misc.py

"""This module provides miscellaneous dialog classes like :class:`AboutDialog`."""

from __future__ import annotations

import platform

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout

import lintrans


class AboutDialog(QDialog):
    """A simple dialog class to display information about the app to the user.

    It only has an :meth:`__init__` method because it only has label widgets, so no other methods are necessary here.
    """

    def __init__(self, *args, **kwargs):
        """Create an :class:`AboutDialog` object with all the label widgets."""
        super().__init__(*args, **kwargs)

        self.setWindowTitle('About lintrans')

        # === Create the widgets

        label_title = QtWidgets.QLabel(self)
        label_title.setText(f'lintrans (version {lintrans.__version__})')
        label_title.setAlignment(Qt.AlignCenter)

        font_title = label_title.font()
        font_title.setPointSize(font_title.pointSize() * 2)
        label_title.setFont(font_title)

        label_version_info = QtWidgets.QLabel(self)
        label_version_info.setText(
            f'With Python version {platform.python_version()}\n'
            f'Running on {platform.platform()}'
        )
        label_version_info.setAlignment(Qt.AlignCenter)

        label_info = QtWidgets.QLabel(self)
        label_info.setText(
            'lintrans is a program designed to help visualise<br>'
            '2D linear transformations represented with matrices.<br><br>'
            "It's designed for teachers and students and any feedback<br>"
            'is greatly appreciated at <a href="https://github.com/DoctorDalek1963/lintrans" '
            'style="color: black;">my GitHub page</a><br>or via email '
            '(<a href="mailto:dyson.dyson@icloud.com" style="color: black;">dyson.dyson@icloud.com</a>).'
        )
        label_info.setAlignment(Qt.AlignCenter)
        label_info.setTextFormat(Qt.RichText)
        label_info.setOpenExternalLinks(True)

        label_copyright = QtWidgets.QLabel(self)
        label_copyright.setText(
            'This program is free software.<br>Copyright 2021-2022 D. Dyson (DoctorDalek1963).<br>'
            'This program is licensed under GPLv3, which can be found '
            '<a href="https://www.gnu.org/licenses/gpl-3.0.html" style="color: black;">here</a>.'
        )
        label_copyright.setAlignment(Qt.AlignCenter)
        label_copyright.setTextFormat(Qt.RichText)
        label_copyright.setOpenExternalLinks(True)

        # === Arrange the widgets

        self.setContentsMargins(10, 10, 10, 10)

        vlay = QVBoxLayout()
        vlay.setSpacing(20)
        vlay.addWidget(label_title)
        vlay.addWidget(label_version_info)
        vlay.addWidget(label_info)
        vlay.addWidget(label_copyright)

        self.setLayout(vlay)

        self.setFixedSize(self.baseSize())
\end{minted}
}"#;

    assert_eq!(
        Comment::from_latex_comment(concat!(
            "%: 7423fff72f09b5f5a3253c734d42c4e7c3182efe\n",
            "%: src/lintrans/gui/dialogs/misc.py"
        ))
        .unwrap()
        .get_text(&repo)
        .unwrap()
        .get_latex(),
        LATEX_11,
        "Testing automatic removal of the copyright comment when it's only 2022"
    );

    const LATEX_12: &str = r#"{
\renewcommand\theFancyVerbLine{ \ttfamily
	\textcolor[rgb]{0.5,0.5,1}{
		\footnotesize
		\oldstylenums{
			\ifnum\value{FancyVerbLine}=-3 \else
			\ifnum\value{FancyVerbLine}=-2 \else
			\ifnum\value{FancyVerbLine}=-1\setcounter{FancyVerbLine}{8}\else
				\arabic{FancyVerbLine}
			\fi\fi\fi
		}
	}
}
\begin{minted}[firstnumber=-3]{python}
# 99a88575f9beb8fed2dcc41dacbb020b31bc8176
# generate_release_notes.py

"""A very simple script to generate release notes."""

import re
import sys

TEXT = '''DESCRIPTION

---

The Linux binary should work fine, but if you use the Windows `.exe` file, you will get a warning that the program may be unsafe. This is expected and you can just ignore it. There's no binary for macOS due to Apple code signing issues.

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
\end{minted}
}"#;

    assert_eq!(
        Comment::from_latex_comment(concat!(
            "%: 99a88575f9beb8fed2dcc41dacbb020b31bc8176\n",
            "%: generate_release_notes.py"
        ))
        .unwrap()
        .get_text(&repo)
        .unwrap()
        .get_latex(),
        LATEX_12,
        "Testing automatic removal of the copyright comment when there's a shebang first"
    );

    // There's an intentional trailing space after "Added". It's fine
    const LATEX_13: &str = r#"{
\renewcommand\theFancyVerbLine{ \ttfamily
	\textcolor[rgb]{0.5,0.5,1}{
		\footnotesize
		\oldstylenums{
			\ifnum\value{FancyVerbLine}=-3 \else
			\ifnum\value{FancyVerbLine}=-2 \else
			\ifnum\value{FancyVerbLine}=-1\setcounter{FancyVerbLine}{0}\else
				\arabic{FancyVerbLine}
			\fi\fi\fi
		}
	}
}
\begin{minted}[firstnumber=-3]{lexers.py:MarkdownWithCommentsLexer -x}
<!-- 47c68c7f4780d0e2c374cf12b9b54c031277af6d -->
<!-- CHANGELOG.md -->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added 

- Explicit `@pyqtSlot` decorators
- Link to Qt5 docs in project docs with intersphinx
- Copyright comment in tests and `setup.py`
- Create version file for Windows compilation
- Create full compile.py script
- Add `Info.plist` file for macOS compilation
- Support --help and --version flags in `__main__.py`
- Create about dialog in help menu
- Implement minimum grid spacing

### Fixed

- Fix problems with compile script
- Fix small bugs and docstrings

## [0.2.0] - 2022-03-11

There were alpha tags before this, but I wasn't properly adhering to semantic versioning, so I'll start the changelog here.

If I'd been using semantic versioning from the start, there would much more changelog here, but instead, I'll just summarise the features.

### Added

- Matrix context with the `MatrixWrapper` class
- Parsing and evaluating matrix expressions
- A simple GUI with a viewport to render linear transformations
- Simple dialogs to create matrices and assign them to names
- Ability to render and animate linear transformations parsed from defined matrices
- Ability to zoom in and out of the viewport
- Add dialog to change display settings

[Unreleased]: https://github.com/DoctorDalek1963/lintrans/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/DoctorDalek1963/lintrans/compare/13600cc6ff6299dc4a8101a367bc52fe08607554...v0.2.0
\end{minted}
}"#;

    assert_eq!(
        Comment::from_latex_comment(concat!(
            "%: 47c68c7f4780d0e2c374cf12b9b54c031277af6d\n",
            "%: CHANGELOG.md language=\"lexers.py:MarkdownWithCommentsLexer -x\"",
            " comment=\"<!-- {} -->\""
        ))
        .unwrap()
        .get_text(&repo)
        .unwrap()
        .get_latex(),
        LATEX_13,
        "Testing custom info comment syntax (double quotes)"
    );
    assert_eq!(
        Comment::from_latex_comment(concat!(
            "%: 47c68c7f4780d0e2c374cf12b9b54c031277af6d\n",
            "%: CHANGELOG.md language=\"lexers.py:MarkdownWithCommentsLexer -x\"",
            " comment='<!-- {} -->'"
        ))
        .unwrap()
        .get_text(&repo)
        .unwrap()
        .get_latex(),
        LATEX_13,
        "Testing custom info comment syntax (single quotes)"
    );

    assert_eq!(
        Comment::from_latex_comment(concat!(
            "%: 47c68c7f4780d0e2c374cf12b9b54c031277af6d\n",
            "%: CHANGELOG.md markdown!",
        ))
        .unwrap()
        .get_text(&repo)
        .unwrap()
        .get_latex(),
        LATEX_13,
        "Testing markdown! macro"
    );

    const LATEX_14: &str = r#"{
\renewcommand\theFancyVerbLine{ \ttfamily
	\textcolor[rgb]{0.5,0.5,1}{
		\footnotesize
		\oldstylenums{
			\ifnum\value{FancyVerbLine}=-3 \else
			\ifnum\value{FancyVerbLine}=-2 \else
			\ifnum\value{FancyVerbLine}=-1\setcounter{FancyVerbLine}{135}\else
			\ifnum\value{FancyVerbLine}=137\setcounter{FancyVerbLine}{219}... \else
			\ifnum\value{FancyVerbLine}=221\setcounter{FancyVerbLine}{230}... \else
				\arabic{FancyVerbLine}
			\fi\fi\fi\fi\fi
		}
	}
}
\begin{minted}[firstnumber=-3, highlightlines={232-233}]{python}
# 8d7143fc33ea7bd4199e0f01b6a5308dfcf03ff9
# src/lintrans/matrices/parse.py

class ExpressionParser:

    def _parse_matrix_part(self) -> bool:

        if self.char.isdigit() or self.char == '-':
            if self.current_token.multiplier != '' \
                    or (self.current_token.multiplier == '' and self.current_token.identifier != ''):
                return False

            self._parse_multiplier()
\end{minted}
}"#;

    assert_eq!(
        Comment::from_latex_comment(concat!(
            "%: 8d7143fc33ea7bd4199e0f01b6a5308dfcf03ff9\n",
            "%: src/lintrans/matrices/parse.py:231-236 highlight=232-233",
        ))
        .unwrap()
        .get_text(&repo)
        .unwrap()
        .get_latex(),
        LATEX_14,
        "Testing highlight lines"
    );
}
