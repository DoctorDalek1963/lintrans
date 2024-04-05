//! This module contains code to deal with the comment at the top of snippets that contains
//! information about them.

use lazy_static::lazy_static;
use regex::Regex;

lazy_static! {
    static ref COMMENT_SYNTAX_PATTERN: Regex = Regex::new(r"^([^{}]*)\{\}([^{}]*)$").unwrap();
}

/// A struct to represent a custom syntax for the info comments in snippets.
///
/// This allows for different comment types for languages like markdown, where the default # is not
/// a comment.
///
/// The info comments must be one line each, so neither field here should contain a newline. That
/// will result in line number alignment errors. Additionally, any spacing around comment syntax
/// should be specified here, since none will be added later.
///
/// To specify this in a snippet config, use:
/// ```text
/// comment="<!-- {} -->"
/// ```
/// or something similar, where `{}` represents the placement of the comment itself.
#[derive(Clone, Debug, Eq, PartialEq)]
pub struct InfoCommentSyntax {
    /// The fragment of syntax before the comment.
    pub before: String,

    /// The fragment of syntax after the comment.
    pub after: String,
}

impl Default for InfoCommentSyntax {
    fn default() -> Self {
        Self {
            before: String::from("# "),
            after: String::new(),
        }
    }
}

impl InfoCommentSyntax {
    /// Parse the info comment syntax from the config option. Panics if the input is invalid.
    pub fn parse(input: &str) -> Self {
        let captures = COMMENT_SYNTAX_PATTERN.captures(input).unwrap();
        let get = |n| captures.get(n).unwrap().as_str().to_string();

        InfoCommentSyntax {
            before: get(1),
            after: get(2),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use pretty_assertions::assert_eq;

    #[test]
    fn parse_test() {
        assert_eq!(
            InfoCommentSyntax::parse("// {}"),
            InfoCommentSyntax {
                before: String::from("// "),
                after: String::from("")
            }
        );
        assert_eq!(
            InfoCommentSyntax::parse("<!-- {} -->"),
            InfoCommentSyntax {
                before: String::from("<!-- "),
                after: String::from(" -->")
            }
        );
    }
}
