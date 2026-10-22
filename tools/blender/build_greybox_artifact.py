"""Build and package the Istiklol greybox in headless Blender for GitHub Actions.

This script invokes create_istiklol_greybox.py, saves an editable .blend file,
renders a preview PNG, and writes a small JSON manifest. It intentionally does
not export GTA V YMAP/YDR assets or claim in-game readiness.
"""
from __future__ import annotations

import json
import os
import runpy
from datetime import datetime, timezone
from pathlib import Path

import bpy
from mathutils import Vector

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_SCRIPT = REPO_ROOT / "tools" / "blender" / "create_istiklol_greybox.py"
DETAIL_SCRIPT = REPO_ROOT / "tools" / "blender" / "add_city_details.py"
OUTPUT_DIR = Path(os.environ.get("DUSHANBE_BUILD_OUTPUT", REPO_ROOT / "artifacts")).resolve()
ROOT_NAME = "Dushanbe_Istiklol_Greybox"
REQUIRED_COLLECTIONS = (
    "00_Ground",
    "01_Roads",
    "02_Plaza",
    "03_Landmark_Blockout",
    "04_Building_Masses",
    "05_Landscape",
    "06_Vehicle_Proxies",
    "07_Facade_Detail",
    "08_Street_Furniture",
)


def add_preview_rig(scene):
    """Add a named camera and sun in a collection excluded from map geometry."""
    preview = bpy.data.collections.get("99_Preview_Only")
    if preview is None:
        preview = bpy.data.collections.new("99_Preview_Only")
        scene.collection.children.link(preview)

    camera_data = bpy.data.cameras.new("Dushanbe_Preview_Camera_Data")
    camera = bpy.data.objects.new("Dushanbe_Preview_Camera", camera_data)
    preview.objects.link(camera)
    camera["dushanbe_preview_only"] = True
    camera.location = (300.0, -360.0, 310.0)
    target = Vector((0.0, 0.0, 4.0))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.lens = 35.0
    camera_data.clip_end = 1500.0
    scene.camera = camera

    light_data = bpy.data.lights.new("Dushanbe_Preview_Sun_Data", type="SUN")
    light_data.energy = 3.0
    if hasattr(light_data, "angle"):
        light_data.angle = 0.18
    light = bpy.data.objects.new("Dushanbe_Preview_Sun", light_data)
    preview.objects.link(light)
    light["dushanbe_preview_only"] = True
    light.rotation_euler = (0.35, -0.25, -0.45)

    world = scene.world
    if world is None:
        world = bpy.data.worlds.new("Dushanbe_Preview_World")
        scene.world = world
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background") if world.node_tree else None
    if background:
        background.inputs["Color"].default_value = (0.15, 0.17, 0.20, 1.0)
        background.inputs["Strength"].default_value = 0.8


def validate_and_describe_scene():
    root = bpy.data.collections.get(ROOT_NAME)
    if root is None:
        raise RuntimeError(f"Expected collection {ROOT_NAME!r} was not created")

    child_names = {collection.name for collection in root.children}
    missing = [name for name in REQUIRED_COLLECTIONS if name not in child_names]
    if missing:
        raise RuntimeError("Greybox is missing required collections: " + ", ".join(missing))

    objects = list(root.all_objects)
    meshes = [obj for obj in objects if obj.type == "MESH"]
    if len(meshes) < 50:
        raise RuntimeError(f"Greybox looks incomplete: expected >= 50 mesh objects, found {len(meshes)}")

    material_names = sorted({
        slot.material.name
        for obj in meshes
        for slot in obj.material_slots
        if slot.material is not None
    })
    corners = [
        obj.matrix_world @ Vector(corner)
        for obj in meshes
        for corner in obj.bound_box
    ]
    if not corners:
        raise RuntimeError("No mesh bounds found")

    bounds = {
        "min": [round(min(getattr(p, axis) for p in corners), 3) for axis in ("x", "y", "z")],
        "max": [round(max(getattr(p, axis) for p in corners), 3) for axis in ("x", "y", "z")],
    }
    counts = {
        collection.name: len(collection.objects)
        for collection in root.children
    }
    return {
        "schema_version": 1,
        "project": "GTA-Dushanbe",
        "scene": ROOT_NAME,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "blender_version": bpy.app.version_string,
        "status": "schematic_greybox_built_with_detail_pass",
        "game_ready": False,
        "units": "metres (illustrative local design units only)",
        "coordinate_status": "not surveyed; not GTA V world coordinates",
        "objects": len(objects),
        "mesh_objects": len(meshes),
        "materials": material_names,
        "collection_object_counts": counts,
        "bounds_metres_illustrative": bounds,
        "preview_only_collection": "99_Preview_Only",
        "outputs": [
            "Dushanbe_Istiklol_Greybox.blend",
            "Dushanbe_Istiklol_preview.png",
            "greybox_manifest.json",
        ],
        "limitations": [
            "All dimensions are schematic assumptions, not surveyed Dushanbe measurements.",
            "This build does not perform Sollumz export to YMAP/YDR/YBN.",
            "This build has not been tested in GTA V Legacy or GTA V Enhanced.",
            "Preview camera and light are for inspection only, not map assets.",
            "Vehicle shapes are non-functional visual placeholders, not drivable GTA vehicles.",
            "Street lights, signals, benches, shopfronts and windows are schematic mesh details only.",
        ],
    }


def main():
    if not SOURCE_SCRIPT.is_file():
        raise FileNotFoundError(f"Greybox source script was not found: {SOURCE_SCRIPT}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not DETAIL_SCRIPT.is_file():
        raise FileNotFoundError(f"City detail script was not found: {DETAIL_SCRIPT}")

    # Generate the base scene, then add architectural/urban detail in a second pass.
    runpy.run_path(str(SOURCE_SCRIPT), run_name="__main__")
    runpy.run_path(str(DETAIL_SCRIPT), run_name="__main__")

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "METERS"
    scene.unit_settings.scale_length = 1.0

    add_preview_rig(scene)
    manifest = validate_and_describe_scene()

    blend_path = OUTPUT_DIR / "Dushanbe_Istiklol_Greybox.blend"
    preview_path = OUTPUT_DIR / "Dushanbe_Istiklol_preview.png"
    manifest_path = OUTPUT_DIR / "greybox_manifest.json"

    available_engines = {
        item.identifier
        for item in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items
    }
    scene.render.engine = (
        "BLENDER_EEVEE_NEXT"
        if "BLENDER_EEVEE_NEXT" in available_engines
        else "BLENDER_EEVEE"
    )
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 70
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.filepath = str(preview_path)
    scene.render.film_transparent = False

    # Save the editable scene before rendering the preview.
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    with manifest_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    bpy.ops.render.render(write_still=True)

    for path in (blend_path, preview_path, manifest_path):
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Expected build output is missing or empty: {path}")

    print("DUSHANBE_GREYBOX_BUILD_OK")
    print(f"Blender version: {bpy.app.version_string}")
    print(f"Objects: {manifest['objects']} total; {manifest['mesh_objects']} meshes")
    print(f"Editable scene: {blend_path}")
    print(f"Preview image: {preview_path}")
    print(f"Manifest: {manifest_path}")
    print("NOT GAME-READY: Sollumz export and in-game validation are separate steps.")


if __name__ == "__main__":
    main()
