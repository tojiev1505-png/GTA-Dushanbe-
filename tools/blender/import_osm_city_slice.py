"""Replace schematic roads/building masses with an OSM-aligned local city slice.

Creates building shells from mapped footprints, projected road ribbons, plaza/park
surfaces, mapped trees, and facade-window geometry. Geometry not mapped in OSM is
estimated; this is not photogrammetry or an exact facade scan.
"""
from __future__ import annotations
import json, math, os
from pathlib import Path
import bpy

ROOT_NAME = "Dushanbe_Istiklol_Greybox"
OSM_FILE = Path(os.environ.get("DUSHANBE_OSM_JSON", "artifacts/osm/istiklol_slice.json")).resolve()
ANCHOR_LAT, ANCHOR_LON = 38.59124, 68.78162
METERS_PER_DEG_LAT = 110540.0
METERS_PER_DEG_LON = 111320.0 * math.cos(math.radians(ANCHOR_LAT))

def get_collection(name):
    root = bpy.data.collections.get(ROOT_NAME)
    if root is None:
        raise RuntimeError(f"Missing root collection: {ROOT_NAME}")
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        root.children.link(collection)
    elif root.children.get(collection.name) is None:
        root.children.link(collection)
    return collection

def tag_approximation_as_hidden(collection_name):
    collection = get_collection(collection_name)
    for obj in collection.all_objects:
        if obj.get("dushanbe_osm_generated"):
            continue
        obj["dushanbe_exclude_from_game"] = True
        obj["dushanbe_original_greybox"] = True
        obj.hide_render = True
        obj.hide_viewport = True

def material(name, colour, roughness=0.78, metallic=0.0):
    full_name = "Dushanbe_OSM_" + name
    mat = bpy.data.materials.get(full_name)
    if mat is None:
        mat = bpy.data.materials.new(full_name)
    mat.diffuse_color = (*colour, 1.0)
    mat.use_nodes = True
    principled = mat.node_tree.nodes.get("Principled BSDF") if mat.node_tree else None
    if principled:
        principled.inputs["Base Color"].default_value = (*colour, 1.0)
        principled.inputs["Roughness"].default_value = roughness
        principled.inputs["Metallic"].default_value = metallic
    return mat

def local_xy(lat, lon):
    return ((lon - ANCHOR_LON) * METERS_PER_DEG_LON, (lat - ANCHOR_LAT) * METERS_PER_DEG_LAT)

def parse_length(value, fallback=None):
    if value is None:
        return fallback
    try:
        token = str(value).strip().lower().replace(",", ".")
        if "'" in token or "ft" in token:
            cleaned = token.replace("feet", "").replace("foot", "").replace("ft", "").replace("'", "").strip()
            return float(cleaned) * 0.3048
        cleaned = token.replace("meters", "").replace("metres", "").replace("meter", "").replace("metre", "").replace("m", "").strip()
        return float(cleaned)
    except (TypeError, ValueError):
        return fallback

def is_closed_way(element):
    geometry = element.get("geometry") or []
    if len(geometry) < 4:
        return False
    a, b = geometry[0], geometry[-1]
    return abs(float(a.get("lat", 999)) - float(b.get("lat", -999))) < 1e-6 and abs(float(a.get("lon", 999)) - float(b.get("lon", -999))) < 1e-6

def polygon_xy(element):
    if not is_closed_way(element):
        return []
    geometry = element.get("geometry") or []
    points = []
    for item in geometry:
        if "lat" not in item or "lon" not in item:
            continue
        p = local_xy(float(item["lat"]), float(item["lon"]))
        if not points or math.dist(points[-1], p) > 0.02:
            points.append(p)
    if len(points) > 1 and math.dist(points[0], points[-1]) < 0.02:
        points.pop()
    if len(points) < 3:
        return []
    area2 = sum(points[i][0] * points[(i + 1) % len(points)][1] - points[(i + 1) % len(points)][0] * points[i][1] for i in range(len(points)))
    if abs(area2) < 1.0:
        return []
    if area2 < 0:
        points.reverse()
    return points

def polygon_area(points):
    return abs(sum(points[i][0] * points[(i + 1) % len(points)][1] - points[(i + 1) % len(points)][0] * points[i][1] for i in range(len(points))) / 2.0)

def make_mesh_object(name, collection, vertices, faces, mats, material_indices=None):
    if not faces or not vertices:
        return None
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    for mat in mats:
        mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj["dushanbe_osm_generated"] = True
    obj["osm_source"] = "OpenStreetMap contributors / ODbL"
    if material_indices is not None:
        for polygon, idx in zip(mesh.polygons, material_indices):
            polygon.material_index = idx
    return obj

def building_category(tags):
    building_type = str(tags.get("building", "")).lower()
    if any(token in building_type for token in ("industrial", "warehouse", "hangar", "manufacture", "service")):
        return 2
    if building_type in {"commercial", "retail", "office", "hotel"}:
        return 1
    if any(token in building_type for token in ("church", "mosque", "cathedral", "temple", "museum", "government", "civic", "public", "school", "university", "hospital", "stadium")):
        return 3
    return 0

def building_height(tags):
    height = parse_length(tags.get("height"))
    if height is not None and 2.5 <= height <= 180.0:
        return height
    levels = tags.get("building:levels") or tags.get("levels")
    try:
        floor_count = float(str(levels).replace(",", "."))
        if 1 <= floor_count <= 50:
            return max(3.2, floor_count * 3.1)
    except (ValueError, TypeError):
        pass
    kind = str(tags.get("building", "")).lower()
    if kind in {"church", "mosque", "cathedral", "temple"}:
        return 14.0
    if kind in {"industrial", "warehouse", "hangar"}:
        return 7.0
    if kind in {"commercial", "office", "hotel", "apartments", "government", "university", "hospital"}:
        return 15.0
    return 9.0

def add_window(vertices, faces, indices, p0, p1, nx, ny, start_z, width, height, mat_index):
    length = math.dist(p0, p1)
    if length <= 0.01 or width <= 0.05 or height <= 0.05:
        return
    ux, uy = (p1[0] - p0[0]) / length, (p1[1] - p0[1]) / length
    cx, cy = (p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5
    x1, y1 = cx - ux * width * 0.5 + nx * 0.04, cy - uy * width * 0.5 + ny * 0.04
    x2, y2 = cx + ux * width * 0.5 + nx * 0.04, cy + uy * width * 0.5 + ny * 0.04
    base = len(vertices)
    vertices.extend(((x1, y1, start_z), (x2, y2, start_z), (x2, y2, start_z + height), (x1, y1, start_z + height)))
    faces.append((base, base + 1, base + 2, base + 3))
    indices.append(mat_index)

def build_buildings(elements, collection):
    mats = [
        material("Residential_Stucco", (0.68, 0.59, 0.47)),
        material("Commercial_Stone", (0.73, 0.70, 0.62)),
        material("Industrial_Concrete", (0.43, 0.46, 0.46)),
        material("Civic_Limestone", (0.78, 0.74, 0.63)),
        material("Facade_Glass", (0.045, 0.105, 0.15), roughness=0.28, metallic=0.22),
    ]
    verts, faces, indices = [], [], []
    building_count = window_count = 0
    for element in elements:
        if element.get("type") != "way":
            continue
        tags = element.get("tags") or {}
        if "building" not in tags or tags.get("building") == "no":
            continue
        points = polygon_xy(element)
        area = polygon_area(points) if points else 0
        if not points or area < 12.0 or area > 90000.0:
            continue
        height = building_height(tags)
        n = len(points)
        base = len(verts)
        verts.extend((x, y, 0.0) for x, y in points)
        verts.extend((x, y, height) for x, y in points)
        category = building_category(tags)
        faces.append(tuple(base + n + i for i in range(n))); indices.append(category)
        faces.append(tuple(base + i for i in reversed(range(n)))); indices.append(category)
        for i in range(n):
            j = (i + 1) % n
            faces.append((base + i, base + j, base + n + j, base + n + i)); indices.append(category)
        if area > 48.0 and height >= 5.8 and tags.get("building") not in {"roof", "greenhouse", "shed"}:
            floors = max(1, min(30, int(height // 3.1)))
            for i in range(n):
                p0, p1 = points[i], points[(i + 1) % n]
                length = math.dist(p0, p1)
                if length < 5.0:
                    continue
                dx, dy = p1[0] - p0[0], p1[1] - p0[1]
                nx, ny = dy / length, -dx / length
                count = min(14, max(1, int(length // 3.4) - 1))
                spacing = length / (count + 1)
                win_width = min(1.45, spacing * 0.48)
                for floor in range(floors):
                    z = 0.7 + floor * 3.05
                    if z + 1.45 >= height:
                        continue
                    for w in range(count):
                        along = (w + 1) / (count + 1)
                        cx, cy = p0[0] + dx * along, p0[1] + dy * along
                        q0 = (cx - dx / length * win_width * 0.5, cy - dy / length * win_width * 0.5)
                        q1 = (cx + dx / length * win_width * 0.5, cy + dy / length * win_width * 0.5)
                        add_window(verts, faces, indices, q0, q1, nx, ny, z, win_width, 1.45, 4)
                        window_count += 1
        building_count += 1
    obj = make_mesh_object("OSM_Real_Building_Footprints_With_Facades", collection, verts, faces, mats, indices)
    return building_count, window_count, obj

def road_width(tags):
    highway = str(tags.get("highway", ""))
    widths = {
        "motorway": 22, "motorway_link": 10, "trunk": 18, "trunk_link": 10,
        "primary": 15, "primary_link": 9, "secondary": 12, "secondary_link": 8,
        "tertiary": 9, "tertiary_link": 7, "unclassified": 7, "residential": 6.5,
        "living_street": 5.5, "service": 4.2, "road": 6.0, "pedestrian": 4.0,
        "footway": 1.8, "path": 1.8, "cycleway": 2.2, "steps": 1.6,
    }
    return float(widths.get(highway, 5.5))

def build_roads(elements, collection):
    mats = [
        material("Road_Asphalt", (0.105, 0.115, 0.12), roughness=0.94),
        material("Sidewalk_Concrete", (0.47, 0.46, 0.42), roughness=0.9),
        material("Walkway", (0.58, 0.54, 0.46), roughness=0.92),
    ]
    verts, faces, indices = [], [], []
    road_count = road_segment_count = 0
    for element in elements:
        if element.get("type") != "way":
            continue
        tags = element.get("tags") or {}
        highway = tags.get("highway")
        if not highway or highway in {"proposed", "construction", "raceway"}:
            continue
        pts = []
        for g in element.get("geometry") or []:
            if "lat" not in g or "lon" not in g: continue
            p = local_xy(float(g["lat"]), float(g["lon"]))
            if not pts or math.dist(pts[-1], p) > 0.4: pts.append(p)
        if len(pts) < 2: continue
        width = road_width(tags)
        pedestrian = highway in {"pedestrian", "footway", "path", "cycleway", "steps"}
        road_mat = 2 if pedestrian else 0
        add_walkways = not pedestrian and highway not in {"motorway", "motorway_link", "trunk", "trunk_link", "service"}
        for p0, p1 in zip(pts, pts[1:]):
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            length = math.hypot(dx, dy)
            if length < 0.5: continue
            nx, ny = -dy / length, dx / length
            hw = width * 0.5
            left0, right0 = (p0[0] + nx * hw, p0[1] + ny * hw), (p0[0] - nx * hw, p0[1] - ny * hw)
            left1, right1 = (p1[0] + nx * hw, p1[1] + ny * hw), (p1[0] - nx * hw, p1[1] - ny * hw)
            z = -0.035
            b = len(verts)
            verts.extend(((left0[0], left0[1], z), (right0[0], right0[1], z), (right1[0], right1[1], z), (left1[0], left1[1], z)))
            faces.append((b, b + 1, b + 2, b + 3)); indices.append(road_mat)
            road_segment_count += 1
            if add_walkways and width >= 5.5:
                for sign in (-1.0, 1.0):
                    s0 = (p0[0] + nx * sign * (hw + 1.45), p0[1] + ny * sign * (hw + 1.45))
                    s1 = (p0[0] + nx * sign * (hw + 2.9), p0[1] + ny * sign * (hw + 2.9))
                    t0 = (p1[0] + nx * sign * (hw + 1.45), p1[1] + ny * sign * (hw + 1.45))
                    t1 = (p1[0] + nx * sign * (hw + 2.9), p1[1] + ny * sign * (hw + 2.9))
                    b = len(verts)
                    verts.extend(((s0[0], s0[1], z + 0.01), (s1[0], s1[1], z + 0.01), (t1[0], t1[1], z + 0.01), (t0[0], t0[1], z + 0.01)))
                    faces.append((b, b + 1, b + 2, b + 3)); indices.append(1)
        road_count += 1
    obj = make_mesh_object("OSM_Real_Road_Network_And_Sidewalks", collection, verts, faces, mats, indices)
    return road_count, road_segment_count, obj

def build_green_and_plazas(elements, green_collection, plaza_collection):
    green_mat = material("Parks_Grass", (0.18, 0.31, 0.13), roughness=0.97)
    woodland_mat = material("Woodland", (0.10, 0.22, 0.095), roughness=0.98)
    water_mat = material("Water", (0.07, 0.25, 0.34), roughness=0.26, metallic=0.08)
    plaza_mat = material("Mapped_Plaza_Paving", (0.57, 0.52, 0.43), roughness=0.9)
    park_vertices, park_faces, park_indices = [], [], []
    plaza_vertices, plaza_faces, plaza_indices = [], [], []
    park_count = plaza_count = water_count = 0
    for element in elements:
        if element.get("type") != "way": continue
        tags = element.get("tags") or {}
        if not is_closed_way(element): continue
        points = polygon_xy(element)
        if not points or polygon_area(points) < 6.0: continue
        is_plaza = tags.get("place") == "square" or tags.get("highway") == "pedestrian" or tags.get("area:highway") == "pedestrian"
        is_water = tags.get("natural") == "water"
        is_green = tags.get("leisure") in {"park", "garden", "playground", "pitch"} or tags.get("landuse") in {"grass", "forest", "recreation_ground", "park", "meadow"} or tags.get("natural") == "wood"
        if not (is_plaza or is_water or is_green): continue
        if is_plaza:
            base = len(plaza_vertices)
            plaza_vertices.extend((x, y, 0.035) for x, y in points)
            plaza_faces.append(tuple(base + i for i in range(len(points)))); plaza_indices.append(0)
            plaza_count += 1
        else:
            base = len(park_vertices)
            z = -0.065 if is_water else -0.055
            park_vertices.extend((x, y, z) for x, y in points)
            park_faces.append(tuple(base + i for i in range(len(points))))
            park_indices.append(2 if is_water else (1 if tags.get("landuse") == "forest" or tags.get("natural") == "wood" else 0))
            if is_water: water_count += 1
            else: park_count += 1
    park_obj = make_mesh_object("OSM_Real_Parks_Greens_Water", green_collection, park_vertices, park_faces, [green_mat, woodland_mat, water_mat], park_indices)
    plaza_obj = make_mesh_object("OSM_Real_Plaza_Polygons", plaza_collection, plaza_vertices, plaza_faces, [plaza_mat], plaza_indices)
    return park_count, plaza_count, water_count, park_obj, plaza_obj

def build_trees(elements, collection):
    trunk_mat = material("Tree_Trunks", (0.26, 0.16, 0.085))
    leaf_mat = material("Tree_Canopy", (0.09, 0.27, 0.10), roughness=0.99)
    verts, faces, indices = [], [], []
    tree_count, sides = 0, 7
    for element in elements:
        if element.get("type") != "node" or (element.get("tags") or {}).get("natural") != "tree": continue
        lat, lon = element.get("lat"), element.get("lon")
        if lat is None or lon is None: continue
        x, y = local_xy(float(lat), float(lon))
        tags = element.get("tags") or {}
        tree_height = max(2.5, min(18.0, parse_length(tags.get("height"), 7.0) or 7.0))
        trunk_h, radius = min(2.3, tree_height * 0.34), max(0.5, min(2.5, tree_height * 0.19))
        base = len(verts)
        for z, r in ((0.0, 0.22), (trunk_h, 0.16)):
            for j in range(sides):
                a = math.tau * j / sides
                verts.append((x + math.cos(a) * r, y + math.sin(a) * r, z - 0.02))
        faces.append(tuple(base + j for j in reversed(range(sides)))); indices.append(0)
        for j in range(sides):
            j2 = (j + 1) % sides
            faces.append((base + j, base + j2, base + sides + j2, base + sides + j)); indices.append(0)
        canopy = len(verts)
        rings = ((trunk_h, radius * 0.95), (trunk_h + (tree_height - trunk_h) * 0.50, radius), (tree_height, 0.05))
        for rz, rr in rings:
            for j in range(sides):
                a = math.tau * j / sides
                verts.append((x + math.cos(a) * rr, y + math.sin(a) * rr, rz - 0.02))
        faces.append(tuple(canopy + j for j in reversed(range(sides)))); indices.append(1)
        for ring in range(len(rings) - 1):
            a0, a1 = canopy + ring * sides, canopy + (ring + 1) * sides
            for j in range(sides):
                j2 = (j + 1) % sides
                faces.append((a0 + j, a0 + j2, a1 + j2, a1 + j)); indices.append(1)
        tree_count += 1
    obj = make_mesh_object("OSM_Real_Mapped_Trees", collection, verts, faces, [trunk_mat, leaf_mat], indices)
    return tree_count, obj

def add_city_ground(collection):
    ground_mat = material("Urban_Base_Ground", (0.35, 0.34, 0.29), roughness=0.99)
    half = 1200.0
    verts = [(-half, -half, -0.42), (half, -half, -0.42), (half, half, -0.42), (-half, half, -0.42)]
    return make_mesh_object("OSM_Real_City_Base", collection, verts, [(0, 1, 2, 3)], [ground_mat])

def main():
    if not OSM_FILE.is_file():
        raise FileNotFoundError(f"OSM extract not found: {OSM_FILE}")
    payload = json.loads(OSM_FILE.read_text(encoding="utf-8"))
    elements = payload.get("elements")
    metadata = payload.get("project_metadata", {})
    if not isinstance(elements, list) or len(elements) < 100:
        raise RuntimeError("OSM extract is empty or too small to build the city slice")

    root = bpy.data.collections.get(ROOT_NAME)
    if root is None: raise RuntimeError(f"Missing base city collection {ROOT_NAME!r}")
    ground_collection = get_collection("00_Ground")
    road_collection = get_collection("01_Roads")
    plaza_collection = get_collection("02_Plaza")
    building_collection = get_collection("04_Building_Masses")
    green_collection = get_collection("05_Landscape")
    vehicle_collection = get_collection("06_Vehicle_Proxies")

    for name in ("00_Ground", "01_Roads", "04_Building_Masses", "05_Landscape", "07_Facade_Detail", "06_Vehicle_Proxies"):
        tag_approximation_as_hidden(name)

    plaza_stats = [e for e in elements if e.get("type") == "way" and is_closed_way(e) and ((e.get("tags") or {}).get("place") == "square" or (e.get("tags") or {}).get("highway") == "pedestrian" or (e.get("tags") or {}).get("area:highway") == "pedestrian")]
    if plaza_stats:
        tag_approximation_as_hidden("02_Plaza")

    add_city_ground(ground_collection)
    road_count, road_segments, _ = build_roads(elements, road_collection)
    building_count, window_count, _ = build_buildings(elements, building_collection)
    park_count, plaza_count, water_count, _, _ = build_green_and_plazas(elements, green_collection, plaza_collection)
    tree_count, _ = build_trees(elements, green_collection)

    for obj in vehicle_collection.all_objects:
        obj.hide_render = True
        obj.hide_viewport = True
        obj["dushanbe_exclude_from_game"] = True

    scene = bpy.context.scene
    scene["dushanbe_osm_imported"] = True
    scene["dushanbe_osm_source"] = "OpenStreetMap contributors / ODbL 1.0"
    scene["dushanbe_osm_buildings"] = building_count
    scene["dushanbe_osm_windows"] = window_count
    scene["dushanbe_osm_road_ways"] = road_count
    scene["dushanbe_osm_road_segments"] = road_segments
    scene["dushanbe_osm_green_areas"] = park_count
    scene["dushanbe_osm_plaza_polygons"] = plaza_count
    scene["dushanbe_osm_water_areas"] = water_count
    scene["dushanbe_osm_mapped_trees"] = tree_count
    scene["dushanbe_osm_fetched_utc"] = metadata.get("fetched_utc", "unknown")
    scene["dushanbe_osm_bbox"] = metadata.get("query_bbox_south_west_north_east", [])

    print("DUSHANBE_OSM_CITY_GEOMETRY_OK")
    print(f"Buildings: {building_count}; procedural facade windows: {window_count}")
    print(f"Road ways/segments: {road_count}/{road_segments}; parks: {park_count}; plazas: {plaza_count}; water: {water_count}; trees: {tree_count}")
    print("OSM footprints and roads are geographically aligned around the Istiklol Monument anchor.")
    print("NOT PHOTOGRAMMETRY: facade materials, roof shapes and window placement remain approximate.")

if __name__ == "__main__":
    main()
