"""Add a second detailing pass to the Dushanbe Istiklol schematic city slice.

Run only after create_istiklol_greybox.py, in the same Blender process.
All detail remains original, schematic, and not game-ready.
"""
import bpy
import math

ROOT_NAME = "Dushanbe_Istiklol_Greybox"


def material(name, colour, metallic=0.0, roughness=0.68, emission=0.0):
    full_name = "DushanbeGreybox_" + name
    mat = bpy.data.materials.get(full_name)
    if mat is None:
        mat = bpy.data.materials.new(full_name)
    mat.diffuse_color = (*colour, 1.0)
    mat.use_nodes = True
    principled = mat.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = (*colour, 1.0)
        principled.inputs["Metallic"].default_value = metallic
        principled.inputs["Roughness"].default_value = roughness
        if emission > 0:
            emission_input = principled.inputs.get("Emission Color") or principled.inputs.get("Emission")
            if emission_input:
                emission_input.default_value = (*colour, 1.0)
            strength = principled.inputs.get("Emission Strength")
            if strength:
                strength.default_value = emission
    return mat


PALETTE = {
    "Glass": ((0.08, 0.20, 0.27), 0.18, 0.28, 0.0),
    "GlassLit": ((0.36, 0.53, 0.60), 0.05, 0.35, 0.0),
    "FacadeTrim": ((0.70, 0.69, 0.62), 0.0, 0.74, 0.0),
    "FacadeWarm": ((0.70, 0.58, 0.42), 0.0, 0.82, 0.0),
    "MetalDark": ((0.075, 0.085, 0.09), 0.65, 0.46, 0.0),
    "LampGlow": ((1.0, 0.72, 0.35), 0.0, 0.38, 2.0),
    "SeatWood": ((0.35, 0.20, 0.10), 0.0, 0.75, 0.0),
    "RoadWhite": ((0.90, 0.88, 0.78), 0.0, 0.8, 0.0),
    "SignalRed": ((0.65, 0.035, 0.02), 0.0, 0.35, 0.4),
    "SignalGreen": ((0.04, 0.38, 0.09), 0.0, 0.35, 0.3),
    "WheelRubber": ((0.025, 0.03, 0.035), 0.0, 0.86, 0.0),
}


def get_collection(name):
    root = bpy.data.collections.get(ROOT_NAME)
    if root is None:
        raise RuntimeError("Run the base greybox generator before add_city_details.py")
    old = bpy.data.collections.get(name)
    if old is not None:
        for obj in list(old.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        for child in list(old.children):
            old.children.unlink(child)
            bpy.data.collections.remove(child)
        for parent in list(bpy.data.collections):
            if parent.children.get(old.name) is not None:
                parent.children.unlink(old)
        bpy.data.collections.remove(old)
    collection = bpy.data.collections.new(name)
    root.children.link(collection)
    return collection


def link_object(obj, collection):
    for old_collection in list(obj.users_collection):
        old_collection.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def box(name, location, dimensions, mat_name, collection, bevel=0.0, rotate_z=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location, rotation=(0.0, 0.0, rotate_z))
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(get_material_by_name(mat_name))
    link_object(obj, collection)
    if bevel:
        modifier = obj.modifiers.new("Detail_edge_softening", "BEVEL")
        modifier.width = bevel
        modifier.segments = 2
    return obj


def cylinder(name, location, radius, depth, mat_name, collection, rotation=None, vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth, location=location,
        rotation=rotation or (0.0, 0.0, 0.0)
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(get_material_by_name(mat_name))
    return link_object(obj, collection)


def get_material_by_name(name):
    if name in PALETTE:
        colour, metallic, roughness, emission = PALETTE[name]
        return material(name, colour, metallic, roughness, emission)
    existing = bpy.data.materials.get("DushanbeGreybox_" + name)
    if existing is None:
        raise RuntimeError("Base greybox material missing: " + name)
    return existing


def add_facades(collection):
    """Window grids, floor bands, parapets, and shopfronts on the six blockout buildings."""
    specs = [
        (-111, -16, 30, 36, 24, "Building_west_south"),
        (111, -16, 30, 36, 27, "Building_east_south"),
        (-111, 33, 30, 38, 30, "Building_west_centre"),
        (111, 33, 30, 38, 23, "Building_east_centre"),
        (-65, 101, 34, 24, 24, "Building_northwest"),
        (65, 101, 34, 24, 29, "Building_northeast"),
    ]
    window_count = 0
    for bx, by, width, depth, height, name in specs:
        # Front face points toward negative Y. Floor-to-floor rhythm is a visual placeholder.
        front_y = by - depth / 2 - 0.19
        floors = max(3, int(height // 4.2))
        cols = max(4, int(width // 4.0))
        window_w = min(2.15, (width - 4.0) / cols * 0.62)
        window_h = 1.55
        # Ground-floor glazed bays.
        bay_count = max(3, cols - 1)
        bay_w = (width - 5.0) / bay_count
        for i in range(bay_count):
            wx = bx - (width - 5.0) / 2 + (i + 0.5) * bay_w
            box(f"{name}_shop_glass_{i}", (wx, front_y - 0.015, 2.1),
                (max(0.9, bay_w * 0.72), 0.055, 2.6), "GlassLit", collection)
        box(f"{name}_entrance_canopy", (bx, front_y - 0.48, 3.65),
            (min(width - 2.0, 19.0), 0.95, 0.22), "FacadeWarm", collection, 0.05)
        # Upper floors: regular windows with sill trim.
        for floor in range(1, floors):
            z = 3.8 + floor * 4.0
            if z + window_h / 2 > height - 1.1:
                continue
            box(f"{name}_floor_band_{floor}", (bx, front_y - 0.01, z - 1.4),
                (width - 1.0, 0.12, 0.16), "FacadeTrim", collection)
            for col in range(cols):
                wx = bx - (cols - 1) * (width - 4.0) / (2 * cols) + col * (width - 4.0) / cols
                box(f"{name}_window_f{floor}_c{col}", (wx, front_y - 0.10, z),
                    (window_w, 0.12, window_h), "Glass" if (floor + col) % 4 else "GlassLit",
                    collection, 0.025)
                window_count += 1
        # Roof parapet segments.
        parapet_z = height + 0.45
        box(f"{name}_roof_parapet_front", (bx, by - depth / 2, parapet_z),
            (width, 0.35, 0.9), "FacadeTrim", collection)
        box(f"{name}_roof_parapet_back", (bx, by + depth / 2, parapet_z),
            (width, 0.35, 0.9), "FacadeTrim", collection)
        for side in (-1, 1):
            box(f"{name}_roof_parapet_side_{side}", (bx + side * width / 2, by, parapet_z),
                (0.35, depth, 0.9), "FacadeTrim", collection)
        # East-facing side facade windows add depth to the aerial preview.
        side_x = bx + width / 2 + 0.15
        side_cols = max(2, int(depth // 5.0))
        for floor in range(1, floors):
            z = 3.8 + floor * 4.0
            if z + 0.75 > height - 1.2:
                continue
            for col in range(side_cols):
                wy = by - (side_cols - 1) * (depth - 3.0) / (2 * side_cols) + col * (depth - 3.0) / side_cols
                box(f"{name}_side_window_f{floor}_c{col}", (side_x, wy, z),
                    (0.12, 1.35, 1.45), "Glass", collection, 0.02)
        # A few shallow pilasters give the ground floor a clear entrance rhythm.
        for side in (-1, 1):
            px = bx + side * (width / 2 - 1.0)
            box(f"{name}_entry_pilaster_{side}", (px, front_y - 0.05, 1.9),
                (0.32, 0.22, 3.7), "FacadeTrim", collection)
    return window_count


def add_paving_and_urban_furniture(plaza, furniture, roads):
    # Paver joints: thin inset lines across the pedestrian promenade.
    for y in range(-18, 77, 4):
        box(f"Promenade_joint_y{y}", (0, y, 0.194), (11.4, 0.035, 0.018), "FacadeTrim", plaza)
    for x in (-4, 0, 4):
        box(f"Promenade_joint_x{x}", (x, 25, 0.194), (0.035, 95, 0.018), "FacadeTrim", plaza)

    # Benches in symmetric pairs around the plaza. All pieces are editable meshes.
    for idx, (x, y, angle) in enumerate([
        (-29, 5, 0), (29, 5, math.pi), (-29, 34, 0), (29, 34, math.pi),
        (-29, 60, 0), (29, 60, math.pi)
    ]):
        box(f"Bench_{idx}_seat", (x, y, 0.62), (2.5, 0.62, 0.16), "SeatWood", furniture, 0.04, angle)
        box(f"Bench_{idx}_back", (x, y - 0.24, 1.12), (2.5, 0.12, 0.9), "SeatWood", furniture, 0.03, angle)
        for leg, dx in enumerate((-0.9, 0.9)):
            box(f"Bench_{idx}_leg_{leg}", (x + dx, y, 0.33), (0.12, 0.55, 0.55), "MetalDark", furniture, 0.02, angle)

    # Short bollard rows protecting the main pedestrian entrance.
    for side in (-1, 1):
        for idx in range(7):
            x = side * (20.0 + idx * 2.4)
            cylinder(f"Entrance_bollard_{side}_{idx}", (x, -31.5, 0.55), 0.20, 1.1,
                     "MetalDark", furniture, vertices=12)
            cylinder(f"Entrance_bollard_cap_{side}_{idx}", (x, -31.5, 1.12), 0.21, 0.08,
                     "FacadeWarm", furniture, vertices=12)

    # Decorative low planters placed along the promenade perimeter.
    for side in (-1, 1):
        for idx, y in enumerate((-9, 15, 40, 64)):
            box(f"Planter_{side}_{idx}_body", (side * 36.0, y, 0.5), (3.6, 3.0, 0.65),
                "Concrete", furniture, 0.08)
            box(f"Planter_{side}_{idx}_soil", (side * 36.0, y, 0.85), (3.25, 2.65, 0.08),
                "Grass", furniture)

    # Modern plaza lights (static geometry in this schematic; no game light behaviour).
    for side in (-1, 1):
        for idx, y in enumerate((-5, 17, 40, 62, 83)):
            x = side * 39.0
            cylinder(f"Plaza_lamp_{side}_{idx}_pole", (x, y, 3.5), 0.10, 7.0,
                     "MetalDark", furniture, vertices=12)
            box(f"Plaza_lamp_{side}_{idx}_head", (x, y, 7.1), (0.85, 0.45, 0.2),
                "LampGlow", furniture, 0.08)


def add_cars_and_road_details(vehicles, roads):
    # Tire geometry for each original car proxy. Wheel axes are horizontal (Y).
    car_specs = [
        (-66, -103, "CarA", 0.65), (66, -103, "CarB", 0.65),
        (-66, -22, "CarC", 0.65), (66, -22, "CarA", 0.65),
    ]
    for car_idx, (x, y, colour, z) in enumerate(car_specs, start=1):
        # Wheels aligned with the 4.4 m body length.
        for axle, dx in enumerate((-1.45, 1.45)):
            for side, dy in enumerate((-0.94, 0.94)):
                cylinder(f"VehicleProxy_{car_idx}_wheel_{axle}_{side}",
                         (x + dx, y + dy, z), 0.34, 0.18, "WheelRubber", vehicles,
                         rotation=(math.pi / 2, 0.0, 0.0), vertices=16)
        # Contrasting glass panes on the roof/cabin, windshield, and rear window.
        box(f"VehicleProxy_{car_idx}_windshield", (x + 0.55, y, 1.38),
            (0.08, 1.28, 0.43), "Glass", vehicles, 0.025)
        box(f"VehicleProxy_{car_idx}_rear_glass", (x - 0.88, y, 1.38),
            (0.08, 1.22, 0.4), "Glass", vehicles, 0.025)
        for side, dy in enumerate((-0.79, 0.79)):
            box(f"VehicleProxy_{car_idx}_side_glass_{side}", (x - 0.12, y + dy, 1.38),
                (1.05, 0.06, 0.38), "Glass", vehicles, 0.02)
        # Headlamps and tail lamps are visual proxies only.
        for side, dy in enumerate((-0.64, 0.64)):
            box(f"VehicleProxy_{car_idx}_headlamp_{side}", (x + 2.17, y + dy, 0.73),
                (0.08, 0.30, 0.18), "LampGlow", vehicles)
            box(f"VehicleProxy_{car_idx}_taillamp_{side}", (x - 2.17, y + dy, 0.73),
                (0.08, 0.30, 0.18), "SignalRed", vehicles)

    # Curb strips define roadway edges. These are visual mesh strips, not collision.
    for side in (-1, 1):
        box(f"Avenue_curb_{side}", (side * 14.3, -80, 0.16), (0.28, 100, 0.24),
            "FacadeTrim", roads)
        box(f"EastWest_curb_{side}", (side * 83.0, -15, 0.16), (0.28, 230, 0.24),
            "FacadeTrim", roads)

    # Parking bay lines and stop-line/crosswalk cues.
    for side in (-1, 1):
        for idx in range(5):
            y = -118 + idx * 8
            x = side * 65.0
            box(f"Parking_bay_{side}_{idx}_line", (x, y, 0.16), (4.8, 0.10, 0.035),
                "RoadWhite", roads)
    for idx in range(10):
        box(f"Crosswalk_stopline_{idx}", (-10.0 + idx * 2.2, -69.5, 0.17),
            (1.7, 0.16, 0.035), "RoadWhite", roads)

    # Traffic signals at the junction; decorative only at this stage.
    for side in (-1, 1):
        x = side * 18.5
        y = -66.0
        cylinder(f"Signal_pole_{side}", (x, y, 3.0), 0.10, 6.0, "MetalDark", roads, vertices=12)
        box(f"Signal_box_{side}", (x, y, 5.3), (0.45, 0.38, 1.05), "MetalDark", roads, 0.03)
        cylinder(f"Signal_red_{side}", (x, y - 0.205, 5.58), 0.10, 0.06, "SignalRed", roads,
                 rotation=(math.pi / 2, 0, 0), vertices=12)
        cylinder(f"Signal_green_{side}", (x, y - 0.205, 5.0), 0.10, 0.06, "SignalGreen", roads,
                 rotation=(math.pi / 2, 0, 0), vertices=12)


def main():
    facade = get_collection("07_Facade_Detail")
    furniture = get_collection("08_Street_Furniture")
    roads = bpy.data.collections.get("01_Roads")
    plaza = bpy.data.collections.get("02_Plaza")
    vehicles = bpy.data.collections.get("06_Vehicle_Proxies")
    if not all((roads, plaza, vehicles)):
        raise RuntimeError("Base greybox collections are incomplete")

    windows = add_facades(facade)
    add_paving_and_urban_furniture(plaza, furniture, roads)
    add_cars_and_road_details(vehicles, roads)

    print("Added second-pass architecture, windows, roof parapets, benches, lamps, planters, car wheels and junction details.")
    print(f"Added facade window panes: {windows}")


if __name__ == "__main__":
    main()
