# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.1] - 2026-09-15

### Fixed (test suite only, no behavior change)
- Removed `tests/test_cli.py`, `tests/test_preset.py`,
  `tests/test_validator.py`: unmodified copies of `diamond-setup`'s own
  test suite, exercising only `diamond_setup` internals, never
  `vrig-cosmological` code. No CLI of its own, so no replacement test
  was needed.

### Fixed (metadata, no behavior change)
- `src/vrig_cosmological/__init__.py`'s `__version__` was never updated
  for the 1.0.0 release — still read `"0.1.0"`. Corrected to track the
  actual released version going forward.

## [1.0.0] - 2026
### Added
- Initial v1.0.0 release as part of the GenesisAeon ecosystem-wide 1.0.0
  milestone.
- Standardized release tooling: `.zenodo.json`, GitHub Actions release
  workflow (`.github/workflows/release.yml`), `RELEASE_GUIDE.md`,
  `CONTRIBUTING.md`, issue/PR templates.

### Changed
- Project metadata (`pyproject.toml`) normalized: version bumped to
  1.0.0, license, authors, `requires-python`, dependency pins.
- Relicensed to dual-license: GPLv3-or-later (code) + CC BY 4.0
  (documentation).

### Fixed
- `README.md` previously contained content describing the unrelated
  `diamond-setup` scaffold tool (a leftover from project scaffolding);
  replaced with content describing `vrig-cosmological` itself.
