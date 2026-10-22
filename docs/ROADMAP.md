# Project roadmap

The goal is a believable, expandable Dushanbe-inspired GTA V map, not a collection of isolated props. Each phase must end with reviewable files and explicit checks before the next phase expands scope.

## Phase 0 — Development foundation

- [x] Set up repository rules, offline JSON validation, tests, and CI.
- [x] Start GTA V Map Agent and verify embedded CodeWalker world and camera.
- [x] Verify local Ollama `qwen3:4b` can place one existing game prop.
- [ ] Record exact target installation: GTA V Legacy or Enhanced.
- [ ] Decide deployment target: single-player mod or named multiplayer platform.

**Acceptance:** target edition/platform noted; local editor/agent setup recorded.

## Phase 1 — Central Dushanbe vertical slice

Proposed scope: Istiklol Square and a short adjoining boulevard, including the central monument/plaza, street/curb layout, pedestrian paths, landscape beds, a few surrounding building masses, and vehicle dressing.

- Establish reference images, source URLs, dates, proportions, and confidence notes.
- Set up a documented local coordinate frame and scale; do not invent surveyed coordinates.
- [x] Add `tools/blender/create_istiklol_greybox.py`, an editable Blender greybox generator for the base, road corridors, plaza footprint, sidewalks, simple building volumes, landmark massing, tree proxies and vehicle placeholders (dimensions are schematic).
- [ ] Run the script in Blender and review the generated scene; correct composition and scale against selected references.
- Refine the greybox: terrain/base, road corridors, plaza footprint, sidewalks, simple building volumes, and landmark massing.
- Review dimensions and sightlines against references from aerial and street-level views.
- Store original source geometry and metadata in the project; keep GTA game files out of Git.
- Keep the existing Map Agent lamp as a tool test, not as the foundation of the city geometry.

**Acceptance:** script runs in the chosen Blender version; greybox is visually reviewed; dimensions are documented as estimates or sourced measurements; a block-by-block list of assets still needed is recorded.

## Phase 2 — GTA V asset pipeline proof

- Install/select a Blender version and Sollumz version from their official upstream sources.
- Record the chosen GTA V edition and verify the exporter and CodeWalker can inspect one original simple asset.
- Export a small original road/plaza segment plus one simple building mass, including collision if the selected workflow requires it.
- Inspect exported files in CodeWalker. Do not yet claim in-game compatibility.
- Resolve LOD, texture, collision, and YMAP organization rules before expanding the asset count.

**Acceptance:** one original geometry test exported and readable in the toolchain with exact versions and steps documented.

## Phase 3 — Build the first complete city slice

- Replace greybox blocks with original architectural shapes and facades inspired by documented references.
- Build the landmark silhouette as original geometry rather than assuming a matching GTA prop exists.
- Add sidewalks, planted areas, street furniture, signs, road markings, and other visual details.
- Add parked decorative vehicles only after the geometry is stable. Drivable vehicles and live traffic behavior may require scripts/game systems beyond a static map file.
- Use Map Agent for optional existing-prop dressing and check each resulting placement.

**Acceptance:** the slice is visually coherent in the editor, scale and collisions are reviewed, and all new assets have source and license notes.

## Phase 4 — Export and in-game verification

- Export to the correct format for the chosen GTA V edition and deployment platform.
- Test in the target environment with a clean log; verify streaming, collisions, visibility, LODs, and performance.
- Record issues and fix them before extending to adjacent blocks.

**Acceptance:** a human tester confirms the city slice loads and works in the exact stated edition/platform.

## Phase 5 — Expand toward a larger Dushanbe map

- Extend from the first slice into adjacent roads and blocks in reviewable increments.
- Add more landmarks, building styles, public spaces, and traffic dressing.
- Keep a source register and asset provenance for every imported/reference item.
- Continue automated data checks and repeat in-game tests at milestone boundaries.

**Acceptance:** every area has editable sources, asset inventory, provenance, validation, and test evidence.
