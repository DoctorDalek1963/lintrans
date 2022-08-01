# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Qt5 and PyQt5 version numbers to the *About* dialog box
- Basis vectors now snap to integer coordinates in the visual definition dialog
- Allow for transitional animation in sequential animation (comma syntax)
- Info panel to display defined matrices
- Icon for window and taskbar
- Implement saving and loading session files

### Fixed

- Make program compatible with Python 3.8 and above
- Make link to documentation in help menu actually link properly
- Fix bug with stretches being detected as rotations
- Cancel animation before closing to prevent the app hanging in the background
- Make matrices with a column of 0s only render 1 rank line
- Reduce memory usage by automatically deleting closed dialogs
- Fix bug with matrices that are too small creating lag with too many lines
- Fix bug that caused crashes when animating very large matrices

## [0.2.2] - 2022-07-04

### Added

- Add options to hide background grid, transformed grid, and basis vectors
- Fully respect display settings in visual definition widget
- Support parenthesized sub-expressions as matrix identifiers
- Add proper rotation animation that rotates at constant speed
- Allow animation time to be varied

### Fixed

- Improve command line argument handling
- Fixed bug with premature rot evaluation in sub-expressions

## [0.2.1] - 2022-03-22

### Added 

- Explicit `@pyqtSlot` decorators
- Link to Qt5 docs in project docs with intersphinx
- Copyright comment in tests and `setup.py`
- Create version file for Windows compilation
- Create full compile.py script
- Add `Info.plist` file for macOS compilation
- Support --help and --version flags in `__main__.py`
- Create about dialog in help menu
- Implement minimum grid spacing

### Fixed

- Fix problems with compile script
- Fix small bugs and docstrings

## [0.2.0] - 2022-03-11

There were alpha tags before this, but I wasn't properly adhering to semantic versioning, so I'll start the changelog here.

If I'd been using semantic versioning from the start, there would much more changelog here, but instead, I'll just summarize the features.

### Added

- Matrix context with the `MatrixWrapper` class
- Parsing and evaluating matrix expressions
- A simple GUI with a viewport to render linear transformations
- Simple dialogs to create matrices and assign them to names
- Ability to render and animate linear transformations parsed from defined matrices
- Ability to zoom in and out of the viewport
- Add dialog to change display settings

[Unreleased]: https://github.com/DoctorDalek1963/lintrans/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/DoctorDalek1963/lintrans/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/DoctorDalek1963/lintrans/compare/13600cc6ff6299dc4a8101a367bc52fe08607554...v0.2.0
