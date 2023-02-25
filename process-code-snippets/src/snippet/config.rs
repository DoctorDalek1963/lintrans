//! This module just contains config for the snippets.

use super::InfoCommentSyntax;
use color_eyre::Report;
use nom::{
    branch::alt,
    bytes::complete::tag,
    character::complete::{alpha1, multispace1},
    multi::separated_list0,
    sequence::{delimited, pair},
    IResult, Parser,
};
use nom_regex::str::{re_capture, re_find};
use regex::Regex;

/// A config struct to use for snippets. Defines options that can be used in snippets.
#[derive(Clone, Debug, PartialEq)]
pub struct Config {
    /// The language of the snippet. Defaults to Python.
    pub language: String,

    /// The custom info comment syntax of the snippet. Defaults to a leading #.
    pub info_comment: InfoCommentSyntax,

    /// Whether to keep the copyright comment. Defaults to false.
    pub keep_copyright_comment: bool,

    /// Whether to ignore containing scopes for the snippet. Defaults to false.
    pub no_scopes: bool,

    /// The lines to highlight. This is passed verbatim to `minted` through `highlightlines`.
    pub highlight_lines: Option<String>,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            language: String::from("python"),
            info_comment: InfoCommentSyntax::default(),
            keep_copyright_comment: false,
            no_scopes: false,
            highlight_lines: None,
        }
    }
}

/// An enum for recognised macros that are allowed in config.
///
/// In the config, the macro name must be appended with an exclamation mark, like `markdown!`. When
/// parsing, we expect the macro name _without_ the exclamation mark.
#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum ConfigMacro {
    Markdown,
}

impl ConfigMacro {
    /// Parse a config macro.
    fn parse(s: &str) -> Result<ConfigMacro, Report> {
        let macro_name = if s.ends_with("!") {
            &s[..s.len() - 1]
        } else {
            s
        };

        match macro_name {
            "markdown" => Ok(Self::Markdown),
            _ => Err(Report::msg(format!("Unrecognised macro name '{s}!'"))),
        }
    }

    /// Mutate the given config to apply the macro effects to it.
    fn mutate_config(&self, config: &mut Config) {
        match self {
            Self::Markdown => {
                config.language = String::from("lexers.py:MarkdownWithCommentsLexer -x");
                config.info_comment = InfoCommentSyntax::parse("<!-- {} -->");
            }
        };
    }
}

/// A simple enum of the available config options.
#[derive(Clone, Debug, Eq, PartialEq)]
enum ConfigOption {
    KeepCopyrightComment,
    NoScopes,
    Language(String),
    InfoComment(InfoCommentSyntax),
    HighlightLines(String),
    Macro(ConfigMacro),
}

impl ConfigOption {
    fn language(lang: &str) -> Self {
        Self::Language(if lang.contains(".py:") {
            lang.to_string()
        } else {
            lang.to_lowercase()
        })
    }

    fn info_comment(syntax: &str) -> Self {
        Self::InfoComment(InfoCommentSyntax::parse(syntax))
    }
}

/// Parse the options for the config. This function is a backend parsing function. Use
/// [`Config::parse`] for the public API.
fn parse_config_options(input: &str) -> IResult<&str, Config> {
    use ConfigOption::*;

    let no_double_quotes = Regex::new("[^\"]+").unwrap();
    let no_single_quotes = Regex::new("[^']+").unwrap();

    macro_rules! option_with_argument {
        ($parser:expr) => {
            alt((
                delimited(tag("'"), re_find(no_single_quotes.clone()), tag("'")),
                delimited(tag("\""), re_find(no_double_quotes.clone()), tag("\"")),
                $parser,
            ))
        };
        () => {
            alt((
                delimited(tag("'"), re_find(no_single_quotes.clone()), tag("'")),
                delimited(tag("\""), re_find(no_double_quotes.clone()), tag("\"")),
            ))
        };
    }

    let (input, (_, items)): (&str, (_, Vec<ConfigOption>)) = pair(
        tag(" "),
        separated_list0(
            multispace1,
            alt((
                tag("keep_copyright_comment").map(|_| KeepCopyrightComment),
                tag("noscopes").map(|_| NoScopes),
                pair(
                    tag("language="),
                    option_with_argument!(alpha1).map(|lang| ConfigOption::language(lang)),
                )
                .map(|(_, option)| option),
                pair(
                    tag("comment="),
                    option_with_argument!().map(|syntax| ConfigOption::info_comment(syntax)),
                )
                .map(|(_, option)| option),
                pair(
                    tag("highlight="),
                    option_with_argument!(re_find(Regex::new(r"[0-9,-]+").unwrap()))
                        .map(|lines| ConfigOption::HighlightLines(lines.to_string())),
                )
                .map(|(_, option)| option),
                re_capture(Regex::new(r"([^\s!]+)!").unwrap()).map(|captures| {
                    ConfigOption::Macro(ConfigMacro::parse(captures.get(1).unwrap()).unwrap())
                }),
            )),
        ),
    )(input)?;

    let mut config = Config::default();
    for item in items {
        match item {
            KeepCopyrightComment => config.keep_copyright_comment = true,
            NoScopes => config.no_scopes = true,
            Language(lang) => config.language = lang,
            InfoComment(syntax) => config.info_comment = syntax,
            HighlightLines(lines) => config.highlight_lines = Some(lines),
            Macro(macro_name) => macro_name.mutate_config(&mut config),
        };
    }

    Ok((input, config))
}

impl Config {
    /// Parse the config from the config options.
    pub fn parse(input: &str) -> Self {
        let mut input = input.to_string();
        if !input.starts_with(" ") {
            input = format!(" {input}");
        }

        parse_config_options(&input)
            .map(|(_, c)| c)
            .unwrap_or_default()
    }

    /// Return a string representing the config that the user would need to add to the snippet
    /// comment to get this config.
    ///
    /// The string will be empty or contain a leading space.
    pub fn details(&self) -> String {
        let mut s = String::new();

        if self.keep_copyright_comment {
            s.push_str(" keep_copyright_comment");
        }
        if self.no_scopes {
            s.push_str(" noscopes");
        }
        if self.language != "python" {
            s.push_str(" language=");
            if self.language.contains(" ") {
                s.push('"');
                s.push_str(&self.language);
                s.push('"');
            } else {
                s.push_str(&self.language);
            }
        }
        if self.info_comment != InfoCommentSyntax::default() {
            s.push_str(" comment=\"");
            s.push_str(&self.info_comment.before);
            s.push_str("{}");
            s.push_str(&self.info_comment.after);
            s.push('"');
        }
        if let Some(highlight_lines) = &self.highlight_lines {
            s.push_str(" highlight=");
            s.push_str(highlight_lines);
        }

        s
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use pretty_assertions::assert_eq;

    #[test]
    fn config_macro_parse_test() {
        assert_eq!(
            ConfigMacro::parse("markdown").unwrap(),
            ConfigMacro::Markdown
        );
        assert_eq!(
            ConfigMacro::parse("markdown!").unwrap(),
            ConfigMacro::Markdown
        );
        assert!(ConfigMacro::parse("not markdown!").is_err());
    }

    #[test]
    fn config_parse_test() {
        assert_eq!(Config::parse(""), Config::default());
        assert_eq!(Config::parse("bad options"), Config::default());
        assert_eq!(
            Config::parse("keep_copyright_comment"),
            Config {
                keep_copyright_comment: true,
                ..Default::default()
            }
        );
        assert_eq!(
            Config::parse("noscopes"),
            Config {
                no_scopes: true,
                ..Default::default()
            }
        );
        assert_eq!(
            Config::parse("language=yaml"),
            Config {
                language: String::from("yaml"),
                ..Default::default()
            }
        );
        assert_eq!(
            Config::parse("language=RUst"),
            Config {
                language: String::from("rust"),
                ..Default::default()
            }
        );
        assert_eq!(
            Config::parse("language='lexers.py:SphObjInvTextLexer -x'"),
            Config {
                language: String::from("lexers.py:SphObjInvTextLexer -x"),
                ..Default::default()
            }
        );
        assert_eq!(
            Config::parse("language=\"lexers.py:SphObjInvTextLexer -x\""),
            Config {
                language: String::from("lexers.py:SphObjInvTextLexer -x"),
                ..Default::default()
            }
        );

        assert_eq!(
            Config::parse("comment=\"<!-- {} -->\""),
            Config {
                info_comment: InfoCommentSyntax {
                    before: String::from("<!-- "),
                    after: String::from(" -->")
                },
                ..Default::default()
            }
        );

        assert_eq!(
            Config::parse("highlight=1,4-10,34-42"),
            Config {
                highlight_lines: Some(String::from("1,4-10,34-42")),
                ..Default::default()
            }
        );

        assert_eq!(
            Config::parse("keep_copyright_comment noscopes language=rust"),
            Config {
                keep_copyright_comment: true,
                no_scopes: true,
                language: String::from("rust"),
                info_comment: InfoCommentSyntax::default(),
                highlight_lines: None,
            }
        );
        assert_eq!(
            Config::parse("noscopes language=rust keep_copyright_comment"),
            Config {
                keep_copyright_comment: true,
                no_scopes: true,
                language: String::from("rust"),
                info_comment: InfoCommentSyntax::default(),
                highlight_lines: None,
            }
        );
        assert_eq!(
            Config::parse(
                "noscopes noscopes language=rust keep_copyright_comment highlight=213,240-245"
            ),
            Config {
                keep_copyright_comment: true,
                no_scopes: true,
                language: String::from("rust"),
                info_comment: InfoCommentSyntax::default(),
                highlight_lines: Some(String::from("213,240-245")),
            }
        );
        assert_eq!(
            Config::parse(
                "language=\"lexers.py:MarkdownWithCommentsLexer -x\" comment='<!-- {} -->'"
            ),
            Config {
                language: String::from("lexers.py:MarkdownWithCommentsLexer -x"),
                info_comment: InfoCommentSyntax {
                    before: String::from("<!-- "),
                    after: String::from(" -->")
                },
                ..Default::default()
            }
        );

        assert_eq!(
            Config::parse("markdown!"),
            Config {
                language: String::from("lexers.py:MarkdownWithCommentsLexer -x"),
                info_comment: InfoCommentSyntax {
                    before: String::from("<!-- "),
                    after: String::from(" -->")
                },
                ..Default::default()
            }
        );
    }
}
