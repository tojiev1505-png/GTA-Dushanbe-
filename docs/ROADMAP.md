# Project roadmap

This roadmap separates planning, prop-scene experiments, custom asset creation, and in-game testing. A milestone is complete only when its acceptance criteria have been checked.

## Phase 0 — Project foundation

- [x] Add contributor/agent rules and legal asset boundaries.
- [x] Add an illustrative central-block JSON prototype.
- [x] Add deterministic data validation and four unit tests.
- [x] Add CI for validation and tests.
- [x] Verify that the local GTA V Map Agent editor launches and CodeWalker renders the world.
- [x] Verify camera navigation in the embedded 3D view.

**Remaining:** AI prop placement is blocked. Claude Code repeatedly timed out connecting to `api.anthropic.com` on 2026-10-22, so sign-in cannot complete. Diagnose ordinary network/firewall access if operating in an officially supported region; otherwise select and implement a supported alternative provider. Game export/testing is also pending, and the target GTA V edition (Legacy or Enhanced) must be recorded.

## Phase 1 — Define the first playable slice

- Choose a small Dushanbe-inspired area or landmark for the initial prototype.
- Decide whether the first test targets single-player (for example, a Menyoo placement export) or a multiplayer server/resource format.
- Record reference sources and dates; separate verified observations from estimates.
- Define the relationship between the project's local planning coordinates and the chosen GTA V world location.
- Keep prototype coordinates fictional until measured or sourced.

**Acceptance:** chosen slice and target platform documented; source register and coordinate conventions established.

## Phase 2 — Verify the GTA V toolchain

- Confirm which game installation CodeWalker reads and whether it is Legacy or Enhanced.
- Camera and viewport controls have been verified.
- Resolve the Claude API connectivity/login blocker or implement and test a supported alternative backend before relying on automated placement.
- Create a disposable scene using only existing GTA V props.
- Export a tiny scene and inspect the output files.

**Acceptance:** reproducible setup notes, a small exported test scene, and a recorded target edition/platform.

## Phase 3 — First prop-based scene

- Build a small Dushanbe-inspired roadside or plaza scene using existing game props.
- Review scale, alignment, collision, visibility, and placement from multiple angles.
- Export to the chosen format and test it in the stated game edition/platform.
- Keep the exported scene separate from the fictional-coordinate block planning JSON until a valid transform is documented.

**Acceptance:** a small scene is visibly correct in the editor and passes a recorded in-game test.

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
