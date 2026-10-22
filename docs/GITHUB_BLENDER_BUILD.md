# Automatic Blender build and Sollumz export proof on GitHub

The GitHub Actions workflow **Build Blender greybox artifact** runs the city-slice scripts
in headless Blender, saves an editable .blend scene, renders a preview PNG, writes a JSON
manifest, and runs a second pipeline smoke test with the official Sollumz release.

## How to watch and download the result

1. Open the repository on GitHub and choose **Actions**.
2. Open **Build Blender greybox artifact**.
3. Select the latest run for the current pull request or feature branch.
4. Open the run to inspect each step and its logs. A green check means the geometry build,
   artifact validation, Sollumz install, XML export test, and output checks passed.
5. At the bottom of the run page, download **Dushanbe-Istiklol-Greybox-and-Sollumz-proof**.
6. Unzip it. A successful run contains:
   - **Dushanbe_Istiklol_Greybox.blend** — the editable Blender city-slice scene.
   - **Dushanbe_Istiklol_preview.png** — a rendered overview for quick inspection.
   - **greybox_manifest.json** — Blender version, object counts, collections, bounds, and limitations.
   - **sollumz-smoke/dushanbe_export_proof_pad.ydr.xml** — a tiny test Drawable exported by Sollumz as CodeWalker XML.
   - **sollumz-smoke/sollumz_export_smoke_manifest.json** — reports the exporter and XML structure checks.

You can also start a build manually: **Actions → Build Blender greybox artifact → Run workflow**.
A manual run builds the default branch; use the latest feature-branch/PR run to inspect
unmerged changes.

## What a successful build means

The first phase opens the project scripts in background Blender, creates the base and
detail collections, validates a minimum of 250 mesh objects, saves the .blend, renders
a PNG, and checks the scene manifest.

The second phase downloads the official Sollumz 2.9.0 release, enables it in a clean
background Blender process, creates a small original test pad, converts it to a Sollumz
Drawable, exports it to CodeWalker XML (CWXML) for **GEN8 / GTA V Legacy**, then parses
the XML and checks that it contains mesh geometry and shader definitions.

The smoke test proves that this specific exporter path can produce a structurally
plausible YDR XML file. It does **not** convert CWXML to the game's binary asset formats,
create a complete YMAP/YTYP city package, install assets into a local GTA V copy, or
prove compatibility/playability in GTA V Legacy or Enhanced. A successful build is
not the same as a playable map.

## Scene and asset boundaries

All city-slice measurements are schematic assumptions in local metre-sized units. They
are not surveyed Dushanbe dimensions and are not GTA V world coordinates. Vehicles,
street lights, windows, and furnishings in the greybox are custom static placeholders,
not functional traffic or final game assets.

YDR CWXML is an intermediate readable format. CodeWalker conversion/import, archetype
registration, map placement, collision setup, edition-specific packaging, and in-game
validation are separate future stages. The current smoke test targets GEN8 only.

## Source versus generated files

The Python scripts and workflow are version-controlled. Generated .blend, PNG, manifests,
and smoke-test XML are temporary GitHub Actions artifacts, not committed to the source
repository. Artifacts are retained for 14 days; run the workflow again for a fresh copy.
