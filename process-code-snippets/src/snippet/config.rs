//! This module just contains config for the snippets.

/// A config struct to use for snippets. Defines some options that can be used in snippets.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Config {
    /// Whether to remove the copyright comment. Defaults to true.
    pub remove_copyright_comment: bool,

    /// Whether to show containing scopes for the snippet. Defaults to true.
    pub use_scopes: bool,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            remove_copyright_comment: true,
            use_scopes: true,
        }
    }
}

impl Config {
    /// Return a string representing the config that the user would need to add to the snippet
    /// comment to get this config.
    ///
    /// The string will be empty or contain a leading space.
    pub fn details(&self) -> String {
        let mut s = String::new();

        if !self.remove_copyright_comment {
            s.push_str(" keep_copyright_comment");
        }
        if !self.use_scopes {
            s.push_str(" noscopes");
        }

        s
    }
}
