//! This module contains code to deal with converting snippet text taken from commits into LaTeX code.

use git2::Oid;
use itertools::Itertools;
use std::path::Path;

/// The text and metadata of an actual snippet.
#[derive(Clone, Debug, PartialEq)]
pub struct Text<'s> {
    /// The commit hash.
    pub hash: Oid,

    /// The file path.
    pub filename: &'s Path,

    /// A vec of `(line_number, text)` of the higher scopes, determined by less indentation.
    ///
    /// Must be ordered by ascending line numbers.
    pub scopes: Vec<(u32, String)>,

    /// The bodies of the snippet; the actual code that we want to include, along with the start of
    /// end line of each body block.
    pub bodies: Vec<(String, u32, u32)>,
}

impl<'s> Text<'s> {
    /// Return the LaTeX code to embed the snippet as a `minted` environment with custom page numbers.
    #[allow(unstable_name_collisions)]
    pub fn get_latex(&self) -> String {
        // Each element is a tuple (a, b) that says "when we encounter line a, show '...' and skip to
        // line b". Line a is just after a line of interest, and line b is just before the next one.
        let line_num_pairs: Vec<(i32, i32)> = {
            let mut lines = vec![];
            let mut a = -1;
            let mut b;

            for (n, _) in &self.scopes {
                b = *n as i32 - 1;
                lines.push((a, b));
                a = *n as i32 + 1;
            }

            for (_, start, end) in &self.bodies {
                b = *start as i32 - 1;
                lines.push((a, b));
                a = *end as i32 + 1;
            }

            lines
        };

        // Redefine the line number macro to handle the snippet comments and scope lines
        let line_number_hack: String = {
            // The start of the line number hack redefines a macro to handle line numbers. The
            // `minted` environment will start counting at -3, so we want -3 and -2 to display no
            // line numbers, because those are the lines for the snippet comments
            let mut s = String::from(
                r"\renewcommand\theFancyVerbLine{ \ttfamily
	\textcolor[rgb]{0.5,0.5,1}{
		\footnotesize
		\oldstylenums{
			\ifnum\value{FancyVerbLine}=-3 \else
			\ifnum\value{FancyVerbLine}=-2 \else",
            );
            s.push('\n');

            // This is a special case of the line number hack that we do over the whole vector a
            // few lines down. We want to display nothing for this first blank line, rather than a
            // `...`, but we also need to set the counter for the first line of interest
            s.push_str("\t\t\t");
            s.push_str(&format!(
                r"\ifnum\value{{FancyVerbLine}}={}\setcounter{{FancyVerbLine}}{{{}}}\else",
                line_num_pairs.first().unwrap().0,
                line_num_pairs.first().unwrap().1,
            ));
            s.push('\n');

            // For each pair of numbers, we want to check and set the line number accordingly. When
            // the line number is `a` (meaning we've just done the previous line of interest), we
            // want to set it to `b` (meaning we set the counter to just before the next line of
            // interest) and then display a `...` here to represent some skipped lines. The counter
            // increments naturally to display the numbers of the lines we care about
            for (a, b) in line_num_pairs.iter().skip(1) {
                s.push_str("\t\t\t");
                s.push_str(&format!(
                    r"\ifnum\value{{FancyVerbLine}}={}\setcounter{{FancyVerbLine}}{{{}}}... \else",
                    a, b
                ));
                s.push('\n');
            }

            // We then close the line hack by stating that any line that we haven't explicitly
            // covered should display a normal number, and then we close all the if statements
            s.push_str("\t\t\t\t");
            s.push_str(
                r"\arabic{FancyVerbLine}
			\fi\fi",
            );

            for _ in line_num_pairs {
                s.push_str(r"\fi");
            }

            // Close the macro redefinition
            s.push('\n');
            s.push_str("\t\t}\n\t}\n}\n");

            s
        };

        let mut s = String::from("{\n");
        s.push_str(&line_number_hack);

        s.push_str(r"\begin{minted}[firstnumber=-3]{python}");
        s.push('\n');

        // Add the commit hash as a comment
        s.push_str("# ");
        s.push_str(&self.hash.to_string());
        s.push('\n');

        // Add the filename as a comment
        s.push_str("# ");
        s.push_str(
            self.filename
                .to_str()
                .expect("Filename should be UTF-8 encoded"),
        );
        s.push('\n');

        s.push('\n');

        // Add the scopes with newlines between them
        for (_, line) in &self.scopes {
            s.push_str(line);
            s.push_str("\n\n");
        }

        // Add the snippet body
        s.push_str(
            &self
                .bodies
                .iter()
                .map(|(s, _, _)| s)
                .cloned()
                .intersperse(String::from("\n\n"))
                .collect::<String>(),
        );
        s.push('\n');

        // Close everything
        s.push_str(r"\end{minted}");
        s.push('\n');
        s.push('}');

        s
    }
}

#[cfg(test)]
mod tests {
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
    }
}
