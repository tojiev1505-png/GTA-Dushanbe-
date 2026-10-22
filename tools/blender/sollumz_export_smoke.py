"""Verify the smallest Sollumz -> CodeWalker XML drawable export in headless Blender.

This is a pipeline smoke test, not a city-map export and not an in-game test.
The output uses CodeWalker XML (CWXML), which must still be converted/imported by
the selected game toolchain before GTA V can consume it.
"""
from __future__ import annotations

import json
import os
import sys
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import bpy

OUTPUT_DIR = Path(
    os.environ.get("DUSHANBE_SOLLUMZ_OUTPUT", os.environ.get("DUSHANBE_SOLLUMZ_OUTPUT", "artifacts/sollumz-smoke"))
).resolve()
ADDON_MODULE = os.environ.get("DUSHANBE_SOLLUMZ_ADDON_MODULE", "Sollumz")


def clean_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in list(bpy.data.collections):
        if collection.name != bpy.context.scene.collection.name and collection.users == 0:
            bpy.data.collections.remove(collection)


def enable_sollumz():
    if not bpy.context.preferences.addons.get(ADDON_MODULE):
        result = bpy.ops.preferences.addon_enable(module=ADDON_MODULE)
        if "FINISHED" not in result:
            raise RuntimeError(f"Could not enable Sollumz addon {ADDON_MODULE}: {result}")
    addon = bpy.context.preferences.addons.get(ADDON_MODULE)
    if addon is None:
        raise RuntimeError(f"Sollumz addon {ADDON_MODULE!r} is not enabled")
    if not hasattr(bpy.ops.sollumz, "converttodrawable"):
        raise RuntimeError("Sollumz loaded without its Drawable conversion operator")
    if not hasattr(bpy.ops.sollumz, "export_assets"):
        raise RuntimeError("Sollumz loaded without its asset export operator")


def create_proof_drawable():
    # A tiny project-authored pad is sufficient to test the actual exporter.
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.25))
    obj = bpy.context.object
    obj.name = "Dushanbe_Export_Proof_Pad"
    obj.dimensions = (10.0, 10.0, 0.5)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Use a real Sollumz shader material, not only a viewport material.
    from Sollumz.ydr.shader_materials import create_shader

    material = create_shader("default.sps")
    obj.data.materials.clear()
    obj.data.materials.append(material)

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    result = bpy.ops.sollumz.converttodrawable()
    if "FINISHED" not in result:
        raise RuntimeError(f"Sollumz Convert to Drawable failed: {result}")

    drawable = bpy.data.objects.get("Dushanbe_Export_Proof_Pad")
    if drawable is None or drawable.sollum_type != "sollumz_drawable":
        candidates = [
            o for o in bpy.data.objects
            if getattr(o, "sollum_type", "") == "sollumz_drawable"
            and "Dushanbe_Export_Proof_Pad" in o.name
        ]
        drawable = candidates[0] if candidates else None
    if drawable is None:
        detail = [(o.name, str(getattr(o, "sollum_type", "")), o.type) for o in bpy.data.objects]
        raise RuntimeError(f"Drawable root not found after conversion: {detail}")

    bpy.ops.object.select_all(action="DESELECT")
    drawable.select_set(True)
    bpy.context.view_layer.objects.active = drawable
    return drawable


def run_export(drawable):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    result = bpy.ops.sollumz.export_assets(
        directory=str(OUTPUT_DIR),
        direct_export=True,
        use_custom_settings=True,
        target_formats={"CWXML"},
        target_versions={"GEN8"},
        limit_to_selected=True,
    )
    if "FINISHED" not in result:
        raise RuntimeError(f"Sollumz CWXML export did not finish: {result}")

    expected = OUTPUT_DIR / "dushanbe_export_proof_pad.ydr.xml"
    if not expected.is_file():
        candidates = sorted(OUTPUT_DIR.glob("*.ydr.xml"))
        if len(candidates) == 1:
            expected = candidates[0]
        else:
            listing = [str(p.name) for p in OUTPUT_DIR.rglob("*") if p.is_file()]
            raise RuntimeError(
                "Expected a drawable CWXML file (*.ydr.xml), but export did not create one. "
                f"Files: {listing}"
            )
    tree = ET.parse(expected)
    root = tree.getroot()
    geometry_count = len(root.findall("./DrawableModelsHigh/Item/Geometries/Item"))
    shader_count = len(root.findall("./ShaderGroup/Shaders/Item"))
    if geometry_count < 1:
        raise RuntimeError(f"Exported XML contains no HIGH-LOD drawable geometry: {expected}")
    if shader_count < 1:
        raise RuntimeError(f"Exported XML contains no shader definitions: {expected}")

    manifest = {
        "schema_version": 1,
        "project": "GTA-Dushanbe",
        "status": "sollumz_cwxml_drawable_export_smoke_test_passed",
        "game_ready": False,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "blender_version": bpy.app.version_string,
        "sollumz_module": ADDON_MODULE,
        "export_format": "CodeWalker XML (CWXML)",
        "target_game_version": "GEN8 (GTA V Legacy)",
        "asset_type": "YDR drawable",
        "output_file": expected.name,
        "xml_root": root.tag,
        "drawable_geometry_count": geometry_count,
        "shader_count": shader_count,
        "drawable_object": drawable.name,
        "limitations": [
            "This is a tiny original test pad, not the Dushanbe city scene.",
            "CWXML is an intermediate readable format, not the final binary game asset.",
            "The XML still needs conversion/validation in the selected GTA V toolchain.",
            "No YMAP placement, YTYP archetype, collision asset, LOD pipeline, or in-game load is tested.",
            "The export target is GEN8 (GTA V Legacy); GEN9 (Enhanced) is not tested here.",
        ],
    }
    manifest_path = OUTPUT_DIR / "sollumz_export_smoke_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("DUSHANBE_SOLLUMZ_EXPORT_SMOKE_OK")
    print(f"Blender: {bpy.app.version_string}")
    print(f"XML: {expected}")
    print(f"Geometry items: {geometry_count}; shader items: {shader_count}")
    print(f"Manifest: {manifest_path}")
    print("NOT GAME-READY: CodeWalker conversion and a local in-game test are not performed.")


def main():
    print(f"Python: {sys.version}")
    clean_scene()
    enable_sollumz()
    drawable = create_proof_drawable()
    run_export(drawable)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise
