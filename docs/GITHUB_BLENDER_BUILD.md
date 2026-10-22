# Automatic Blender greybox build on GitHub

The GitHub Actions workflow **Build Blender greybox artifact** runs the original
tools/blender/create_istiklol_greybox.py script in headless Blender, saves an editable
.blend scene, renders a preview PNG, and writes a JSON manifest.

## How to watch and download the result

1. Open the repository on GitHub and choose **Actions**.
2. Open **Build Blender greybox artifact**.
3. Select the latest run for the current pull request or feature branch.
4. Wait for the run to finish. A green check means the headless build and output checks passed.
5. At the bottom of the run page, find **Artifacts** and download **Dushanbe-Istiklol-Greybox**.
6. Unzip it. The package contains:
   - **Dushanbe_Istiklol_Greybox.blend** — the editable Blender scene.
   - **Dushanbe_Istiklol_preview.png** — a rendered overview for quick inspection.
   - **greybox_manifest.json** — Blender version, object counts, collections, bounds, and explicit limitations.

You can also start a build manually: **Actions → Build Blender greybox artifact → Run workflow**.
A manual run builds the default branch; use the latest feature-branch/PR run to inspect
unmerged changes.

## What a successful build means

It means Blender opened the project script in background mode, created the expected
collections and enough mesh geometry, saved the .blend file, rendered a PNG, and
produced a valid manifest. CI does this automatically; it does not require Blender to
be open on your PC for the build itself.

It does **not** mean the model is a finished GTA V map. The output is still a schematic
greybox in illustrative metre-sized local coordinates. The workflow does not install or
invoke Sollumz, export YMAP/YDR/YBN files, place the map into your local GTA installation,
or prove compatibility with GTA V Legacy or GTA V Enhanced. Those remain later validation
steps. Preview-only camera and lighting are grouped under 99_Preview_Only.

## Source versus generated files

The Python build scripts and workflow are version-controlled. The binary .blend and
rendered PNG are uploaded as temporary GitHub Actions artifacts, not committed to the
repository. Artifacts are retained for 14 days by this workflow; rerun the workflow if
you need a fresh copy.
