"""Create an editable, illustrative Blender greybox for the first Dushanbe city slice.

Run inside Blender (Blender 4.0+):
  1. Open the Scripting workspace.
  2. Load this script into a Text Editor.
  3. Click Run Script.

All dimensions are deliberately schematic design assumptions in metres. They are NOT
surveyed Dushanbe measurements and NOT GTA V world coordinates. Nothing here is a
game-ready export. The script creates original greybox geometry only.
"""
import bpy
import math

ROOT_NAME = "Dushanbe_Istiklol_Greybox"

# Friendly greybox colours; materials are for visual review only.
MATERIALS = {
    "Ground": ((0.20, 0.24, 0.20, 1.0), 0.0),
    "Asphalt": ((0.10, 0.11, 0.12, 1.0), 0.0),
    "Marking": ((0.88, 0.84, 0.66, 1.0), 0.0),
    "Concrete": ((0.56, 0.57, 0.55, 1.0), 0.0),
    "PlazaStone": ((0.72, 0.70, 0.64, 1.0), 0.0),
    "BuildingMass": ((0.49, 0.52, 0.55, 1.0), 0.0),
    "BuildingDark": ((0.32, 0.36, 0.39, 1.0), 0.0),
    "Grass": ((0.14, 0.36, 0.16, 1.0), 0.0),
    "TreeTrunk": ((0.24, 0.15, 0.08, 1.0), 0.0),
    "TreeCanopy": ((0.10, 0.28, 0.10, 1.0), 0.0),
    "Stone": ((0.72, 0.68, 0.56, 1.0), 0.0),
    "GoldAccent": ((0.82, 0.52, 0.08, 1.0), 0.35),
    "CarA": ((0.65, 0.12, 0.08, 1.0), 0.1),
    "CarB": ((0.10, 0.22, 0.56, 1.0), 0.1),
    "CarC": ((0.78, 0.78, 0.72, 1.0), 0.1),
}


def get_material(name):
    material = bpy.data.materials.get("DushanbeGreybox_" + name)
    if material is None:
        material = bpy.data.materials.new("DushanbeGreybox_" + name)
    colour, metallic = MATERIALS[name]
    material.diffuse_color = colour
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = colour
        principled.inputs["Metallic"].default_value = metallic
        principled.inputs["Roughness"].default_value = 0.72
    return material


def remove_collection_tree(collection):
    for child in list(collection.children):
        remove_collection_tree(child)
    for obj in list(collection.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(collection, do_unlink=True)


def setup_collections():
    old_root = bpy.data.collections.get(ROOT_NAME)
    if old_root:
        remove_collection_tree(old_root)

    root = bpy.data.collections.new(ROOT_NAME)
    bpy.context.scene.collection.children.link(root)
    collections = {}
    for name in [
        "00_Ground",
        "01_Roads",
        "02_Plaza",
        "03_Landmark_Blockout",
        "04_Building_Masses",
        "05_Landscape",
        "06_Vehicle_Proxies",
    ]:
        collection = bpy.data.collections.new(name)
        root.children.link(collection)
        collections[name] = collection
    return collections


def relink_to_collection(obj, collection):
    for old_collection in list(obj.users_collection):
        old_collection.objects.unlink(obj)
    collection.objects.link(obj)


def add_box(name, location, dimensions, material_name, collection, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(get_material(material_name))
    relink_to_collection(obj, collection)
    if bevel > 0:
        modifier = obj.modifiers.new("Greybox_edge_softening", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
    return obj


def add_cylinder(name, location, radius, depth, material_name, collection, vertices=48):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth, location=location
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(get_material(material_name))
    relink_to_collection(obj, collection)
    return obj


def add_sphere(name, location, scale, material_name, collection):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(get_material(material_name))
    relink_to_collection(obj, collection)
    return obj


def add_tree(x, y, collection, height=5.5):
    add_cylinder(
        f"TreeTrunk_proxy_{x}_{y}",
        (x, y, height * 0.27),
        0.22,
        height * 0.54,
        "TreeTrunk",
        collection,
        vertices=12,
    )
    add_sphere(
        f"TreeCanopy_proxy_{x}_{y}",
        (x, y, height * 0.79),
        (height * 0.34, height * 0.34, height * 0.36),
        "TreeCanopy",
        collection,
    )


def add_vehicle_proxy(x, y, colour, collection, name):
    # Simple original blockout proxy, not a real GTA vehicle model.
    add_box(f"{name}_body_proxy", (x, y, 0.68), (4.4, 1.85, 0.95), colour, collection, 0.12)
    add_box(f"{name}_cabin_proxy", (x - 0.15, y, 1.28), (2.15, 1.55, 0.62), colour, collection, 0.1)


def add_road_markings(roads):
    # North-south avenue lane dashes.
    for x in (-7.0, -1.8, 3.4, 8.6):
        y = -125.0
        index = 0
        while y < -31.0:
            add_box(
                f"AvenueDash_{index}_{x}",
                (x, y, 0.16),
                (0.12, 3.0, 0.035),
                "Marking",
                roads,
            )
            y += 7.0
            index += 1
    # Cross street zebra crossing: visual greybox only.
    for index in range(10):
        x = -9.0 + index * 2.0
        add_box(
            f"CrosswalkStripe_{index}",
            (x, -65.0, 0.17),
            (0.95, 4.4, 0.04),
            "Marking",
            roads,
        )


def build_scene():
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "METERS"
    scene.unit_settings.scale_length = 1.0

    collections = setup_collections()
    ground = collections["00_Ground"]
    roads = collections["01_Roads"]
    plaza = collections["02_Plaza"]
    landmark = collections["03_Landmark_Blockout"]
    buildings = collections["04_Building_Masses"]
    landscape = collections["05_Landscape"]
    vehicles = collections["06_Vehicle_Proxies"]

    # Flat base: schematic extent 280 x 260 m, not a surveyed city footprint.
    add_box("Greybox_ground_base", (0, 0, -0.32), (280, 260, 0.55), "Ground", ground)

    # Primary approach avenue and perpendicular cross street.
    add_box("NorthSouth_approach_avenue", (0, -80, -0.02), (26, 100, 0.28), "Asphalt", roads)
    add_box("EastWest_cross_street", (0, -78, -0.01), (250, 18, 0.28), "Asphalt", roads)
    # Short local access roads bounding the blocks.
    add_box("West_local_street", (-77, -15, 0.0), (12, 230, 0.28), "Asphalt", roads)
    add_box("East_local_street", (77, -15, 0.0), (12, 230, 0.28), "Asphalt", roads)

    # Avenue sidewalks and outer boulevard sidewalks.
    for side in (-1, 1):
        add_box(f"Avenue_sidewalk_{side}", (side * 16.3, -80, 0.11), (3.4, 100, 0.22), "Concrete", roads)
        add_box(f"WestEast_sidewalk_{side}", (side * 84.8, -15, 0.11), (3.0, 230, 0.22), "Concrete", roads)

    add_road_markings(roads)

    # Plaza platform and central pedestrian axis.
    add_box("Istiklol_plaza_base_blockout", (0, 24, -0.005), (94, 108, 0.26), "Concrete", plaza)
    add_box("Main_pedestrian_axis", (0, 25, 0.145), (12, 100, 0.08), "PlazaStone", plaza)
    add_box("South_plaza_entry", (0, -29, 0.14), (38, 8, 0.07), "PlazaStone", plaza)
    add_box("North_plaza_forecourt", (0, 78, 0.14), (52, 8, 0.07), "PlazaStone", plaza)

    # Formal landscape beds placed symmetrically along the plaza.
    for side in (-1, 1):
        for index, y in enumerate((-12, 9, 30, 51, 69)):
            width = 11 if index % 2 == 0 else 8
            depth = 10 if index % 2 == 0 else 13
            add_box(
                f"Plaza_planting_bed_{side}_{index}",
                (side * (24 if index < 4 else 30), y, 0.17),
                (width, depth, 0.12),
                "Grass",
                landscape,
            )

    # Original landmark silhouette placeholder: stepped circular podium, tower and crown-like cap.
    # This is only a rough massing placeholder, not a reproduction or game-ready asset.
    add_cylinder("Landmark_plinth_large", (0, 32, 0.55), 15.0, 0.75, "Stone", landmark)
    add_cylinder("Landmark_plinth_mid", (0, 32, 1.12), 11.0, 0.45, "PlazaStone", landmark)
    add_cylinder("Landmark_plinth_top", (0, 32, 1.48), 7.5, 0.28, "Stone", landmark)
    add_cylinder("Landmark_tower_mass", (0, 32, 10.2), 2.45, 17.0, "Stone", landmark)
    add_cylinder("Landmark_upper_ring", (0, 32, 19.0), 3.25, 0.55, "GoldAccent", landmark)
    add_sphere("Landmark_cap_proxy", (0, 32, 20.0), (2.2, 2.2, 1.3), "GoldAccent", landmark)

    # Neighbourhood building masses: intentionally simple volumes to test scale and silhouette.
    building_specs = [
        (-111, -16, 30, 36, 24, "Building_west_south"),
        (111, -16, 30, 36, 27, "Building_east_south"),
        (-111, 33, 30, 38, 30, "Building_west_centre"),
        (111, 33, 30, 38, 23, "Building_east_centre"),
        (-65, 101, 34, 24, 24, "Building_northwest"),
        (65, 101, 34, 24, 29, "Building_northeast"),
    ]
    for x, y, width, depth, height, name in building_specs:
        add_box(
            f"{name}_mass",
            (x, y, height / 2),
            (width, depth, height),
            "BuildingMass",
            buildings,
            bevel=0.15,
        )
        # A darker inset volume helps distinguish the front side during the greybox review.
        add_box(
            f"{name}_front_volume",
            (x, y - depth / 2 - 0.08, min(height - 1.0, 8.0)),
            (width * 0.72, 0.16, min(9.0, height * 0.42)),
            "BuildingDark",
            buildings,
        )

    # Tree rows around the approach and plaza perimeter.
    for side in (-1, 1):
        for index, y in enumerate((-116, -103, -90, -45, -32)):
            add_tree(side * 20.5, y, landscape, height=5.5)
        for index, y in enumerate((-3, 20, 45, 68)):
            add_tree(side * 43.0, y, landscape, height=5.0)

    # Four schematic parked-car placeholders in side parking areas.
    # Replace these with approved existing GTA V assets in a later set-dressing pass.
    add_vehicle_proxy(-66, -103, "CarA", vehicles, "VehicleProxy_01")
    add_vehicle_proxy(66, -103, "CarB", vehicles, "VehicleProxy_02")
    add_vehicle_proxy(-66, -22, "CarC", vehicles, "VehicleProxy_03")
    add_vehicle_proxy(66, -22, "CarA", vehicles, "VehicleProxy_04")

    # Select the main scene extents and a useful initial view.
    bpy.ops.object.select_all(action="DESELECT")
    scene.cursor.location = (0, 24, 0)
    for area in bpy.context.screen.areas if bpy.context.screen else []:
        if area.type == "VIEW_3D":
            area.spaces.active.region_3d.view_location = (0, 15, 8)
            area.spaces.active.region_3d.view_distance = 180
            area.spaces.active.region_3d.view_perspective = "PERSP"

    print("Created Dushanbe Istiklol greybox.")
    print("Reminder: all geometry dimensions are schematic; not surveyed and not GTA V world coordinates.")
    print("Next: review the silhouette, choose target edition/platform, then prove a small export with Blender + Sollumz.")


build_scene()
