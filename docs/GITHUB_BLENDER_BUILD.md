# Automatic Blender, OpenStreetMap, Sollumz and CodeWalker build

The GitHub Actions pipeline fetches a small OpenStreetMap extract around Istiklol Monument,
rebuilds the surrounding city geometry from mapped features, exports through Sollumz, and
converts the result with CodeWalker Core to GTA V Legacy / GEN8 binary resources.

## How to download the results

1. Open the repository on GitHub and select Actions.
2. Open the latest successful Build Blender greybox artifact run for this pull request.
3. Download Dushanbe-Istiklol-CitySlice-CWXML for the Blender source scene, preview, OSM extract, attribution, DDS textures and readable CWXML.
4. Download Dushanbe-Istiklol-GTA-V-Legacy-Native-Preview for CodeWalker-converted RSC7 resources and the native conversion manifest.

The native preview package includes seven YDR files plus one YTYP and one YMAP (nine resources).
The OSM source extract is packaged with the build artifacts and attributed to OpenStreetMap contributors.
Artifacts are retained for 14 days. No game files are installed on your PC automatically, and the
pull request stays unmerged until reviewed.

## What the pipeline builds

**OpenStreetMap + Blender:**
- Downloads an approximately 2 km district centered on the Istiklol Monument using Overpass.
- Uses the source road centerlines and generates metric road ribbons/sidewalks.
- Uses mapped building outlines and tagged heights/floor counts where available; makes facade walls and procedural window rows.
- Imports mapped plaza, green, water and tree features when available.
- Keeps the independently authored central landmark blockout visible as a temporary placeholder.
- Writes an editable .blend scene, a rendered overview and JSON manifests.

**Sollumz:**
- Installs official Sollumz 2.9.0.
- Runs a separate export smoke test on one original Drawable.
- Exports seven scene groups as YDR CWXML, plus a YTYP and YMAP.
- Validates the XML structures and DXT1 texture payloads.

**CodeWalker Core:**
- Checks out pinned CodeWalker source at commit 485d56bec00262ed7fa472261cce7bbc6202b96e.
- Converts the seven YDR XML files and the YTYP/YMAP through CodeWalker.
- Requires RSC7 headers and loads every generated binary resource back through CodeWalker.
- Uploads a package that includes seven YDRs, one YTYP and one YMAP.

## Accuracy: what is real and what is not yet exact

The street layout and building footprints now come from OpenStreetMap and are positioned in a
local metric frame with origin at 38.59124, 68.78162. This removes the arbitrary hand-positioned
road/building layout and gives the district a real spatial base.

This is still **not a photogrammetry scan or one-to-one facade reconstruction**. OSM has incomplete
height and facade attributes; missing building heights use estimates, and windows are procedural.
Some mapped building footprints may not include detailed roof forms. The Istiklol monument itself
remains a schematic placeholder because a reusable, openly licensed model of the exact current
monument was not found in this pass. Public model links and license notes are in
docs/REAL_WORLD_3D_ASSETS.md.

A successful build means CodeWalker can convert the assets and read them back. It does not mean
the map is ready to play or correctly placed in the GTA V world. These are still outstanding:
GTA V world-space transform, YBN collision assets, LOD/SLOD hierarchy, streaming review, target
installation package layout, in-game testing and validation of GTA V Legacy. Enhanced / GEN9 is
not tested. No proprietary Rockstar assets are included.

## Coordinate and licensing notes

The OSM extract uses bounds 38.58200, 68.77100 to 38.60050, 68.79250, anchored at 38.59124,
68.78162 for local coordinates. It includes data attribution and the ODbL 1.0 notice in
assets/osm/README.md; the full Overpass response is included under artifacts/osm in the build
artifact. See https://www.openstreetmap.org/copyright.

The output is a local-coordinate preview, not yet mapped to a verified GTA V world location.
OSM data is updated when a new workflow run fetches it. Generated scene/build outputs are
stored as Actions artifacts rather than committed as binary files to Git.
