# Project instructions for AI agents

## Project scope
- Build an original, legally distributable map project inspired by Dushanbe, Tajikistan, for GTA V on PC.
- The current exploratory toolchain uses GTA V Map Agent and its bundled CodeWalker viewer. Map Agent places existing GTA V props; it does not create new terrain, custom building models, or complete city geometry.
- Keep planning data, GTA world coordinates, exported map assets, and in-game test evidence clearly separate.
- Record whether the target game installation is GTA V Legacy or Enhanced before claiming edition-specific compatibility. Do not assume assets or exports are interchangeable across editions.
- Do not claim a map is playable until it has been tested in the stated game edition and target platform.

## Legal and asset boundaries
- Never commit Rockstar game binaries, archives, textures, audio, models, scripts, executables, or extracted game data.
- Do not commit third-party assets unless their license permits redistribution and the source/license are documented.
- Prefer original project-authored JSON, code, Blender source files, and original assets.
- Keep local game paths, credentials, tokens, and machine-specific settings out of version control.

## Data and code conventions
- Keep prototype map data machine-readable JSON with a documented schema and explicit units.
- Use UTF-8 text, LF line endings, descriptive file names, and small reviewable commits.
- Add tests for data validation and keep validation deterministic and offline.
- Do not invent surveyed geographic coordinates. Mark illustrative prototype geometry as fictional/local coordinates until verified.
- Never treat fictional local coordinates as GTA V world coordinates without a documented coordinate transform or measured placement reference.
- Preserve the distinction between a planning prototype, prop-placement scene, custom geometry, exported game assets, and a verified playable build.

## Validation
- Run `python scripts/validate_project.py`.
- Run `python -m unittest discover -s tests -v`.
- The CI workflow should run both commands on supported Python versions.
- Report test results truthfully; do not state a test passed unless it actually ran.

## Git workflow
- Make changes on a feature branch, never commit directly to `main` for routine project work.
- Open a pull request and do not merge it automatically.
- Inspect the full diff and check for prohibited game assets before opening a pull request.
