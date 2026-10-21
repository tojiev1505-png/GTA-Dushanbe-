# Dushanbe-GTA

An original map-mod project for the classic PC edition of **Grand Theft Auto: San Andreas**, inspired by Dushanbe, Tajikistan.

The repository begins with planning data and validation tools. It does **not** include the game or any Rockstar assets, and it does not claim to be a playable build.

## Current scope

- Establish project rules and an incremental roadmap.
- Define a small, clearly fictional central-district block as a data prototype.
- Validate project JSON and run unit tests automatically through GitHub Actions.
- Research a compatible, legally usable mapping workflow before producing game-specific assets.

## Repository layout

- `AGENTS.md` — contributor and agent rules, including asset boundaries.
- `docs/ROADMAP.md` — phased project plan.
- `docs/ARIANE_TOOLING.md` — tooling research and workflow notes; verify tool compatibility before adoption.
- `map-data/blocks/center_prototype.json` — illustrative block data in local project coordinates.
- `scripts/validate_project.py` — standard-library-only data validator.
- `tests/test_project_data.py` — four unit tests for schema and geometry constraints.
- `.github/workflows/validate.yml` — automated validation and test workflow.

## Requirements

- Python 3.10 or later (the validator uses only the Python standard library).
- Git for version control.
- For future asset authoring: a suitable 3D editor and version-compatible GTA San Andreas modding tools, selected after research.

## Validate locally

From the repository root:

```bash
python scripts/validate_project.py
python -m unittest discover -s tests -v
```

The data coordinates are fictional local coordinates in metres, not surveyed coordinates for real streets. The prototype is a planning example, not a GTA map export.

## Legal and asset policy

Use only original assets or resources whose licenses permit the intended use. Do not add Rockstar game files, extracted assets, pirated copies, or assets from other mods without explicit redistribution permission. Users must obtain and install their own lawful copy of the game. No game launch or runtime validation has been performed as part of this repository setup.
