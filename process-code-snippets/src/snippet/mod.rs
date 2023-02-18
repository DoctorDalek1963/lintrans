//! This module contains everything to do with reading and generating code snippets.

mod comment;
mod config;
mod info_comment;
mod text;

pub use self::{comment::Comment, config::Config, info_comment::InfoCommentSyntax, text::Text};
