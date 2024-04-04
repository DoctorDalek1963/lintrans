//! This module contains code to deal with converting snippet text taken from commits into LaTeX code.

use super::InfoCommentSyntax;
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

    /// The language of the snippet.
    pub language: String,

    /// The comment syntax to use for the info comments.
    pub info_comment_syntax: InfoCommentSyntax,

    /// The config to pass to the `highlightlines` option of `minted`.
    pub highlight_lines: Option<String>,

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

        s.push_str(r"\begin{minted}[firstnumber=-3");
        if let Some(lines) = &self.highlight_lines {
            s.push_str(", highlightlines={");
            s.push_str(lines);
            s.push('}');
        }
        s.push_str("]{");
        s.push_str(&self.language);
        s.push_str("}");
        s.push('\n');

        // Add the commit hash as a comment
        s.push_str(&self.info_comment_syntax.before);
        s.push_str(&self.hash.to_string());
        s.push_str(&self.info_comment_syntax.after);
        s.push('\n');

        // Add the filename as a comment
        s.push_str(&self.info_comment_syntax.before);
        s.push_str(
            self.filename
                .to_str()
                .expect("Filename should be UTF-8 encoded"),
        );
        s.push_str(&self.info_comment_syntax.after);
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
