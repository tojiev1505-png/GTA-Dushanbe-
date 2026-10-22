# Dushanbe-GTA

An original GTA V PC map-mod project inspired by Dushanbe, Tajikistan.

This is moving beyond prop-placement tests toward a real city slice: custom road and plaza geometry, original building masses and facades, recognizable landmarks, landscaping, and staged vehicle dressing. The repository does **not** include the game, Rockstar assets, or a playable build.

## Current status

- Project validation, tests, and CI are in place.
- **Editor, embedded CodeWalker world, and camera navigation verified on 2026-10-22.**
- **Local AI placement verified on 2026-10-22:** GTA V Map Agent with Ollama `qwen3:4b` successfully placed one existing GTA V streetlight.
- **Real custom city geometry, map export, and in-game testing have not yet been verified.**
- The GTA V installation edition and target deployment (single-player or a multiplayer platform) must be recorded before making compatibility claims.

## First serious city slice

The proposed first slice is **Istiklol Square and a short adjoining boulevard segment**, with the monument/plaza, approach roads, sidewalks, landscaped beds, a small number of surrounding building masses, and appropriate parked-vehicle dressing. This is a bounded vertical slice that can grow into adjacent blocks after scale, collisions, exports, and performance are checked.

See [the city-slice plan](docs/CITY_SLICE_PLAN.md) for scope, toolchain, reference sources, layers, and acceptance criteria. The first editable Blender greybox generator is [here](tools/blender/create_istiklol_greybox.py). It is schematic and not a game-ready export.

## Toolchain roles

- **Blender + Sollumz:** author original buildings, road pieces, plaza geometry, and map assets. Sollumz is an open-source Blender add-on for creating/importing/exporting GTA V assets; its YMAP workflow and exact version must be verified for the chosen GTA V edition.
- **CodeWalker:** inspect game world geometry and verify coordinates/assets.
- **GTA V Map Agent + local Ollama/Qwen:** quickly place existing game props for set dressing and test tool-driven iteration. It does not, by itself, replace Los Santos, create terrain, model custom buildings, or build a complete road network.
- **GitHub project data/CI:** track original source data, provenance, scripts, validation, and incremental deliverables.

## Local AI configuration

The known working setup for the prop-placement test used Ollama's local Anthropic-compatible endpoint in the same PowerShell session used to launch the editor:

```powershell
$env:ANTHROPIC_BASE_URL = "http://localhost:11434"
$env:ANTHROPIC_AUTH_TOKEN = "ollama"
$env:ANTHROPIC_API_KEY = ""
$env:MAP_EDITOR_MODEL = "qwen3:4b"
```

One simple prop placement was confirmed by the user. Larger scenes, critic/review loops, custom asset creation, map export, and in-game behavior remain to be tested.

## Repository layout

- `AGENTS.md` — contribution and asset rules.
- `docs/ROADMAP.md` — phases and acceptance criteria.
- `docs/CITY_SLICE_PLAN.md` — first serious city slice and work breakdown.
- `tools/blender/create_istiklol_greybox.py` — Blender script that generates an editable schematic greybox with roads, plaza, landmark massing, building volumes, trees and vehicle placeholders.
- `docs/ARIANE_TOOLING.md` — tool research and compatibility notes.
- `docs/GTAV_MAPAGENT_WORKFLOW.md` — optional prop-placement/set-dressing workflow.
- `map-data/blocks/center_prototype.json` — legacy illustrative planning example; not real survey or GTA coordinates.
- `scripts/validate_project.py` and `tests/test_project_data.py` — offline JSON validation and tests.
- `.github/workflows/validate.yml` — CI validation.

## Validate locally

```bash
python scripts/validate_project.py
python -m unittest discover -s tests -v
```

## Legal and asset policy

Do not commit Rockstar game binaries, archives, extracted models/textures, credentials, or third-party mod assets without redistribution rights. Keep source references and licenses documented. A model visible in CodeWalker is not proof that an exported map works in the selected GTA V edition.

## External tools

- [Sollumz](https://github.com/Sollumz/Sollumz) — Blender add-on for GTA V asset creation and map workflows.
- [GTA V Map Agent](https://github.com/cngil/gtav-mapagent) — AI-assisted placement of existing game props and scene export.
