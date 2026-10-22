"""Prepare the Dushanbe Istiklol greybox for a first Sollumz CWXML city-slice export.

Builds one Drawable (YDR XML) per authored scene collection, one YTYP that defines
those drawables as archetypes, and one YMAP with entities placed in the schematic
local coordinate system. This is an export-pipeline prototype, NOT a game-ready mod.

Requires official Sollumz installed and enabled in Blender.
"""
from __future__ import annotations

import json
import os
import re
import struct
import sys
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import bpy

ADDON_MODULE = os.environ.get("DUSHANBE_SOLLUMZ_ADDON_MODULE", "Sollumz")
INPUT_BLEND = Path(
    os.environ.get("DUSHANBE_INPUT_BLEND", "artifacts/Dushanbe_Istiklol_Greybox.blend")
).resolve()
OUTPUT_DIR = Path(
    os.environ.get("DUSHANBE_CITY_EXPORT_OUTPUT", "artifacts/city-export")
).resolve()
ROOT_NAME = "Dushanbe_Istiklol_Greybox"
SCENE_COLLECTIONS = (
    ("00_Ground", "dsh_00_ground"),
    ("01_Roads", "dsh_01_roads"),
    ("02_Plaza", "dsh_02_plaza"),
    ("03_Landmark_Blockout", "dsh_03_landmark"),
    ("04_Building_Masses", "dsh_04_buildings"),
    ("05_Landscape", "dsh_05_landscape"),
    ("06_Vehicle_Proxies", "dsh_06_vehicles"),
    ("07_Facade_Detail", "dsh_07_facades"),
    ("08_Street_Furniture", "dsh_08_furniture"),
)
YMAP_NAME = "dushanbe_istiklol"
YTYP_NAME = "dushanbe_istiklol"


def require_addon():
    if not bpy.context.preferences.addons.get(ADDON_MODULE):
        result = bpy.ops.preferences.addon_enable(module=ADDON_MODULE)
        if "FINISHED" not in result:
            raise RuntimeError(f"Could not enable Sollumz addon {ADDON_MODULE}: {result}")
    if not bpy.context.preferences.addons.get(ADDON_MODULE):
        raise RuntimeError(f"Sollumz addon {ADDON_MODULE!r} is not enabled")
    if not hasattr(bpy.ops.sollumz, "export_assets"):
        raise RuntimeError("Sollumz export operator is unavailable")


def dds_rgba_solid(width: int, height: int, rgba: tuple[int, int, int, int]) -> bytes:
    """Return a valid opaque DXT1 DDS. Sollumz declares these swatches as D3DFMT_DXT1."""
    if width <= 0 or height <= 0:
        raise ValueError("DDS dimensions must be positive")

    # Encode the solid colour as RGB565. Equal DXT1 endpoints with zero selectors
    # make every texel use colour 0 and remain opaque.
    red, green, blue, _alpha = rgba
    red5 = round(max(0, min(255, red)) * 31 / 255)
    green6 = round(max(0, min(255, green)) * 63 / 255)
    blue5 = round(max(0, min(255, blue)) * 31 / 255)
    colour565 = (red5 << 11) | (green6 << 5) | blue5
    block = struct.pack("<HHI", colour565, colour565, 0)

    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4
    linear_size = blocks_x * blocks_y * 8

    # DDS_HEADER.dwFlags = CAPS | HEIGHT | WIDTH | PIXELFORMAT | LINEARSIZE.
    header = struct.pack(
        "<7I",
        124,           # DDS_HEADER.dwSize
        0x00081007,    # dwFlags
        height,
        width,
        linear_size,
        0,              # dwDepth
        1,              # dwMipMapCount
    )
    header += struct.pack("<11I", *([0] * 11))
    header += struct.pack(
        "<8I",
        32,             # DDS_PIXELFORMAT.dwSize
        0x4,            # DDPF_FOURCC
        0x31545844,     # 'DXT1' in little-endian
        0, 0, 0, 0, 0, # no RGB masks when FourCC is used
    )
    header += struct.pack("<5I", 0x1000, 0, 0, 0, 0)  # DDSCAPS_TEXTURE

    payload = block * (blocks_x * blocks_y)
    result = b"DDS " + header + payload
    if len(result) != 128 + linear_size:
        raise RuntimeError("Internal error while writing DXT1 DDS")
    return result

def safe_resource_name(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_]+", "_", value.strip()).strip("_").lower()
    if not value:
        value = "dsh_material"
    if value[0].isdigit():
        value = "dsh_" + value
    return value[:60]


def write_material_dds(material_name: str, rgba_float: tuple[float, float, float, float], texture_dir: Path) -> tuple[str, Path]:
    texture_name = safe_resource_name(material_name.replace("DushanbeGreybox_", "dsh_"))
    # Unique resource names are needed in GTA's texture namespace.
    rgba = tuple(max(0, min(255, round(component * 255))) for component in rgba_float)
    texture_path = texture_dir / f"{texture_name}.dds"
    texture_path.write_bytes(dds_rgba_solid(4, 4, rgba))
    return texture_name, texture_path


def get_or_make_sollumz_material(material, texture_dir: Path, created_textures: dict[str, str]):
    from Sollumz.ydr.shader_materials import create_shader

    if material.name not in created_textures:
        original_colour = tuple(material.diffuse_color)
        material = create_shader("default.sps", in_place_material=material)
        tex_name, tex_path = write_material_dds(material.name, original_colour, texture_dir)
        node = material.node_tree.nodes.get("DiffuseSampler")
        if node is None:
            raise RuntimeError(f"Sollumz default shader has no DiffuseSampler: {material.name}")
        image = bpy.data.images.new(f"{tex_name}_image", width=4, height=4, alpha=True)
        # The DDS has uniform pixels; the generated image provides a viewport swatch.
        image.pixels.foreach_set(list(original_colour) * 16)
        # Use a blend-relative path so the prepared .blend can be moved together with its textures.
        relative_texture_path = Path("textures") / tex_path.name
        image.filepath = "//" + relative_texture_path.as_posix()
        node.image = image
        # Sollumz exposes this as a read-only property derived from image.filepath.
        # The filename stem above therefore supplies the exported GTA texture name.
        node.texture_properties.embedded = True
        created_textures[material.name] = tex_name
    return material


def ensure_vertex_attributes(mesh, colour):
    """Create required Sollumz UV/color attributes for every mesh used by the YDR exporter."""
    if "UVMap 0" not in mesh.uv_layers:
        uv_layer = mesh.uv_layers.new(name="UVMap 0")
        for datum in uv_layer.data:
            datum.uv = (0.0, 0.0)
    if "Color 1" not in mesh.color_attributes:
        color_layer = mesh.color_attributes.new(
            name="Color 1", type="BYTE_COLOR", domain="CORNER"
        )
        for datum in color_layer.data:
            datum.color_srgb = colour


def configure_materials_and_meshes(collections, texture_dir: Path):
    created_textures: dict[str, str] = {}
    material_count = 0
    mesh_count = 0

    # Snapshot material colours before the Sollumz shader setup replaces node trees.
    material_colours = {}
    for collection in collections:
        for obj in collection.all_objects:
            if obj.type != "MESH":
                continue
            for material in obj.data.materials:
                if material is not None and material.name not in material_colours:
                    material_colours[material.name] = tuple(material.diffuse_color)

    for collection in collections:
        for obj in list(collection.all_objects):
            if obj.type != "MESH":
                continue
            if not obj.data.materials or all(mat is None for mat in obj.data.materials):
                fallback = bpy.data.materials.get("DushanbeGreybox_Ground")
                if fallback is None:
                    fallback = bpy.data.materials.new("DushanbeGreybox_Fallback")
                    fallback.diffuse_color = (0.55, 0.55, 0.55, 1.0)
                obj.data.materials.clear()
                obj.data.materials.append(fallback)

            # Preserve every original material slot, but convert its material datablock to a GTA shader.
            for slot_index, old_material in enumerate(list(obj.data.materials)):
                if old_material is None:
                    continue
                if old_material.name not in created_textures:
                    original_name = old_material.name
                    original_colour = material_colours.get(original_name, tuple(old_material.diffuse_color))
                    converted = get_or_make_sollumz_material(old_material, texture_dir, created_textures)
                    # Map original material name to converted texture resource (the datablock is modified in-place).
                    created_textures.setdefault(original_name, created_textures.get(converted.name, ""))
                else:
                    # The original material has already been converted in-place.
                    get_or_make_sollumz_material(old_material, texture_dir, created_textures)

            first_material = next((m for m in obj.data.materials if m), None)
            colour = material_colours.get(first_material.name, (0.8, 0.8, 0.8, 1.0)) if first_material else (0.8, 0.8, 0.8, 1.0)
            ensure_vertex_attributes(obj.data, colour)
            mesh_count += 1

    material_count = len({
        material.name
        for collection in collections
        for obj in collection.all_objects if obj.type == "MESH"
        for material in obj.data.materials if material
    })
    return mesh_count, material_count, created_textures


def find_meshes(collection):
    return [obj for obj in collection.all_objects if obj.type == "MESH"]


def convert_collections_to_drawables(collections):
    from Sollumz.tools.drawablehelper import convert_objs_to_single_drawable

    drawables = []
    for collection, drawable_name in zip(collections, [pair[1] for pair in SCENE_COLLECTIONS]):
        meshes = find_meshes(collection)
        if not meshes:
            raise RuntimeError(f"Collection {collection.name!r} has no mesh geometry")
        with bpy.context.temp_override(collection=collection):
            drawable = convert_objs_to_single_drawable(meshes)
        drawable.name = drawable_name
        drawable.location = (0.0, 0.0, 0.0)
        drawable.rotation_euler = (0.0, 0.0, 0.0)
        drawable.scale = (1.0, 1.0, 1.0)
        drawables.append(drawable)
    return drawables


def create_ytyp_and_ymap(drawables):
    from Sollumz.sollumz_properties import ArchetypeType
    from Sollumz.ymap_next.properties.map import get_maps

    scene = bpy.context.scene
    # One YTYP defines one base archetype for each custom drawable model.
    ytyp = scene.ytyps.add()
    ytyp.name = YTYP_NAME
    for drawable in drawables:
        archetype = ytyp.new_archetype(ArchetypeType.BASE)
        archetype.name = drawable.name.lower()
        archetype.asset = drawable
        archetype.lod_dist = 250.0
        archetype.hd_texture_dist = 100.0

    maps = get_maps(bpy.context, create_if_missing=True)
    group = maps.new_group()
    group.name = YMAP_NAME
    map_data = group.new_map()
    map_data.name = YMAP_NAME
    map_data.partition_mode = "NONE"

    for drawable in drawables:
        entity = group.new_entity()
        entity.name = drawable.name
        entity.map_data_uuid = map_data.uuid
        entity.map_group_uuid = group.uuid
        entity.archetype_name = drawable.name.lower()
        entity.position = tuple(drawable.location)
        entity.rotation = (1.0, 0.0, 0.0, 0.0)
        entity.scale_xy = 1.0
        entity.scale_z = 1.0
        entity.lod_level = "HD"
        entity.lod_dist = 250.0
        entity.priority_level = "REQUIRED"

    return ytyp, group, map_data


def export_ydds_and_maps(drawables, output_dir: Path):
    # Export YDRs separately so every scene collection has a predictable resource name.
    bpy.ops.object.select_all(action="DESELECT")
    for drawable in drawables:
        drawable.select_set(True)
    bpy.context.view_layer.objects.active = drawables[0]
    result = bpy.ops.sollumz.export_assets(
        directory=str(output_dir),
        direct_export=True,
        use_custom_settings=True,
        target_formats={"CWXML"},
        target_versions={"GEN8"},
        limit_to_selected=True,
        export_ytyps=False,
        export_ymaps=False,
    )
    if "FINISHED" not in result:
        raise RuntimeError(f"Sollumz YDR export failed: {result}")

    # Export map placement and matching archetype registry as a pair.
    bpy.ops.object.select_all(action="DESELECT")
    result = bpy.ops.sollumz.export_assets(
        directory=str(output_dir),
        direct_export=True,
        use_custom_settings=True,
        target_formats={"CWXML"},
        target_versions={"GEN8"},
        limit_to_selected=False,
        export_ytyps=True,
        export_ytyps_include="ALL",
        export_ymaps=True,
        export_ymaps_include="ALL",
    )
    if "FINISHED" not in result:
        raise RuntimeError(f"Sollumz YTYP/YMAP export failed: {result}")


def validate_xml_exports(output_dir: Path, drawables, mesh_count: int, material_count: int, texture_map):
    expected_ydrs = [f"{name}.ydr.xml" for _, name in SCENE_COLLECTIONS]
    ydr_files = [output_dir / name for name in expected_ydrs]
    missing = [str(path.name) for path in ydr_files if not path.is_file()]
    if missing:
        files = sorted(str(p.relative_to(output_dir)) for p in output_dir.rglob("*") if p.is_file())
        raise RuntimeError(f"Some expected YDR XML files are missing: {missing}; outputs={files}")

    parsed_ydeets = []
    for ydr_path in ydr_files:
        root = ET.parse(ydr_path).getroot()
        geometry_count = len(root.findall(".//DrawableModelsHigh/Item/Geometries/Item"))
        if geometry_count < 1:
            raise RuntimeError(f"No drawable geometry in {ydr_path.name}")
        parsed_ydeets.append({"file": ydr_path.name, "xml_root": root.tag, "geometry_items": geometry_count})

    ytyp_candidates = sorted(output_dir.glob("*.ytyp.xml"))
    ymap_candidates = sorted(output_dir.glob("*.ymap.xml"))
    if not ytyp_candidates:
        files = sorted(str(p.relative_to(output_dir)) for p in output_dir.rglob("*") if p.is_file())
        raise RuntimeError(f"Sollumz did not create any .ytyp.xml output. Files: {files}")
    if not ymap_candidates:
        files = sorted(str(p.relative_to(output_dir)) for p in output_dir.rglob("*") if p.is_file())
        raise RuntimeError(f"Sollumz did not create any .ymap.xml output. Files: {files}")

    parsed_ytyp = ET.parse(ytyp_candidates[0]).getroot()
    parsed_ymap = ET.parse(ymap_candidates[0]).getroot()
    ytyp_archetypes = len(parsed_ytyp.findall(".//archetypes/Item")) or len(parsed_ytyp.findall(".//Archetypes/Item"))
    ymap_entities = len(parsed_ymap.findall(".//entities/Item")) or len(parsed_ymap.findall(".//Entities/Item"))
    if ytyp_archetypes < len(drawables):
        raise RuntimeError(f"Expected >= {len(drawables)} YTYP archetypes, got {ytyp_archetypes} in {ytyp_candidates[0].name}")
    if ymap_entities < len(drawables):
        raise RuntimeError(f"Expected >= {len(drawables)} YMAP entities, got {ymap_entities} in {ymap_candidates[0].name}")

    manifest = {
        "schema_version": 1,
        "project": "GTA-Dushanbe",
        "status": "city_slice_cwxml_export_pipeline_passed",
        "game_ready": False,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "blender_version": bpy.app.version_string,
        "sollumz_version": "2.9.0",
        "export_format": "CodeWalker XML (CWXML)",
        "target_game_version": "GEN8 (GTA V Legacy)",
        "scene": ROOT_NAME,
        "coordinate_status": "schematic local coordinates only; not GTA V world coordinates",
        "source_mesh_count": mesh_count,
        "source_material_count": material_count,
        "texture_count": len(set(texture_map.values())),
        "drawable_count": len(drawables),
        "ydr_exports": parsed_ydeets,
        "ytyp_export": {
            "file": ytyp_candidates[0].name,
            "xml_root": parsed_ytyp.tag,
            "archetype_count": ytyp_archetypes,
        },
        "ymap_export": {
            "file": ymap_candidates[0].name,
            "xml_root": parsed_ymap.tag,
            "entity_count": ymap_entities,
        },
        "limitations": [
            "This is a first-pass CWXML export, not the game's binary files.",
            "All dimensions are schematic, not surveyed Dushanbe measurements.",
            "Coordinates are not mapped to GTA V world coordinates.",
            "There are no proper collision YBN files or complete LOD/SLOD hierarchy yet.",
            "Custom static cars and lights are geometry placeholders, not functional GTA traffic/lights.",
            "CodeWalker conversion/import and a local GTA V Legacy in-game test are still required.",
            "GTA V Enhanced / GEN9 has not been tested.",
        ],
    }
    (output_dir / "city_slice_export_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main():
    if not INPUT_BLEND.is_file():
        raise FileNotFoundError(f"Input Blender project not found: {INPUT_BLEND}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    texture_dir = OUTPUT_DIR / "textures"
    texture_dir.mkdir(parents=True, exist_ok=True)

    require_addon()
    bpy.ops.wm.open_mainfile(filepath=str(INPUT_BLEND))
    root = bpy.data.collections.get(ROOT_NAME)
    if root is None:
        raise RuntimeError(f"Input .blend has no {ROOT_NAME!r} collection")
    collections = []
    for collection_name, _ in SCENE_COLLECTIONS:
        collection = bpy.data.collections.get(collection_name)
        if collection is None:
            collection = root.children.get(collection_name)
        if collection is None:
            raise RuntimeError(f"Required city collection is missing: {collection_name}")
        collections.append(collection)

    mesh_count, material_count, texture_map = configure_materials_and_meshes(collections, texture_dir)
    drawables = convert_collections_to_drawables(collections)
    ytyp, ymap_group, map_data = create_ytyp_and_ymap(drawables)

    # Save a prepared editable scene before export; texture file paths are relative to this .blend.
    prepared_blend = OUTPUT_DIR / "Dushanbe_Istiklol_Sollumz_Prepared.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(prepared_blend))

    export_ydds_and_maps(drawables, OUTPUT_DIR)
    manifest = validate_xml_exports(OUTPUT_DIR, drawables, mesh_count, material_count, texture_map)
    print("DUSHANBE_CITY_SLICE_CWXML_EXPORT_OK")
    print(f"Blender: {bpy.app.version_string}")
    print(f"Source meshes: {mesh_count}; materials: {material_count}; drawables: {len(drawables)}")
    print(f"YTYP archetypes: {manifest['ytyp_export']['archetype_count']}")
    print(f"YMAP entities: {manifest['ymap_export']['entity_count']}")
    print(f"Prepared Blender scene: {prepared_blend}")
    print("NOT GAME-READY: CWXML conversion, collision/LOD setup, coordinate placement and in-game testing remain.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise
