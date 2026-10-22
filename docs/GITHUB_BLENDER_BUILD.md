# Automatic Blender build and Sollumz city export on GitHub

The GitHub Actions workflow **Build Blender greybox artifact** runs the city-slice scripts
in headless Blender, saves an editable scene, renders a preview, then uses the official
Sollumz release to exercise the custom-asset export pipeline.

## How to watch and download the result

1. Open the repository on GitHub and choose **Actions**.
2. Open **Build Blender greybox artifact**.
3. Select the latest run for the current pull request or feature branch.
4. Open the run to inspect individual steps and logs.
5. At the bottom of a completed run, download **Dushanbe-Istiklol-CitySlice-CWXML**.
6. Unzip it. A successful run contains:
   - **Dushanbe_Istiklol_Greybox.blend** — the editable city-slice source scene.
   - **Dushanbe_Istiklol_preview.png** — a rendered scene overview.
   - **greybox_manifest.json** — Blender version, object counts, collections, bounds, and limits.
   - **sollumz-smoke/** — the small exporter pipeline test with one original test Drawable.
   - **city-export/Dushanbe_Istiklol_Sollumz_Prepared.blend** — a copy prepared with Sollumz shaders, drawable roots, YTYP archetypes and YMAP data.
   - **city-export/*.ydr.xml** — one CWXML drawable export for each of the nine main scene collections.
   - **city-export/*.ytyp.xml** — a YTYP with archetypes for the custom drawables.
   - **city-export/*.ymap.xml** — a YMAP with the nine drawable placements.
   - **city-export/textures/*.dds** — small original, solid-colour test textures used to exercise the shader/texture path.
   - **city-export/city_slice_export_manifest.json** — export counts, Blender/Sollumz versions, target, and limitations.

A manual build can be started through **Actions → Build Blender greybox artifact → Run workflow**.
To inspect the unmerged branch, use the run tied to the current pull request, not a run on main.

## What a successful build means

The first stage creates the illustrative geometry, validates a minimum of 250 mesh objects,
saves the .blend, renders a PNG, and checks the scene manifest.

The next stage downloads official Sollumz 2.9.0 and verifies that it can export a tiny
original test Drawable as CodeWalker XML. The city-export stage then attempts to convert
the nine main scene collections to separate Drawables, creates a YTYP with matching archetypes,
creates a YMAP with matching entities, writes simple original solid-colour DDS textures, exports
the assets as CWXML for **GEN8 / GTA V Legacy**, and parses the exported XML to check that
geometry, archetypes, and map entities are present.

This is an export-pipeline build, not a playable game mod. CodeWalker still needs to convert
or import the readable CWXML into the game's native asset format. GTA V world-coordinate
placement, collision YBNs, a proper LOD/SLOD hierarchy, streaming boundaries, and an in-game
test are still outstanding. GTA V Enhanced / GEN9 is not tested by this workflow. No game
binaries or extracted proprietary game assets are included.

## Scene and asset boundaries

All city-slice measurements are schematic assumptions in local metre-sized units. They are
not surveyed Dushanbe measurements and are not GTA V world coordinates. The monument and
surrounding buildings are still blockout geometry. Cars, lamps, traffic signals, windows and
furnishings are original static placeholders, not functional traffic or lighting systems.
The generated DDS files are only flat-colour placeholders, not final material textures.

## Source versus generated files

Python scripts and the workflow are version-controlled. Generated .blend, PNG, manifests,
DDS textures and CWXML output are stored in temporary GitHub Actions artifacts, not committed
as binary outputs into the source repository. Artifacts are retained for 14 days; rerun the
workflow if you need a fresh copy.
