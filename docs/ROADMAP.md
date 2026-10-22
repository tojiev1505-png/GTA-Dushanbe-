# Project roadmap

This roadmap separates planning, prop-scene experiments, custom asset creation, and in-game testing. A milestone is complete only when its acceptance criteria have been checked.

## Phase 0 — Project foundation

- [x] Add contributor/agent rules and legal asset boundaries.
- [x] Add an illustrative central-block JSON prototype.
- [x] Add deterministic data validation and four unit tests.
- [x] Add CI for validation and tests.
- [x] Verify that the local GTA V Map Agent editor launches and CodeWalker renders the world.
- [x] Verify camera navigation in the embedded 3D view.
- [x] Verify that Ollama `qwen3:4b` can place one existing GTA V streetlight through the editor.

**Remaining:** complex multi-object placement, critic/review, export and in-game testing are not yet verified. Record the target GTA V edition (Legacy or Enhanced) and target platform before making compatibility claims.

## Phase 1 — First prop-based public square

- Keep the confirmed streetlight as the first smoke-test prop.
- Create a small Dushanbe-inspired public square with two benches facing each other, four streetlights total, and three planters.
- Use only existing props and a dedicated scene folder; do not create custom models in this step.
- Inspect the arrangement from several angles and resolve validation errors.
- Export JSON for review before attempting the target game format.

**Acceptance:** the requested prop layout appears in the editor, placement validation is clean or remaining limitations are documented, and a JSON export can be inspected.

## Phase 2 — Define the playable slice

- Choose a small Dushanbe-inspired location or landmark for the first intended release.
- Decide whether the first test targets single-player (for example, a Menyoo placement export) or a multiplayer server/resource format.
- Record reference sources and dates; separate verified observations from estimates.
- Define the relationship between the project's local planning coordinates and the chosen GTA V world location.
- Keep prototype coordinates fictional until measured or sourced.

**Acceptance:** chosen slice and target platform documented; source register and coordinate conventions established.

## Phase 3 — Verify export and game compatibility

- Confirm which game installation CodeWalker reads and whether it is Legacy or Enhanced.
- Export the small scene to the selected format and inspect the files.
- Test the output in the stated edition/platform; record the environment and results.
- Keep the exported scene separate from the fictional-coordinate block planning JSON until a valid transform is documented.

**Acceptance:** a small prop scene passes a recorded test in the chosen game edition/platform.

## Phase 4 — Original city geometry

- Research and verify a suitable pipeline for original terrain, roads, sidewalks, and building models.
- Create original geometry and textures, with documented scale, collision, and licensing.
- Test one small building/road segment before increasing scope.
- Do not claim that prop placement alone recreates Dushanbe or supplies new building interiors.

**Acceptance:** one original geometry segment exports, loads, and is verified in the target edition.

## Phase 5 — Expand carefully

- Add adjacent blocks, recognizable landmarks, and original visual details in small pull requests.
- Track provenance and licenses for all non-original reference material.
- Run automated checks on every change and in-game verification when a runnable slice exists.

**Acceptance:** each area has source data, asset provenance, review notes, and test evidence.
