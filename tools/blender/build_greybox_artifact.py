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
OSM_SCRIPT = REPO_ROOT / "tools" / "blender" / "import_osm_city_slice.py"
MONUMENT_SCRIPT = REPO_ROOT / "tools" / "blender" / "build_istiklol_monument.py"
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
    # The imported OSM district is roughly 2 km wide; use a wide overview camera.
    camera.location = (1800.0, -2100.0, 1650.0)
    target = Vector((0.0, 0.0, 0.0))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.lens = 35.0
    camera_data.clip_end = 6000.0
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
    if len(meshes) < 250:
        raise RuntimeError(f"Greybox looks incomplete: expected >= 250 mesh objects, found {len(meshes)}")

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
        "status": "osm_geospatial_city_slice_built",
        "game_ready": False,
        "units": "metres (illustrative local design units only)",
        "coordinate_status": "OSM local metric projection anchored at Istiklol Monument; not GTA V world coordinates",
        "monument": {
            "model_type": bpy.context.scene.get("dushanbe_monument_model_type", "not generated"),
            "target_overall_height_m": float(bpy.context.scene.get("dushanbe_monument_target_height_m", 0.0)),
            "lower_architectural_section_m": float(bpy.context.scene.get("dushanbe_monument_lower_section_m", 0.0)),
            "gate_count": int(bpy.context.scene.get("dushanbe_monument_gate_count", 0)),
            "mesh_objects": int(bpy.context.scene.get("dushanbe_monument_mesh_objects", 0)),
            "accuracy_note": "Original procedural reference-based model, not photogrammetry; small ornament and materials remain approximate.",
        },
        "osm_data": {
            "imported": bool(bpy.context.scene.get("dushanbe_osm_imported", False)),
            "source": bpy.context.scene.get("dushanbe_osm_source", "not imported"),
            "fetched_utc": bpy.context.scene.get("dushanbe_osm_fetched_utc", "unknown"),
            "building_count": int(bpy.context.scene.get("dushanbe_osm_buildings", 0)),
            "procedural_facade_window_count": int(bpy.context.scene.get("dushanbe_osm_windows", 0)),
            "road_way_count": int(bpy.context.scene.get("dushanbe_osm_road_ways", 0)),
            "road_segment_count": int(bpy.context.scene.get("dushanbe_osm_road_segments", 0)),
            "green_area_count": int(bpy.context.scene.get("dushanbe_osm_green_areas", 0)),
            "plaza_polygon_count": int(bpy.context.scene.get("dushanbe_osm_plaza_polygons", 0)),
            "water_area_count": int(bpy.context.scene.get("dushanbe_osm_water_areas", 0)),
            "mapped_tree_count": int(bpy.context.scene.get("dushanbe_osm_mapped_trees", 0)),
            "bbox_south_west_north_east": list(bpy.context.scene.get("dushanbe_osm_bbox", [])),
        },
        "objects": len(objects),
        "mesh_objects": len(meshes),
        "materials": material_names,
        "collection_object_counts": counts,
        "bounds_metres_illustrative": bounds,
        "preview_only_collection": "99_Preview_Only",
        "outputs": [
            "Dushanbe_Istiklol_Greybox.blend",
            "Dushanbe_Istiklol_preview.png",
            "Dushanbe_Istiklol_monument_closeup.png",
            "greybox_manifest.json",
        ],
        "limitations": [
            "All dimensions are schematic assumptions, not surveyed Dushanbe measurements.",
            "OSM building heights, roof shapes and facade windows are approximate when not tagged in the source data.",
            "This is not photogrammetry and does not reproduce every facade one-to-one.",
            "This build does not perform Sollumz export to YMAP/YDR/YBN.",
            "This build has not been tested in GTA V Legacy or GTA V Enhanced.",
            "Preview camera and light are for inspection only, not map assets.",
            "The Istiklol monument uses published 121 m / 30 m dimensions and a procedural architectural reconstruction; fine ornament is approximate, not photogrammetry.",
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
    if not MONUMENT_SCRIPT.is_file():
        raise FileNotFoundError(f"Detailed Istiklol monument script was not found: {MONUMENT_SCRIPT}")

    # Generate the base scene, add second-pass details, then replace placeholder masses
    # with georeferenced building footprints and road geometry from the OSM extract.
    osm_path = Path(os.environ.get("DUSHANBE_OSM_JSON", REPO_ROOT / "artifacts" / "osm" / "istiklol_slice.json")).resolve()
    if not osm_path.is_file():
        raise FileNotFoundError(f"OSM extract is missing: {osm_path}. Run tools/osm/fetch_dushanbe_slice.py first.")
    os.environ["DUSHANBE_OSM_JSON"] = str(osm_path)
    runpy.run_path(str(SOURCE_SCRIPT), run_name="__main__")
    runpy.run_path(str(DETAIL_SCRIPT), run_name="__main__")
    runpy.run_path(str(OSM_SCRIPT), run_name="__main__")
    runpy.run_path(str(MONUMENT_SCRIPT), run_name="__main__")

    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "METERS"
    scene.unit_settings.scale_length = 1.0

    add_preview_rig(scene)
    manifest = validate_and_describe_scene()

    blend_path = OUTPUT_DIR / "Dushanbe_Istiklol_Greybox.blend"
    preview_path = OUTPUT_DIR / "Dushanbe_Istiklol_preview.png"
    monument_preview_path = OUTPUT_DIR / "Dushanbe_Istiklol_monument_closeup.png"
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

    # Full-district overview uses the wide camera saved into the .blend file.
    overview_location = scene.camera.location.copy()
    overview_rotation = scene.camera.rotation_euler.copy()
    overview_lens = scene.camera.data.lens
    overview_clip = scene.camera.data.clip_end
    bpy.ops.render.render(write_still=True)

    # A separate closeup makes the 121 m landmark legible instead of a tiny pin
    # in the 2 km district overview. Keep the editable .blend's camera on overview.
    scene.camera.location = (200.0, -310.0, 170.0)
    closeup_target = Vector((0.0, 0.0, 58.0))
    scene.camera.rotation_euler = (closeup_target - scene.camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera.data.lens = 50.0
    scene.camera.data.clip_end = 1200.0
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.resolution_percentage = 75
    scene.render.filepath = str(monument_preview_path)
    bpy.ops.render.render(write_still=True)

    scene.camera.location = overview_location
    scene.camera.rotation_euler = overview_rotation
    scene.camera.data.lens = overview_lens
    scene.camera.data.clip_end = overview_clip
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 70
    scene.render.filepath = str(preview_path)

    for path in (blend_path, preview_path, monument_preview_path, manifest_path):
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"Expected build output is missing or empty: {path}")

    print("DUSHANBE_GREYBOX_BUILD_OK")
    print(f"Blender version: {bpy.app.version_string}")
    print(f"Objects: {manifest['objects']} total; {manifest['mesh_objects']} meshes")
    print(f"Editable scene: {blend_path}")
    print(f"District overview: {preview_path}")
    print(f"Monument closeup: {monument_preview_path}")
    print(f"Manifest: {manifest_path}")
    print("NOT GAME-READY: Sollumz export and in-game validation are separate steps.")


if __name__ == "__main__":
    main()
