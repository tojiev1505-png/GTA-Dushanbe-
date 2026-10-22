# GTA V tooling research notes

## Purpose

The project is now targeting a real, expandable Dushanbe-inspired city slice. Prop-placement tooling is useful for dressing, but cannot replace the need for custom road, plaza, terrain, and building geometry.

## Tool roles

### GTA V Map Agent + CodeWalker

- Upstream: https://github.com/cngil/gtav-mapagent
- Verified locally on 2026-10-22: editor launches, CodeWalker world and camera work, and a local Ollama `qwen3:4b` agent placed one existing streetlight prop.
- Use for inspection, existing-prop placement, collision/ground checks, and supported map exports.
- Do not treat it as a custom-city generator: it does not create original terrain, building models, or a complete replacement road network.
- Complex multi-object placement, map export, and in-game behavior remain to be verified.

### Blender + Sollumz — custom geometry

- Official upstream: https://github.com/Sollumz/Sollumz
- Sollumz is an open-source Blender add-on for GTA V assets and map work. The upstream documentation lists formats including YDR, YBN, YTYP, and YMAP support; the project announced a major YMAP workflow rework in August 2026.
- Use Blender for original building masses/facades, plaza surfaces, roads, sidewalks, terrain and unique landmark geometry.
- Version and edition compatibility must be verified before committing to an export format. Record Blender version, Sollumz commit/release, GTA V edition and CodeWalker version.
- Follow upstream documentation and notices; do not redistribute game assets.

## Key design constraints

- Keep source geometry, planning data, GTA V placement coordinates, exports and in-game evidence separate.
- Do not paste fictional local coordinates from `map-data/blocks/center_prototype.json` into GTA V world coordinates.
- A YMAP containing static objects is not, by itself, a fully functioning traffic system. Static parked vehicles may be feasible in a map; live traffic and drivable vehicles can require game scripts or separate systems.
- Large custom buildings need scale, materials/textures, collision, and suitable LODs. An imported mesh that looks right in Blender is not finished until it exports and is verified in game.
- Never place or commit Rockstar archives, extracted proprietary game assets, credentials, or unauthorized third-party mod assets in this repository.

## First slice proposal

The proposed slice is Istiklol Square and a short adjoining boulevard, with landmark massing, roads, sidewalks, landscaping, parked-vehicle placeholders, and several surrounding building volumes. A first editable Blender script is now at `tools/blender/create_istiklol_greybox.py`. It creates schematic geometry only; it has not yet been run in Blender, exported through Sollumz, or tested in game. Review it against sourced reference dimensions before treating any coordinates as meaningful.

Reference-source register and acceptance criteria are in `docs/CITY_SLICE_PLAN.md`.

## Current status

- Viewer and camera: verified locally on 2026-10-22.
- Local Qwen model and one prop placement: confirmed by the user on 2026-10-22.
- Blender/Sollumz installed and tested in this project: not yet confirmed.
- Custom geometry export, map export, and in-game behavior: not yet tested.
- Target GTA V edition and final deployment platform: not decided.
