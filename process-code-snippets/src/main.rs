//! This simple binary crate will process code snippet comments in LaTeX source code to produce
//! `minted` environments with the snippet bodies.
//!
//! Code snippets are written as TeX comments with a : following the %.
//!
//! For example:
//!
//!   %: 29ec1fedbf307e3b7ca731c4a381535fec899b0b
//!   %: src/lintrans/matrices/wrapper.py:11-22
//!
//! Would reference lines 11-22 of the file src/lintrans/matrices/wrapper.py in commit
//! 29ec1fedbf307e3b7ca731c4a381535fec899b0b on the main branch of lintrans. Line numbers are
//! optional. If omitted, the whole file is included.

use color_eyre::eyre::Result;
use git2::{Oid, Repository};
use itertools::Itertools;
use lazy_static::lazy_static;
use regex::Regex;
use std::{env, fs, path::Path};

/// The copyright comment that appears at the top of newer files.
const COPYRIGHT_COMMENT: &str = r"# lintrans - The linear transformation visualizer
# Copyright (C) 2021-2022 D. Dyson (DoctorDalek1963)

# This program is licensed under GNU GPLv3, available here:
# <https://www.gnu.org/licenses/gpl-3.0.html>
";

lazy_static! {
    /// The regex for the snippet comments. The options after filename should be given in
    /// alphabetic order.
    static ref COMMENT_PATTERN: Regex = Regex::new(concat!(
        r"(?m)^%: (?P<hash>[0-9a-f]{40})\n",
        r"%: (?P<filename>[^\s:]+)(:(?P<linenums>\d+-\d+|\d+))?(?P<keep_copyright_comment> keep_copyright_comment)?(?P<noscopes> noscopes)?$"
    ))
    .unwrap();

    /// The regex for the linenumbers in the snippet comments.
    static ref LINENUMS_PATTERN: Regex = Regex::new(r"^(?P<first>\d+)(-(?P<last>\d+))?$").unwrap();
}

/// A config struct to use for snippets. Defines some options that can be used in snippets.
#[derive(Clone, Copy, Debug, PartialEq)]
struct SnippetConfig {
    // Whether to remove the copyright comment. Defaults to true.
    remove_copyright_comment: bool,

    /// Whether to show containing scopes for the snippet. Defaults to true.
    use_scopes: bool,
}

impl Default for SnippetConfig {
    fn default() -> Self {
        Self {
            remove_copyright_comment: true,
            use_scopes: true,
        }
    }
}

/// A reference to a code snippet, as used in comments.
#[derive(Clone, Debug, PartialEq)]
struct SnippetRef<'s> {
    /// The commit hash.
    hash: Oid,

    /// The file path.
    filename: &'s Path,

    /// The start and end lines of the snippet. If [`None`], then the whole file is implied.
    line_range: Option<(u32, u32)>,

    /// The config for this snippet.
    config: SnippetConfig,
}

impl<'s> SnippetRef<'s> {
    /// Create a snippet from a pair of snippet comments with the hash and file information.
    fn from_comment(comment: &'s str) -> Option<Self> {
        let c = COMMENT_PATTERN.captures(comment)?;

        // Parse the hash and filename
        let hash = Oid::from_str(c.name("hash")?.as_str()).ok()?;
        let filename = Path::new(c.name("filename")?.as_str());

        // Parse the line numbers. If we don't have line numbers here, then they are `None`. This
        // will be resolved by [`get_text`] when getting the text from the commit with the repo
        let line_range = c.name("linenums").map(|m| {
            let text = m.as_str();
            let c = LINENUMS_PATTERN
                .captures(text)
                .expect("If we can get here, then the LINENUMS_PATTERN should match the text");

            // The call to `map()` that this closure is in means that we have at least one line
            // number. If we've got both, use them. If we've only got one, then use that for both
            let first = c.name("first").unwrap().as_str().parse::<u32>().unwrap();
            let last = match c.name("last") {
                None => first,
                Some(num) => num.as_str().parse::<u32>().ok().unwrap(),
            };

            (first, last)
        });

        // Check the options and create a config struct for them.
        let config = SnippetConfig {
            remove_copyright_comment: c.name("keep_copyright_comment").is_none(),
            use_scopes: c.name("noscopes").is_none(),
        };

        Some(Self {
            hash,
            filename,
            line_range,
            config,
        })
    }

    /// Return the raw text of the snippet, removing the copyright comment if the whole file was included.
    ///
    /// The string returned does not include a trailing newline.
    #[allow(unstable_name_collisions)]
    fn get_text(&self, repo: &Repository) -> Result<SnippetText<'s>> {
        // Get the commit, find the file in the tree, and find the file as a blob
        let x = repo
            .find_commit(self.hash)?
            .tree()?
            .get_path(self.filename)?
            .to_object(repo)?
            .into_blob();

        // Read the file blob or return an Err
        let content = match x {
            Ok(ref blob) => std::str::from_utf8(blob.content())?,
            Err(_) => {
                return Err(color_eyre::eyre::Error::msg(
                    "Couldn't convert object to blob",
                ))
            }
        };

        // Get the line range or use 1 to the end of the file
        let (mut first, last) = self
            .line_range
            .unwrap_or_else(|| (1, content.lines().count() as u32));

        // If we've got a copyright comment, then remove it and update the line number accordingly
        if self.config.remove_copyright_comment
            && first == 1
            && content
                .lines()
                .take(6)
                .intersperse("\n")
                .collect::<String>()
                == COPYRIGHT_COMMENT
        {
            first = 7;
        }

        // We now calculate a vector that maps line numbers to line contents.
        // Each line is a line above the snippet which has less indentation, indicating that it is
        // an enclosing scope. This works because all the snippets are Python, which uses
        // meaningful whitespace for scoping
        let scopes: Vec<(u32, String)> = if self.config.use_scopes {
            // Get the indentation of the first line of the snippet. We'll use this as a baseline
            // for the enclosing scopes. They will need less indentation than this
            let first_line_indentation: usize = content
                .lines()
                .nth(first as usize - 1)
                .unwrap()
                .chars()
                .take_while(|&c| c == ' ')
                .count();

            content
                .lines()

                // Match line numbers to lines to propagate through to the end
                .enumerate()
                .map(|(n, s)| (n + 1, s.to_string()))

                // We only want to look at the lines before the snippet
                .take(first as usize - 1)

                // This little hack is inefficient but it reverses the lines so that we can work up
                // from the snippet
                .collect::<Vec<_>>()
                .iter()
                .rev()

                // We want to filter out any empty lines or lines with less indentation than the
                // start of the snippet, and also incorporate the indentation of other lines into
                // the tuple so that we can continue using it
                .filter_map(|(n, line)| {
                    let indentation = line.chars().take_while(|&c| c == ' ').count();

                    if line.is_empty() || indentation >= first_line_indentation || indentation % 4 != 0 {
                        None
                    } else {
                        Some((indentation, *n, line.clone()))
                    }
                })

                // Remove all duplicate indentations. This leaves the first occurence of each
                // indentation level
                .unique_by(|x| x.0)

                // Reverse the direction again, so that we're going from the top down
                .collect::<Vec<_>>()
                .iter()
                .cloned()
                .rev()

                // Remove any leading lines with non-zero indentation. This can occur in
                // module-level docstrings with indented blocks, and these lines come before any
                // classes or functions, so we have to remove these extraneous documentation lines
                .skip_while(|&(indent, _, _)| indent > 0)

                // Discard the indentation amount so that we have line number and string
                .map(|(_, n, s)| (n as u32, s))

                .collect()
        } else {
            // If we're using the `noscopes` option, then we obviously don't want any enclosing scopes
            vec![]
        };

        // The body is just the section of the content from the first line to the last line,
        // interspersed with newlines
        let body: String = content
            .lines()
            .skip((first - 1) as usize)
            .take(1 + (last - first) as usize)
            .intersperse("\n")
            .collect();

        Ok(SnippetText {
            hash: self.hash,
            filename: self.filename,
            scopes,
            body,
            line_range: (first, last),
        })
    }
}

/// The text and metadata of an actual snippet.
#[derive(Clone, Debug, PartialEq)]
struct SnippetText<'s> {
    /// The commit hash.
    hash: Oid,

    /// The file path.
    filename: &'s Path,

    /// A vec of `(line_number, text)` of the higher scopes, determined by less indentation.
    ///
    /// Must be ordered by ascending line numbers.
    scopes: Vec<(u32, String)>,

    /// The body of the snippet; the actual code that we want to include.
    body: String,

    /// The range of lines of the original file that this body comes from.
    line_range: (u32, u32),
}

impl<'s> SnippetText<'s> {
    /// Return the LaTeX code to embed the snippet as a `minted` environment with custom page numbers.
    fn get_latex(&self) -> String {
        let line_num_pairs: Vec<(i32, i32)> = {
            // This is a list of line numbers for each change in line numbers - all scope lines and
            // the first line of the snippet
            let mut line_nums: Vec<i32> = self.scopes.iter().map(|&(n, _)| n as i32).collect();
            line_nums.push(self.line_range.0 as i32);

            // Create a new vector which is the same as `line_nums`, but has a prepended `-2`
            let prepended: Vec<i32> = {
                let mut v = vec![-2];
                for n in &line_nums {
                    v.push(*n);
                }
                v
            };

            // Zip the `prepended` vector with the `line_nums` vector, accounting for off-by-one errors.
            // This creates a vector of tuples `(a, b)` where `a` is the number after the previous
            // line that we cared about, and `b` is the number before the line number we care about
            prepended
                .iter()
                .zip(line_nums)
                .map(|(f, l)| (f + 1, l - 1))
                .collect()
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
        s.push_str(&self.body);
        s.push('\n');

        // Close everything
        s.push_str(r"\end{minted}");
        s.push('\n');
        s.push('}');

        s
    }
}

/// Process every snippet in the given file and write out a processed version under a new name with
/// `processed_` prepended to the basename of the file.
fn process_all_snippets_in_file(filename: &str, repo: &Repository) -> Result<()> {
    let file_string = fs::read_to_string(filename)?;

    // Find all the snippet comments in the file and process each of them, to get an iterator of
    // tuples like `(comment, replacement_latex)`
    let comments_and_latex = COMMENT_PATTERN.find_iter(&file_string).map(|m| {
        (
            m.as_str(),
            SnippetRef::from_comment(m.as_str())
                .unwrap()
                .get_text(repo)
                .unwrap()
                .get_latex(),
        )
    });

    // Copy the file contents and replace each snippet comment with its LaTeX replacement
    let mut body = file_string.clone();
    for (comment, latex) in comments_and_latex {
        body = body.replace(comment, &latex);
    }

    // Create a new filename by prepending `processed_` to the basename
    let new_filename = {
        let p = Path::new(filename);
        let parent = p.parent().unwrap();
        let fname = String::from("processed_") + p.strip_prefix(parent)?.to_str().unwrap();
        parent.join(fname)
    };

    fs::write(new_filename, body)?;

    Ok(())
}

/// Process every file given as a command line argument.
fn main() -> Result<()> {
    color_eyre::install()?;

    let repo = Repository::open(Path::new(env!("LINTRANS_DIR")))?;

    if env::args().count() == 1 {
        return Err(color_eyre::eyre::Error::msg(
            "Please provide file names as command line arguments",
        ));
    }

    for filename in env::args().skip(1) {
        process_all_snippets_in_file(&filename, &repo)?;
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn get_repo() -> Repository {
        Repository::open(Path::new("../../lintrans/")).unwrap()
    }

    mod snippet_ref {
        use super::*;
        use pretty_assertions::assert_eq;

        #[test]
        fn from_comment_test() {
            let comment =
                "%: 29ec1fedbf307e3b7ca731c4a381535fec899b0b\n%: src/lintrans/matrices/wrapper.py";
            let snip = SnippetRef {
                hash: Oid::from_str("29ec1fedbf307e3b7ca731c4a381535fec899b0b").unwrap(),
                filename: Path::new("src/lintrans/matrices/wrapper.py"),
                line_range: None,
                config: SnippetConfig::default(),
            };
            assert_eq!(SnippetRef::from_comment(comment).unwrap(), snip);

            let comment =
            "%: 29ec1fedbf307e3b7ca731c4a381535fec899b0b\n%: src/lintrans/matrices/wrapper.py:11-22";
            let snip = SnippetRef {
                hash: Oid::from_str("29ec1fedbf307e3b7ca731c4a381535fec899b0b").unwrap(),
                filename: Path::new("src/lintrans/matrices/wrapper.py"),
                line_range: Some((11, 22)),
                config: SnippetConfig::default(),
            };
            assert_eq!(SnippetRef::from_comment(comment).unwrap(), snip);

            let comment =
            "%: 29ec1fedbf307e3b7ca731c4a381535fec899b0b\n%: src/lintrans/matrices/wrapper.py:11";
            let snip = SnippetRef {
                hash: Oid::from_str("29ec1fedbf307e3b7ca731c4a381535fec899b0b").unwrap(),
                filename: Path::new("src/lintrans/matrices/wrapper.py"),
                line_range: Some((11, 11)),
                config: SnippetConfig::default(),
            };
            assert_eq!(SnippetRef::from_comment(comment).unwrap(), snip);
        }

        #[test]
        fn get_text_test() {
            const FILE: &str = r#""""A module containing a simple MatrixWrapper class to wrap matrices and context."""

import numpy as np

from lintrans.typing import MatrixType


class MatrixWrapper:
    """A simple wrapper class to hold all possible matrices and allow access to them."""

    def __init__(self):
        """Initialise a MatrixWrapper object with a matrices dict."""
        self._matrices: dict[str, MatrixType | None] = {
            'A': None, 'B': None, 'C': None, 'D': None,
            'E': None, 'F': None, 'G': None, 'H': None,
            'I': np.eye(2),  # I is always defined as the identity matrix
            'J': None, 'K': None, 'L': None, 'M': None,
            'N': None, 'O': None, 'P': None, 'Q': None,
            'R': None, 'S': None, 'T': None, 'U': None,
            'V': None, 'W': None, 'X': None, 'Y': None,
            'Z': None
        }

    def __getitem__(self, name: str) -> MatrixType | None:
        """Get the matrix with `name` from the dictionary.

        Raises:
            KeyError:
                If there is no matrix with the given name
        """
        return self._matrices[name]

    def __setitem__(self, name: str, new_matrix: MatrixType) -> None:
        """Set the value of matrix `name` with the new_matrix.

        Raises:
            ValueError:
                If `name` isn't a valid matrix name
        """
        name = name.upper()

        if name == 'I' or name not in self._matrices:
            raise NameError('Matrix name must be a capital letter and cannot be "I"')

        self._matrices[name] = new_matrix"#;

            const FILE_11_22: &str = r#"    def __init__(self):
        """Initialise a MatrixWrapper object with a matrices dict."""
        self._matrices: dict[str, MatrixType | None] = {
            'A': None, 'B': None, 'C': None, 'D': None,
            'E': None, 'F': None, 'G': None, 'H': None,
            'I': np.eye(2),  # I is always defined as the identity matrix
            'J': None, 'K': None, 'L': None, 'M': None,
            'N': None, 'O': None, 'P': None, 'Q': None,
            'R': None, 'S': None, 'T': None, 'U': None,
            'V': None, 'W': None, 'X': None, 'Y': None,
            'Z': None
        }"#;

            let repo = get_repo();

            let snip = SnippetRef::from_comment(
                "%: 29ec1fedbf307e3b7ca731c4a381535fec899b0b\n%: src/lintrans/matrices/wrapper.py",
            )
            .unwrap();
            assert_eq!(snip.get_text(&repo).unwrap().body, FILE.to_string(),);
            assert_eq!(snip.get_text(&repo).unwrap().line_range, (1, 45));

            let snip = SnippetRef::from_comment(
                "%: 29ec1fedbf307e3b7ca731c4a381535fec899b0b\n%: src/lintrans/matrices/wrapper.py:11-22",
            )
            .unwrap();
            assert_eq!(snip.get_text(&repo).unwrap().body, FILE_11_22.to_string());
            assert_eq!(snip.get_text(&repo).unwrap().line_range, (11, 22));

            let snip = SnippetRef::from_comment(
                "%: 29ec1fedbf307e3b7ca731c4a381535fec899b0b\n%: src/lintrans/matrices/wrapper.py:11",
            )
            .unwrap();
            assert_eq!(
                snip.get_text(&repo).unwrap().body,
                "    def __init__(self):".to_string()
            );
            assert_eq!(snip.get_text(&repo).unwrap().line_range, (11, 11));
        }
    }

    mod snippet_text {
        use super::*;
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
                SnippetRef::from_comment(concat!(
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
                SnippetRef::from_comment(concat!(
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
                SnippetRef::from_comment(concat!(
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
                SnippetRef::from_comment(concat!(
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
                SnippetRef::from_comment(concat!(
                    "%: 3c490c48a0f4017ab8ee9cf471a65c251817b00e\n",
                    "%: src/lintrans/gui/main_window.py:333 noscopes"
                ))
                .unwrap()
                .get_text(&repo)
                .unwrap()
                .get_latex(),
                LATEX_5,
                "Testing noscopes option"
            )
        }
    }
}
