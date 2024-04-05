//! This module contains code to deal with reading and interpreting LaTeX comments that refer to snippets.

use super::{Config, Text};
use crate::{COMMENT_PATTERN, COPYRIGHT_COMMENT_PATTERN};
use color_eyre::eyre::Result;
use git2::{Oid, Repository};
use itertools::Itertools;
use nom::{
    branch::alt, bytes::complete::tag, character::complete, multi::separated_list1,
    sequence::separated_pair, IResult, Parser,
};
use std::path::Path;

/// A reference to a code snippet, as used in comments.
#[derive(Clone, Debug, PartialEq)]
pub struct Comment<'s> {
    /// The commit hash.
    hash: Oid,

    /// The file path.
    filename: &'s Path,

    /// The start and end lines of each snippet. If [`None`], then the whole file is implied.
    line_ranges: Option<Vec<(u32, u32)>>,

    /// The config for this snippet.
    config: Config,
}

/// Parse line ranges from the input.
fn parse_line_ranges(input: &str) -> IResult<&str, Vec<(u32, u32)>> {
    separated_list1(
        tag(","),
        alt((
            separated_pair(complete::u32, tag("-"), complete::u32),
            complete::u32.map(|n| (n, n)),
        )),
    )(input)
}

impl<'s> Comment<'s> {
    /// Create a snippet from a pair of LaTeX snippet comments with the hash and file information.
    pub fn from_latex_comment(comment: &'s str) -> Option<Self> {
        let c = COMMENT_PATTERN.captures(comment)?;

        // Parse the hash and filename
        let hash = Oid::from_str(c.name("hash")?.as_str()).ok()?;
        let filename = Path::new(c.name("filename")?.as_str());

        // Parse the line numbers. If we don't have line numbers here, then they are `None`. This
        // will be resolved by [`get_text`] when getting the text from the commit with the repo
        let line_ranges = c.name("linenums").map(|m| {
            parse_line_ranges(m.as_str())
                .expect("We should be able to parse line numbers if they've matched the regex")
                .1
        });

        // Check the options and create a config struct for them.
        let config = Config::parse(
            c.name("options")
                .expect("There should always be options, even if they're empty")
                .as_str(),
        );

        Some(Self {
            hash,
            filename,
            line_ranges,
            config,
        })
    }

    /// Return the raw text of the snippet, removing the copyright comment if the whole file was included.
    ///
    /// The string returned does not include a trailing newline.
    #[allow(unstable_name_collisions)]
    pub fn get_text(self, repo: &Repository) -> Result<Text<'s>> {
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
                ));
            }
        };

        let bodies: Vec<(String, u32, u32)> = match &self.line_ranges {
            None => {
                let mut first = 1;
                let last = content.lines().count() as u32;

                // If we've got a copyright comment, then remove it and update the line number accordingly
                if !self.config.keep_copyright_comment && first == 1 {
                    let first_n = |n| {
                        content
                            .lines()
                            .take(n)
                            .intersperse("\n")
                            .collect::<String>()
                    };

                    if COPYRIGHT_COMMENT_PATTERN.is_match(&first_n(6)) {
                        first = 7;
                    } else if COPYRIGHT_COMMENT_PATTERN.is_match(&first_n(8)) {
                        first = 9;
                    }
                }

                // The body is just the section of the content from the first line to the last line,
                // interspersed with newlines
                let body: String = content
                    .lines()
                    .skip((first - 1) as usize)
                    .take(1 + (last - first) as usize)
                    .intersperse("\n")
                    .collect();

                vec![(body, first, last)]
            }
            Some(ranges) => ranges
                .iter()
                .map(|&(first, last)| {
                    (
                        content
                            .lines()
                            .skip((first - 1) as usize)
                            .take(1 + (last - first) as usize)
                            .intersperse("\n")
                            .collect(),
                        first,
                        last,
                    )
                })
                .collect(),
        };

        // Get the line range or use 1 to the end of the file
        // We now calculate a vector that maps line numbers to line contents.
        // Each line is a line above the snippet which has less indentation, indicating that it is
        // an enclosing scope. This works because all the snippets are Python, which uses
        // meaningful whitespace for scoping
        let scopes: Vec<(u32, String)> = if !self.config.no_scopes {
            // The first line of any snippet body
            let first = *bodies.iter().map(|(_, n, _)| n).min().unwrap();

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

        Ok(Text {
            hash: self.hash,
            filename: self.filename,
            // We need to wrap custom lexers with '' for very weird reasons for minted versions >= 2.7
            // See https://tex.stackexchange.com/a/703698
            language: if self.config.language.contains(" -x") {
                format!("'{}'", self.config.language)
            } else {
                self.config.language
            },
            info_comment_syntax: self.config.info_comment,
            highlight_lines: self.config.highlight_lines,
            scopes,
            bodies,
        })
    }

    /// Return a string containing the details of this snippet reference.
    ///
    /// The string contains the first 4 bytes of the hash, the filename, (possibly) linenumbers,
    /// and the config. See [`Config`].
    pub fn details(&self) -> String {
        let hash = hex::encode(&self.hash.as_bytes()[..4]);
        let filename = self.filename.to_str().unwrap();
        let linenums = match &self.line_ranges {
            None => "".to_string(),
            Some(pairs) => {
                String::from(":")
                    + &pairs
                        .iter()
                        .map(|(first, last)| {
                            if first == last {
                                first.to_string()
                            } else {
                                format!("{first}-{last}")
                            }
                        })
                        .join(",")
            }
        };
        let config = self.config.details();

        format!("{hash} {filename}{linenums}{config}")
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::get_repo;
    use pretty_assertions::assert_eq;

    #[test]
    fn parse_line_ranges_test() {
        assert_eq!(parse_line_ranges("123-234"), Ok(("", vec![(123, 234)])));
        assert_eq!(
            parse_line_ranges("123-234,250-300"),
            Ok(("", vec![(123, 234), (250, 300)]))
        );
        assert_eq!(parse_line_ranges("123"), Ok(("", vec![(123, 123)])));
    }

    #[test]
    fn from_comment_test() {
        let comment =
            "%: 29ec1fedbf307e3b7ca731c4a381535fec899b0b\n%: src/lintrans/matrices/wrapper.py";
        let snip = Comment {
            hash: Oid::from_str("29ec1fedbf307e3b7ca731c4a381535fec899b0b").unwrap(),
            filename: Path::new("src/lintrans/matrices/wrapper.py"),
            line_ranges: None,
            config: Config::default(),
        };
        assert_eq!(Comment::from_latex_comment(comment).unwrap(), snip);

        let comment =
            "%: 29ec1fedbf307e3b7ca731c4a381535fec899b0b\n%: src/lintrans/matrices/wrapper.py:11-22";
        let snip = Comment {
            hash: Oid::from_str("29ec1fedbf307e3b7ca731c4a381535fec899b0b").unwrap(),
            filename: Path::new("src/lintrans/matrices/wrapper.py"),
            line_ranges: Some(vec![(11, 22)]),
            config: Config::default(),
        };
        assert_eq!(Comment::from_latex_comment(comment).unwrap(), snip);

        let comment =
            "%: 29ec1fedbf307e3b7ca731c4a381535fec899b0b\n%: src/lintrans/matrices/wrapper.py:11";
        let snip = Comment {
            hash: Oid::from_str("29ec1fedbf307e3b7ca731c4a381535fec899b0b").unwrap(),
            filename: Path::new("src/lintrans/matrices/wrapper.py"),
            line_ranges: Some(vec![(11, 11)]),
            config: Config::default(),
        };
        assert_eq!(Comment::from_latex_comment(comment).unwrap(), snip);

        let comment =
            "%: 29ec1fedbf307e3b7ca731c4a381535fec899b0b\n%: src/lintrans/matrices/wrapper.py:11-20,24,31-40";
        let snip = Comment {
            hash: Oid::from_str("29ec1fedbf307e3b7ca731c4a381535fec899b0b").unwrap(),
            filename: Path::new("src/lintrans/matrices/wrapper.py"),
            line_ranges: Some(vec![(11, 20), (24, 24), (31, 40)]),
            config: Config::default(),
        };
        assert_eq!(Comment::from_latex_comment(comment).unwrap(), snip);
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

        const FILE_31_40: &str = r#"        return self._matrices[name]

    def __setitem__(self, name: str, new_matrix: MatrixType) -> None:
        """Set the value of matrix `name` with the new_matrix.

        Raises:
            ValueError:
                If `name` isn't a valid matrix name
        """
        name = name.upper()"#;

        let repo = get_repo();

        let snip = Comment::from_latex_comment(
            "%: 29ec1fedbf307e3b7ca731c4a381535fec899b0b\n%: src/lintrans/matrices/wrapper.py",
        )
        .unwrap();
        assert_eq!(
            snip.get_text(&repo).unwrap().bodies,
            vec![(FILE.to_string(), 1, 45)]
        );

        let snip = Comment::from_latex_comment(
                "%: 29ec1fedbf307e3b7ca731c4a381535fec899b0b\n%: src/lintrans/matrices/wrapper.py:11-22",
            )
            .unwrap();
        assert_eq!(
            snip.get_text(&repo).unwrap().bodies,
            vec![(FILE_11_22.to_string(), 11, 22)]
        );

        let snip = Comment::from_latex_comment(
            "%: 29ec1fedbf307e3b7ca731c4a381535fec899b0b\n%: src/lintrans/matrices/wrapper.py:11",
        )
        .unwrap();
        assert_eq!(
            snip.get_text(&repo).unwrap().bodies,
            vec![("    def __init__(self):".to_string(), 11, 11)]
        );

        let snip = Comment::from_latex_comment(
            "%: 29ec1fedbf307e3b7ca731c4a381535fec899b0b\n%: src/lintrans/matrices/wrapper.py:11-22,24,31-40",
        )
        .unwrap();
        assert_eq!(
            snip.get_text(&repo).unwrap().bodies,
            vec![
                (FILE_11_22.to_string(), 11, 22),
                (
                    "    def __getitem__(self, name: str) -> MatrixType | None:".to_string(),
                    24,
                    24
                ),
                (FILE_31_40.to_string(), 31, 40)
            ]
        );
    }
}
