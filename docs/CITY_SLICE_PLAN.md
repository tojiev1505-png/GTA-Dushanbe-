# First serious city slice: Istiklol Square and adjoining boulevard

## Goal

Build a recognizable, expandable central Dushanbe environment for GTA V. Start with one bounded city slice rather than trying to recreate the entire capital in one pass.

**Proposed slice:** Istiklol (Independence) Square, its landmark/plaza composition, a short adjoining boulevard approach, and the nearest surrounding building blocks. The goal is an editable greybox first, then a tested GTA asset export—not just a staged prop arrangement.

## Visual target and reference register

Treat references as evidence for shape, layout and visual character, not as source assets to copy. Record the date accessed and separate measured facts from estimates.

- **Official Tajikistan investment/government source: Istiklol Square inauguration** — https://investcom.tj/82-iftitoi-majdoni-istilol-va-mamaai-memorii-ramzi-istilol-dar-shari.html  
  Use for the landmark silhouette, circular/plaza composition and landscaped geometry. Reference image located 2026-10-22.
- **Dushanbe central-landmark aerial photograph** — https://www.gettyimages.com/  
  Search result: central Independence Monument, broad gardens and surrounding road network; image license/use rights must be checked before using or reproducing any actual image.
- **Sollumz upstream documentation/source** — https://github.com/Sollumz/Sollumz  
  Tooling reference only, not city geometry.

Add new sources only with URL, access date, intended use, confidence, and license/attribution notes. For road alignment and measurements, seek a verifiable street map or official plan; do not claim metric accuracy from a perspective photograph.

## Build scope

### A. Greybox geometry
- One consistent project coordinate frame with metres as units.
- Ground/base surface and approximate local terrain.
- Plaza footprint and main approach axis.
- Boulevard lanes, medians, curb edges, junctions and sidewalks.
- Basic adjacent block/building volumes to establish skyline and camera views.
- Monument/landmark massing placeholder with overall proportions, kept as original geometry.
- Landscape-bed outlines and pedestrian paths.

### B. Replace placeholders
- Refine road and plaza dimensions using source references and an explicit confidence note.
- Make original building silhouettes and facade rhythms for the immediate surrounding blocks.
- Build the landmark as original art-inspired geometry; do not extract proprietary models.
- Add pavement materials, road markings, trees, planters, light fixtures, signs and public-space details.

### C. Vehicle dressing
- First use static parked vehicle models only if the chosen toolchain reliably supports those models in exported map data.
- Record exact model names and validate ground contact/collisions.
- Treat moving cars, traffic AI, and drivable vehicles as a separate runtime/script task, not as a consequence of placing a static map object.

### D. Game asset proof
- Confirm the exact installation: GTA V Legacy or Enhanced.
- Confirm deployment target: single-player or named multiplayer platform.
- Install a current Blender version and a compatible Sollumz release only after checking official requirements.
- Make a tiny original road/platform segment and simple building volume; export, inspect in CodeWalker, then perform a local in-game test.
- Record export logs, collision results and in-game evidence before expanding the scene.

## Suggested Blender scene organization

Use collections or equivalent groups with stable names:
- `00_Reference` — non-exporting image planes/notes, source URLs recorded separately.
- `01_Ground` — ground and terrain blockout.
- `02_Roads` — road surfaces, medians, curb geometry and junctions.
- `03_Plaza` — paved square, stairs/platforms, pedestrian routes.
- `04_Landmark` — original landmark blockout and refined mesh.
- `05_Building_Masses` — surrounding volumes, then facade modules.
- `06_Landscape` — trees, lawn, planting beds and irrigation/water feature geometry if referenced.
- `07_Street_Dressing` — lights, signs, benches, barriers and bins.
- `08_Vehicle_Dressing` — static vehicles only.
- `09_Collision_LOD` — collision and level-of-detail outputs required by the selected pipeline.

## Milestones and acceptance

1. **Coordinate and reference sheet:** chosen view bounds, a metric unit convention, a source register, and confidence labels.
2. **Greybox review:** the plaza, major road axis, sidewalks and 2–4 surrounding building masses are legible from above and street level.
3. **Asset-pipeline proof:** one original road piece and one simple building asset export and open in CodeWalker with recorded versions.
4. **Landmark and environment pass:** distinctive plaza/landmark silhouette, facade rhythms, trees and materials are modeled; no critical collision/scale warnings remain.
5. **In-game vertical slice:** exported scene loads in the selected edition/platform; record collisions, LODs, visibility and performance.
6. **Expansion decision:** only after the slice passes review, continue into adjacent streets and blocks.

## Boundaries

- This is a project proposal, not a claim that the city slice has already been built.
- The existing Map Agent streetlight is a tool smoke-test prop, not the scale/layout anchor for the city.
- Do not use coordinates copied from the fictional JSON planning prototype as GTA V world coordinates.
- Do not commit GTA V game archives, extracted game assets, credentials, or assets from other mods without redistribution rights.
- Static prop placement, custom geometry, drivable vehicles, and live traffic are distinct technical features and need separate validation.
