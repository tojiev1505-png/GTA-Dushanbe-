# Project instructions for AI agents

## Project scope
- Build an original, legally distributable map-mod project inspired by Dushanbe, Tajikistan, for the classic PC version of Grand Theft Auto: San Andreas.
- Do not attempt to launch the game unless the user explicitly confirms it is installed and asks for runtime testing.
- Treat real-world map references as research inputs; document provenance and avoid copying protected map assets or other people's mod assets without permission.

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
- Preserve the distinction between a planning prototype and game-ready map geometry.

## Validation
- Run `python scripts/validate_project.py`.
- Run `python -m unittest discover -s tests -v`.
- The CI workflow should run both commands on supported Python versions.
- Report test results truthfully; do not state a test passed unless it actually ran.

## Git workflow
- Make changes on a feature branch, never commit directly to `main` for routine project work.
- Open a pull request and do not merge it automatically.
- Inspect the full diff and check for prohibited game assets before opening a pull request.
