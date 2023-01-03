//! This module contains everything to do with reading and generating code snippets.

mod comment;
mod config;
mod text;

pub use self::{comment::Comment, config::Config, text::Text};
