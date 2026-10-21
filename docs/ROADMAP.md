# Project roadmap

This roadmap separates early design and data validation from actual in-game implementation. A milestone is complete only when its acceptance criteria have been checked.

## Phase 0 — Project foundation (current)

- [x] Add contributor/agent rules and legal asset boundaries.
- [x] Add a first illustrative central-block JSON prototype.
- [x] Add deterministic data validation and four unit tests.
- [x] Add CI for validation and tests.
- [ ] Review and approve the foundation pull request.

**Acceptance:** validator succeeds; all four unit tests pass; no third-party game assets are present.

## Phase 1 — Define the mapping reference

- Choose a manageable, well-defined district in Dushanbe for the first playable slice.
- Record public reference sources and dates; separate verified observations from estimates.
- Define coordinate conventions, block IDs, road widths, elevation assumptions, and metadata schema.
- Keep prototype coordinates fictional until measured or sourced.

**Acceptance:** documented source register and a stable, versioned data schema.

## Phase 2 — Select an asset toolchain

- Confirm the target game edition and the supported formats used by the selected community tools.
- Verify tool licensing, project activity, safety, and compatibility from primary documentation.
- Create a minimal blank scene and export a test object using only original assets.
- Document setup steps without bundling proprietary game files.

**Acceptance:** a reproducible toolchain guide and a tiny original test asset that can be inspected in the intended tools.

## Phase 3 — Central-district blockout

- Build terrain, roads, intersections, sidewalks, and building footprints from original geometry.
- Add a repeatable naming and placement convention.
- Review scale, collision, visibility, and navigation in the target editor.
- Avoid claiming in-game compatibility until a legal local installation is available for testing.

**Acceptance:** reviewable blockout source files, documented coordinates, and a verification checklist.

## Phase 4 — Playable vertical slice

- Implement one small area with collision and basic navigation.
- Validate performance and streaming boundaries using the target game and compatible tools.
- Track limitations and bugs as issues.

**Acceptance:** a human tester confirms the slice works in the intended game version; record the test environment and results.

## Phase 5 — Expand carefully

- Add adjacent blocks, landmarks, roads, and original visual details in small pull requests.
- Track provenance and licenses for all non-original reference material.
- Run automated checks on every change and periodic in-game verification when available.

**Acceptance:** each area has source data, asset provenance, review notes, and test evidence.
