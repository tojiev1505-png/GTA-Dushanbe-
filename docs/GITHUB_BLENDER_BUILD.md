# Automatic Blender, Sollumz and CodeWalker build on GitHub

The GitHub Actions workflow **Build Blender greybox artifact** builds the city slice in
headless Blender, runs the official Sollumz exporter, validates the CodeWalker XML, and
then runs a separate Windows job against a pinned CodeWalker Core revision to create and
read back GTA V Legacy / GEN8 binary resources.

## How to watch and download results

1. Open the repository on GitHub and choose **Actions**.
2. Open **Build Blender greybox artifact**.
3. Select the latest run for the current pull request.
4. Open the run to inspect each step and its logs.
5. A successful workflow produces two downloadable artifacts:
   - **Dushanbe-Istiklol-CitySlice-CWXML** — editable Blender scene, render, manifest, DDS textures, and readable CWXML source assets.
   - **Dushanbe-Istiklol-GTA-V-Legacy-Native-Preview** — CodeWalker-converted RSC7 resource files and a manifest after CodeWalker successfully reads each binary asset back.

The native preview package is retained by GitHub Actions for 14 days. No game files are installed
on your PC automatically, and the PR stays unmerged until reviewed.

## What the pipeline checks

**Blender/Sollumz stage:**
- Creates the schematic city slice and validates the scene object/collection counts.
- Renders a preview.
- Installs official Sollumz 2.9.0 in the temporary runner.
- Exports one small original test Drawable as a smoke test.
- Exports nine main scene collections to YDR CWXML, plus one YTYP with nine archetypes and one YMAP with nine entities.
- Validates that generated DDS swatches use actual DXT1 blocks matching the material declaration.

**CodeWalker binary stage:**
- Checks out pinned CodeWalker Core source at commit 485d56bec00262ed7fa472261cce7bbc6202b96e.
- Converts the nine YDR XML files and the YTYP/YMAP XML through CodeWalker.
- Requires each resulting file to carry the RSC7 resource header.
- Loads each binary YDR, YTYP and YMAP back through CodeWalker and checks the drawable, archetype and entity counts.
- Saves files under native-gen8/stream/ inside the binary preview artifact.

A successful conversion/readback means CodeWalker produced plausible native-format GEN8 resources
that it can read again. It does **not** mean the map is ready to play or correctly positioned in
the game world.

## Known limitations

All scene dimensions are schematic local metre-sized coordinates, not surveyed Dushanbe data
and not GTA V world coordinates. The map positions are intentionally local; they have not been
transformed to an identified coordinate within GTA V's world.

The monument and surrounding buildings remain blockout geometry. Cars, lamps, traffic signals,
windows and furnishings are static placeholders, not functioning traffic or lighting systems.
DDS swatches are flat-colour placeholders, not final art textures.

Collision YBNs, a proper LOD/SLOD hierarchy, streaming boundary review, CodeWalker viewport
inspection, a target installation/package layout, and an in-game test are still outstanding.
Only GTA V Legacy / GEN8 is targeted in this pipeline; GTA V Enhanced / GEN9 has not been tested.
No Rockstar game files or extracted proprietary assets are committed or included.

## Generated files

Python and C# source, workflow definitions and documentation are version-controlled. Generated
.blend, PNG, JSON manifests, DDS textures, CWXML files and native binary assets are stored as
temporary GitHub Actions artifacts rather than committed to Git. Re-run the workflow to produce
a fresh artifact after its 14-day retention period expires.
