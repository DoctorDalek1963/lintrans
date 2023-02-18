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

#[cfg(test)]
mod latex_tests;
mod snippet;

use self::snippet::Comment;
use color_eyre::eyre::Result;
use git2::Repository;
use lazy_static::lazy_static;
use regex::Regex;
use std::{env, fs, path::Path};

lazy_static! {
    /// The regex for the snippet comments. The options after filename should be given in
    /// alphabetic order.
    pub static ref COMMENT_PATTERN: Regex = Regex::new(concat!(
        r"(?m)^%: (?P<hash>[0-9a-f]{40})\n",
        r"%: (?P<filename>[^\s:]+)(:(?P<linenums>((\d+-\d+|\d+),?)+))?(?P<options>[^\n]*)$"
    ))
    .unwrap();

    /// The regex for the linenumbers in the snippet comments.
    pub static ref LINENUMS_PATTERN: Regex = Regex::new(r"^(?P<first>\d+)(-(?P<last>\d+))?$").unwrap();

    /// The copyright comment that appears at the top of newer files.
    pub static ref COPYRIGHT_COMMENT_PATTERN: Regex = Regex::new(
r"(#!/usr/bin/env python

)?#\s+lintrans - The linear transformation visualizer
#\s+Copyright \(C\) (2021-)?2022 D. Dyson \(DoctorDalek1963\)
#?
#\s+This program is licensed under GNU GPLv3, available here:
#\s+<https://www.gnu.org/licenses/gpl-3.0.html>
").unwrap();

}

/// Process every snippet in the given file and write out a processed version under a new name with
/// `processed_` prepended to the basename of the file.
fn process_all_snippets_in_file(filename: &str, repo: &Repository) -> Result<()> {
    let file_string = fs::read_to_string(filename)?;

    println!("{filename}");

    // Find all the snippet comments in the file and process each of them, to get an iterator of
    // tuples like `(comment, replacement_latex)`
    let comments_and_latex = COMMENT_PATTERN.find_iter(&file_string).map(|m| {
        let comment = Comment::from_latex_comment(m.as_str()).unwrap();
        println!("  {}", comment.details());
        (m.as_str(), comment.get_text(repo).unwrap().get_latex())
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
    println!();

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
fn get_repo() -> Repository {
    Repository::open(Path::new("../../lintrans/")).unwrap()
}
