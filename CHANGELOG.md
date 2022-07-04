# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Nothing here yet...

### Added

- Add options to hide background grid, transformed grid, and basis vectors
- Fully respect display settings in visual definition widget
- Add proper rotation animation that rotates at constant speed

### Fixed

- Improve command line argument handling

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
