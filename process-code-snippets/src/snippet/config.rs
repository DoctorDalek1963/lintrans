//! This module just contains config for the snippets.

use nom::{
    branch::alt,
    bytes::complete::tag,
    character::complete::{alpha1, multispace1},
    multi::separated_list0,
    sequence::{delimited, pair},
    IResult, Parser,
};
use nom_regex::str::re_find;
use regex::Regex;

/// A config struct to use for snippets. Defines options that can be used in snippets.
#[derive(Clone, Debug, PartialEq)]
pub struct Config {
    /// The language of the snippet. Defaults to Python.
    pub language: String,

    /// Whether to keep the copyright comment. Defaults to false.
    pub keep_copyright_comment: bool,

    /// Whether to ignore containing scopes for the snippet. Defaults to false.
    pub no_scopes: bool,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            language: String::from("python"),
            keep_copyright_comment: false,
            no_scopes: false,
        }
    }
}

/// A simple enum of the available config options.
#[derive(Debug, Eq, PartialEq)]
enum ConfigOption {
    KeepCopyrightComment,
    NoScopes,
    Language(String),
}

impl ConfigOption {
    fn language(lang: &str) -> Self {
        Self::Language(if lang.contains(".py:") {
            lang.to_string()
        } else {
            lang.to_lowercase()
        })
    }
}

/// Parse the options for the config. This function is a backend parsing function. Use
/// [`Config::parse`] for the public API.
fn parse_config_options(input: &str) -> IResult<&str, Config> {
    use ConfigOption::*;

    let no_double_quotes = Regex::new("[^\"]+").unwrap();
    let no_single_quotes = Regex::new("[^']+").unwrap();

    let (input, (_, items)): (&str, (_, Vec<ConfigOption>)) = pair(
        tag(" "),
        separated_list0(
            multispace1,
            alt((
                tag("keep_copyright_comment").map(|_| KeepCopyrightComment),
                tag("noscopes").map(|_| NoScopes),
                pair(
                    tag("language="),
                    alt((
                        delimited(tag("'"), re_find(no_single_quotes), tag("'")),
                        delimited(tag("\""), re_find(no_double_quotes), tag("\"")),
                        alpha1,
                    ))
                    .map(|lang| ConfigOption::language(lang)),
                )
                .map(|(_, option)| option),
            )),
        ),
    )(input)?;

    let mut config = Config::default();
    for item in items {
        match item {
            KeepCopyrightComment => config.keep_copyright_comment = true,
            NoScopes => config.no_scopes = true,
            Language(lang) => config.language = lang,
        };
    }

    Ok((input, config))
}

impl Config {
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

        s
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use pretty_assertions::assert_eq;

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
            Config::parse("keep_copyright_comment noscopes language=rust"),
            Config {
                keep_copyright_comment: true,
                no_scopes: true,
                language: String::from("rust")
            }
        );
        assert_eq!(
            Config::parse("noscopes language=rust keep_copyright_comment"),
            Config {
                keep_copyright_comment: true,
                no_scopes: true,
                language: String::from("rust")
            }
        );
        assert_eq!(
            Config::parse("noscopes noscopes language=rust keep_copyright_comment"),
            Config {
                keep_copyright_comment: true,
                no_scopes: true,
                language: String::from("rust")
            }
        );
    }
}
