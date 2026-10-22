# Dushanbe-GTA

An original map project inspired by Dushanbe, Tajikistan, targeting **Grand Theft Auto V on PC**.

The repository contains planning data, validation tools, and a documented path toward an initial prototype. It does **not** include the game, Rockstar assets, or a playable build.

## Current status

- Project foundation and offline JSON validation are in place.
- **Local tool launch, 3D world loading, and camera navigation verified on 2026-10-22.**
- **AI placement is blocked:** on 2026-10-22, Claude Code repeatedly reported `Unable to connect to Anthropic services` and a 10-second timeout connecting to `api.anthropic.com`. GTA V Map Agent therefore reports `Not logged in · Please run /login`, but the CLI cannot reach the service to complete login.
- **In-game export/testing has not been performed.**
- The exact target installation—GTA V Legacy or Enhanced—must be recorded before making edition-specific compatibility claims.

## Initial prototype scope

The first goal is a small, reviewable Dushanbe-inspired scene rather than a claim to recreate the entire city. GTA V Map Agent can arrange existing GTA V props and export placements. It does not create new terrain, custom building models, interiors, or complete road geometry; those require a separate 3D authoring and game-format workflow.

The initial central-block data is an illustrative planning model only. Its coordinates use a fictional local Cartesian grid in metres. They are **not** surveyed Dushanbe coordinates or GTA V world coordinates, and cannot be loaded directly into the game as a map.

## Repository layout

- `AGENTS.md` — contribution and agent rules, including asset and edition boundaries.
- `docs/ROADMAP.md` — phased project plan.
- `docs/ARIANE_TOOLING.md` — tool research, checks, and current setup status.
- `docs/GTAV_MAPAGENT_WORKFLOW.md` — repeatable steps for the first small scene.
- `map-data/blocks/center_prototype.json` — illustrative block data in local project coordinates.
- `scripts/validate_project.py` — standard-library-only data validator.
- `tests/test_project_data.py` — four unit tests for schema and geometry constraints.
- `.github/workflows/validate.yml` — automated validation and tests.

## Requirements for project data

- Python 3.10 or later; the validator uses only the standard library.
- Git for version control.
- For the first prop-placement experiment, [GTA V Map Agent](https://github.com/cngil/gtav-mapagent) and a compatible GTA V PC installation.
- For original terrain, roads, and building models, a separately verified 3D authoring and GTA V export pipeline.

## Validate locally

From the repository root:

```bash
python scripts/validate_project.py
python -m unittest discover -s tests -v
```

## Legal and asset policy

Use only original assets or resources whose licenses permit the intended use. Do not add Rockstar game files, extracted assets, pirated copies, or assets from other mods without explicit redistribution permission. Users must obtain and install their own lawful copy of the game. A loaded 3D world is not proof that an exported map works in-game.

## External tool references

- [GTA V Map Agent](https://github.com/cngil/gtav-mapagent) — open-source prop-placement editor using CodeWalker and Claude Code. Its bundled CodeWalker has its own licensing notices; review them before redistributing bundled components.
