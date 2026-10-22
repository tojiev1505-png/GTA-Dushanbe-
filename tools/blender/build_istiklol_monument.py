"""Build a detailed, reference-based procedural model of Dushanbe's Istiklol Monument.

The model uses the published overall height (121 m) and lower architectural section (30 m),
plus visual reference for the life-tree shaft, observation deck, seven-gate base, blue panels
and gilded crown. It is original geometry, not extracted third-party content or photogrammetry.
"""
from __future__ import annotations

import math
import bpy
import bmesh
from mathutils import Vector

ROOT_NAME = "Dushanbe_Istiklol_Greybox"
COLLECTION_NAME = "03_Landmark_Blockout"
SEGMENTS = 48
OVERALL_HEIGHT_M = 121.0
LOWER_SECTION_HEIGHT_M = 30.0
GATE_COUNT = 7


def get_collection():
    root = bpy.data.collections.get(ROOT_NAME)
    if root is None:
        raise RuntimeError(f"Missing scene root {ROOT_NAME!r}")
    collection = bpy.data.collections.get(COLLECTION_NAME)
    if collection is None:
        collection = bpy.data.collections.new(COLLECTION_NAME)
        root.children.link(collection)
    elif root.children.get(collection.name) is None:
        root.children.link(collection)
    return collection


def make_material(name, colour, metallic=0.0, roughness=0.55):
    full_name = "IstiklolRealism_" + name
    mat = bpy.data.materials.get(full_name)
    if mat is None:
        mat = bpy.data.materials.new(full_name)
    mat.diffuse_color = (*colour, 1.0)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF") if mat.node_tree else None
    if shader:
        shader.inputs["Base Color"].default_value = (*colour, 1.0)
        shader.inputs["Metallic"].default_value = metallic
        shader.inputs["Roughness"].default_value = roughness
    return mat


class MeshBuilder:
    def __init__(self, name, materials, smooth=False):
        self.name = name
        self.materials = materials
        self.smooth = smooth
        self.vertices = []
        self.faces = []
        self.material_indices = []

    def add_vertices(self, points):
        first = len(self.vertices)
        self.vertices.extend(tuple(float(v) for v in point) for point in points)
        return list(range(first, len(self.vertices)))

    def face(self, indices, material_index=0):
        if len(indices) >= 3:
            self.faces.append(tuple(indices))
            self.material_indices.append(material_index)

    def face_points(self, points, material_index=0):
        self.face(self.add_vertices(points), material_index)

    def build(self, collection):
        if not self.vertices or not self.faces:
            return None
        mesh = bpy.data.meshes.new(self.name + "_Mesh")
        mesh.from_pydata(self.vertices, [], self.faces)
        mesh.update()
        for mat in self.materials:
            mesh.materials.append(mat)
        for polygon, mat_index in zip(mesh.polygons, self.material_indices):
            polygon.material_index = max(0, min(mat_index, len(self.materials) - 1))
            polygon.use_smooth = self.smooth
        # Recalculate normals so the mesh remains watertight-looking after export.
        bm = bmesh.new()
        bm.from_mesh(mesh)
        if bm.faces:
            bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()
        obj = bpy.data.objects.new(self.name, mesh)
        collection.objects.link(obj)
        obj["dushanbe_procedural_asset"] = "Istiklol Monument visual reconstruction"
        obj["dushanbe_reference_height_m"] = OVERALL_HEIGHT_M
        obj["dushanbe_exclude_from_game"] = False
        return obj


def point_local(tangent, z, radial_depth, angle, centre_radius=0.0):
    radius = centre_radius + radial_depth
    return (
        radius * math.cos(angle) - tangent * math.sin(angle),
        radius * math.sin(angle) + tangent * math.cos(angle),
        z,
    )


def add_loft(builder, profile, segments=32, centre=(0.0, 0.0), angle_offset=0.0,
             twist_fn=None, band_materials=None, caps=True):
    """Build a ring loft from (z, radius) pairs around an optional XY centre."""
    if len(profile) < 2:
        return
    first = len(builder.vertices)
    for z, radius in profile:
        for j in range(segments):
            angle = math.tau * j / segments + angle_offset
            if twist_fn:
                angle += twist_fn(z)
            builder.vertices.append((centre[0] + radius * math.cos(angle),
                                     centre[1] + radius * math.sin(angle), z))
    for ring in range(len(profile) - 1):
        for j in range(segments):
            j2 = (j + 1) % segments
            idx = (band_materials[ring] if band_materials and ring < len(band_materials) else 0)
            builder.face((first + ring * segments + j,
                          first + ring * segments + j2,
                          first + (ring + 1) * segments + j2,
                          first + (ring + 1) * segments + j), idx)
    if caps:
        builder.face(tuple(first + j for j in reversed(range(segments))), 0)
        last = first + (len(profile) - 1) * segments
        builder.face(tuple(last + j for j in range(segments)), 0)


def add_band(builder, z, radius, height, width=0.25, segments=48, material_index=0):
    add_loft(
        builder,
        [(z - height / 2, radius - width / 2),
         (z - height / 2, radius + width / 2),
         (z + height / 2, radius + width / 2),
         (z + height / 2, radius - width / 2)],
        segments=segments,
        band_materials=[material_index, material_index, material_index],
        caps=False,
    )


def radius_at(z, profile):
    for (za, ra), (zb, rb) in zip(profile, profile[1:]):
        if za <= z <= zb:
            t = 0.0 if zb == za else (z - za) / (zb - za)
            return ra + (rb - ra) * t
    return profile[0][1] if z < profile[0][0] else profile[-1][1]


def add_helix(builder, profile, start_angle, turns=1.75, z0=33.5, z1=109.5,
              width=0.62, radial_offset=0.22, samples=280, material_index=0):
    """Create a raised ribbon wound up the monument's curved shaft."""
    first = len(builder.vertices)
    for i in range(samples + 1):
        t = i / samples
        z = z0 + (z1 - z0) * t
        centre_angle = start_angle + math.tau * turns * t + 0.016 * (z - 30.0)
        radius = radius_at(z, profile) + radial_offset
        half = (width * 0.5) / max(radius, 0.1)
        for angle in (centre_angle - half, centre_angle + half):
            builder.vertices.append((radius * math.cos(angle), radius * math.sin(angle), z))
    for i in range(samples):
        a = first + i * 2
        builder.face((a, a + 1, a + 3, a + 2), material_index)


def add_radial_box(builder, angle, centre_radius, width, depth, z0, z1, material_index=0):
    """Oriented prism with its front directed radially out from the tower."""
    tangent = Vector((-math.sin(angle), math.cos(angle), 0.0))
    radial = Vector((math.cos(angle), math.sin(angle), 0.0))
    centre = radial * centre_radius
    points = []
    for z in (z0, z1):
        for along, outward in ((-width / 2, -depth / 2),
                               (width / 2, -depth / 2),
                               (width / 2, depth / 2),
                               (-width / 2, depth / 2)):
            p = centre + tangent * along + radial * outward
            points.append((p.x, p.y, z))
    v = builder.add_vertices(points)
    builder.face((v[0], v[3], v[2], v[1]), material_index)
    builder.face((v[4], v[5], v[6], v[7]), material_index)
    for j in range(4):
        j2 = (j + 1) % 4
        builder.face((v[j], v[j2], v[j2 + 4], v[j + 4]), material_index)


def arch_outline(width, height, z_base, arc_segments=12):
    half = width / 2
    spring = z_base + height - half
    points = [(-half, z_base), (half, z_base), (half, spring)]
    for k in range(1, arc_segments + 1):
        a = math.pi * k / arc_segments
        points.append((half * math.cos(a), spring + half * math.sin(a)))
    points.append((-half, z_base))
    return points


def world_on_gate(tangent, z, radial_distance, angle):
    x = radial_distance * math.cos(angle) - tangent * math.sin(angle)
    y = radial_distance * math.sin(angle) + tangent * math.cos(angle)
    return (x, y, z)


def add_arch_frame(builder, angle, radius, z_base, width, height,
                   frame_width=0.62, depth=0.85, material_index=0):
    outer = arch_outline(width + frame_width * 2, height + frame_width * 1.4, z_base)
    inner = arch_outline(width, height, z_base)
    if len(outer) != len(inner):
        raise RuntimeError("Arch frame paths need equal vertex counts")
    back_radius = radius - depth
    out_front = [world_on_gate(s, z, radius, angle) for s, z in outer]
    in_front = [world_on_gate(s, z, radius + 0.035, angle) for s, z in inner]
    out_back = [world_on_gate(s, z, back_radius, angle) for s, z in outer]
    in_back = [world_on_gate(s, z, back_radius, angle) for s, z in inner]
    of = builder.add_vertices(out_front)
    inf = builder.add_vertices(in_front)
    ob = builder.add_vertices(out_back)
    ib = builder.add_vertices(in_back)
    for i in range(len(outer) - 1):
        j = i + 1
        builder.face((of[i], of[j], inf[j], inf[i]), material_index)
        builder.face((ob[i], ib[i], ib[j], ob[j]), material_index)
        builder.face((of[i], ob[i], ob[j], of[j]), material_index)
        builder.face((inf[i], inf[j], ib[j], ib[i]), material_index)


def add_doorway(builder, angle, radius, z_base, width, height, material_index=0):
    shape = arch_outline(width, height, z_base, arc_segments=16)[:-1]
    builder.face_points([world_on_gate(s, z, radius, angle) for s, z in shape], material_index)


def add_medallion(builder, angle, radius, z, disk_radius=0.72, segments=24,
                  outer_material=0, inner_material=1):
    centre = world_on_gate(0.0, z, radius, angle)
    outer = []
    inner = []
    for j in range(segments):
        a = math.tau * j / segments
        outer.append(world_on_gate(disk_radius * math.cos(a), z + disk_radius * math.sin(a), radius, angle))
        inner.append(world_on_gate(disk_radius * 0.76 * math.cos(a), z + disk_radius * 0.76 * math.sin(a), radius + 0.04, angle))
    c = builder.add_vertices([centre])
    o = builder.add_vertices(outer)
    ii = builder.add_vertices(inner)
    for j in range(segments):
        j2 = (j + 1) % segments
        builder.face((c[0], o[j], o[j2]), outer_material)
        builder.face((o[j], ii[j], ii[j2], o[j2]), outer_material)
        builder.face((c[0], ii[j], ii[j2]), inner_material)


def add_pillar(builder, x, y, z0, z1, radius=0.38, segments=12, material_index=0):
    profile = [(z0, radius * 0.8), (z0 + 0.18, radius),
               (z1 - 0.28, radius * 0.84), (z1 - 0.16, radius * 1.22),
               (z1, radius * 1.22)]
    add_loft(builder, profile, segments=segments, centre=(x, y),
             band_materials=[material_index] * (len(profile) - 1), caps=True)


def add_tube_rib(builder, azimuth, radius_function, z0, z1, radius=0.16,
                 rings=30, sides=7, material_index=0):
    """Curved gold crown rib with a true cross-section rather than a rectangular block."""
    first = len(builder.vertices)
    for i in range(rings + 1):
        t = i / rings
        z = z0 + (z1 - z0) * t
        radial_r = radius_function(t)
        radial = Vector((math.cos(azimuth), math.sin(azimuth), 0.0))
        p = Vector((radial_r * math.cos(azimuth), radial_r * math.sin(azimuth), z))
        if i == 0:
            tangent = Vector((0.0, 0.0, 1.0))
        elif i == rings:
            tangent = Vector((0.0, 0.0, 1.0))
        else:
            tprev = (i - 1) / rings
            tnext = (i + 1) / rings
            zprev, znext = z0 + (z1 - z0) * tprev, z0 + (z1 - z0) * tnext
            rprev, rnext = radius_function(tprev), radius_function(tnext)
            prev = Vector((rprev * math.cos(azimuth), rprev * math.sin(azimuth), zprev))
            nxt = Vector((rnext * math.cos(azimuth), rnext * math.sin(azimuth), znext))
            tangent = (nxt - prev).normalized()
        side = tangent.cross(radial)
        if side.length < 1e-6:
            side = Vector((0.0, 1.0, 0.0))
        else:
            side.normalize()
        for j in range(sides):
            a = math.tau * j / sides
            q = p + radius * (math.cos(a) * radial + math.sin(a) * side)
            builder.vertices.append((q.x, q.y, q.z))
    for i in range(rings):
        for j in range(sides):
            j2 = (j + 1) % sides
            builder.face((first + i * sides + j,
                          first + i * sides + j2,
                          first + (i + 1) * sides + j2,
                          first + (i + 1) * sides + j), material_index)


def mark_and_hide_old_blockout(collection):
    for obj in list(collection.all_objects):
        obj["dushanbe_exclude_from_game"] = True
        obj["dushanbe_old_landmark_blockout"] = True
        obj.hide_render = True
        obj.hide_viewport = True


def main():
    collection = get_collection()
    root = bpy.data.collections[ROOT_NAME]
    # Do not leave the old cylinder-and-sphere placeholder visible or export it.
    mark_and_hide_old_blockout(collection)

    limestone = make_material("Warm_Limestone", (0.72, 0.66, 0.55), roughness=0.7)
    light_stone = make_material("Carved_Ivory", (0.87, 0.83, 0.72), roughness=0.62)
    stone_shadow = make_material("Recess_Shadow", (0.075, 0.095, 0.105), roughness=0.78)
    blue = make_material("Tower_Blue_Glazed_Tile", (0.035, 0.14, 0.26), metallic=0.12, roughness=0.3)
    blue_light = make_material("Tower_Turquoise_Inlay", (0.10, 0.42, 0.52), metallic=0.16, roughness=0.26)
    blue_glass = make_material("Observation_Gallery_Glass", (0.06, 0.18, 0.23), metallic=0.14, roughness=0.23)
    gold = make_material("Gilded_Brass", (0.83, 0.53, 0.13), metallic=0.8, roughness=0.28)
    pale_gold = make_material("Pale_Gold_Trim", (0.98, 0.78, 0.34), metallic=0.65, roughness=0.24)
    dark_blue = make_material("Blue_Inset_Shadow", (0.012, 0.045, 0.09), metallic=0.1, roughness=0.34)

    base = MeshBuilder("Istiklol_Seven_Gate_Architectural_Base",
                       [limestone, light_stone, blue, gold, stone_shadow], smooth=False)
    pavilion = MeshBuilder("Istiklol_Radial_Pavilions_And_Cupolas",
                           [limestone, light_stone, blue, gold, stone_shadow], smooth=True)
    shaft = MeshBuilder("Istiklol_121m_Twisted_Life_Tree_Shaft",
                        [blue, blue_light, light_stone, gold], smooth=True)
    goldwork = MeshBuilder("Istiklol_Gilded_Spiral_Ribs_Railings_And_Crown",
                           [gold, pale_gold], smooth=True)
    glasswork = MeshBuilder("Istiklol_Observation_Gallery",
                            [blue_glass, blue, light_stone, gold], smooth=True)
    recess = MeshBuilder("Istiklol_Seven_Arched_Gate_Recesses",
                         [stone_shadow, blue, gold], smooth=False)

    # 30 m lower architecture: large beveled multi-sided plinth, scaled from published specs.
    base_profile = [
        (0.15, 38.9), (0.65, 40.4), (1.5, 40.4), (2.2, 39.2),
        (3.0, 37.7), (4.0, 37.0), (7.0, 34.9), (10.5, 32.0),
        (14.8, 28.7), (19.0, 24.0), (23.0, 19.0), (27.0, 13.6),
        (29.0, 10.4), (30.0, 9.4),
    ]
    base_bands = [1, 3, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1]
    add_loft(base, base_profile, segments=14, band_materials=base_bands, caps=True)
    for z, radius, height, width, mat_index in [
        (0.8, 40.15, 0.26, 0.30, 1),
        (2.5, 38.25, 0.22, 0.32, 3),
        (6.8, 35.0, 0.25, 0.35, 1),
        (10.0, 32.3, 0.25, 0.32, 3),
        (14.1, 29.3, 0.28, 0.35, 1),
        (18.4, 24.8, 0.28, 0.32, 3),
        (22.6, 19.8, 0.28, 0.32, 1),
        (27.2, 13.2, 0.22, 0.28, 3),
        (29.3, 10.0, 0.18, 0.25, 7),
    ]:
        add_band(base, z, radius, height, width, segments=56, material_index=mat_index)

    # The architectural base is arranged around seven entrance axes. Each has a
    # carved-looking arch frame, dark inset, pilasters and a gilded relief medallion.
    for i in range(GATE_COUNT):
        angle = math.tau * i / GATE_COUNT + math.pi / 14
        add_arch_frame(base, angle, 37.0, 3.6, 4.6, 17.0,
                       frame_width=0.82, depth=1.2, material_index=1)
        add_arch_frame(goldwork, angle, 37.08, 3.8, 3.65, 15.5,
                       frame_width=0.22, depth=0.12, material_index=0)
        add_doorway(recess, angle, 37.12, 3.8, 3.65, 15.5, material_index=0)

        tangent = Vector((-math.sin(angle), math.cos(angle), 0.0))
        radial = Vector((math.cos(angle), math.sin(angle), 0.0))
        for side in (-1, 1):
            p = radial * 36.8 + tangent * side * 3.35
            add_pillar(base, p.x, p.y, 4.0, 17.2, radius=0.38,
                       segments=14, material_index=1)
            p2 = radial * 36.95 + tangent * side * 4.1
            add_pillar(goldwork, p2.x, p2.y, 4.5, 15.9, radius=0.12,
                       segments=10, material_index=1)
        add_medallion(base, angle, 37.28, 23.0, disk_radius=0.78,
                      segments=24, outer_material=3, inner_material=1)
        # A second medallion below the arch gives each entrance relief rhythm.
        add_medallion(base, angle, 37.36, 19.4, disk_radius=0.42,
                      segments=20, outer_material=1, inner_material=2)

        # Broad stepped approach in front of each gate, each landing a little lower.
        tangent = Vector((-math.sin(angle), math.cos(angle), 0.0))
        radial = Vector((math.cos(angle), math.sin(angle), 0.0))
        for step in range(9):
            r0 = 37.7 + step * 0.9
            r1 = r0 + 0.94
            width = 11.0 + step * 0.4
            z0 = 3.35 - step * 0.16
            z1 = z0 + 0.20
            pts = []
            for rr, ss in ((r0, -width/2), (r1, -width/2),
                           (r1, width/2), (r0, width/2)):
                p = radial * rr + tangent * ss
                pts.append((p.x, p.y, z1))
            v = base.add_vertices(pts)
            base.face(v, 1 if step % 2 == 0 else 0)
            # Narrow vertical riser face on the outward edge.
            p0 = radial * r1 + tangent * (-width/2)
            p1 = radial * r1 + tangent * (width/2)
            base.face_points([(p0.x,p0.y,z0),(p1.x,p1.y,z0),
                              (p1.x,p1.y,z1),(p0.x,p0.y,z1)], 0)

    # Seven side pavilions, layered rooflines and turquoise-and-gold cupolas.
    for i in range(GATE_COUNT):
        angle = math.tau * i / GATE_COUNT + math.pi / 14
        centre_r = 28.7
        add_radial_box(pavilion, angle, centre_r, 12.4, 13.2, 5.2, 12.0, 0)
        add_radial_box(pavilion, angle, centre_r, 11.0, 11.8, 12.0, 15.2, 1)
        add_radial_box(pavilion, angle, centre_r, 10.3, 11.0, 15.2, 16.3, 0)
        cx, cy = centre_r * math.cos(angle), centre_r * math.sin(angle)
        dome_profile = [(16.1, 4.6), (16.4, 4.9), (17.2, 4.6),
                        (18.4, 3.6), (19.4, 2.5), (20.3, 1.2), (20.8, 0.12)]
        add_loft(pavilion, dome_profile, segments=28, centre=(cx, cy),
                 band_materials=[3, 2, 2, 1, 3, 3], caps=True)
        add_band(pavilion, 16.45, 4.75, 0.22, 0.30, segments=28, material_index=3)
        # Seven columns across the front elevation, spaced like a carved arcade.
        radial = Vector((math.cos(angle), math.sin(angle), 0.0))
        tangent = Vector((-math.sin(angle), math.cos(angle), 0.0))
        for col in range(5):
            offset = (col - 2) * 2.0
            p = radial * 35.15 + tangent * offset
            add_pillar(pavilion, p.x, p.y, 5.5, 14.9,
                       radius=0.29, segments=12, material_index=1)
        # Dark window bays inserted between the columns.
        for bay in (-3.0, -1.0, 1.0, 3.0):
            p = radial * 35.25 + tangent * bay
            add_radial_box(recess, angle, 35.25, 0.72, 0.08, 7.0, 13.5, 0)
        add_band(pavilion, 12.15, 35.4, 0.18, 0.24, segments=14, material_index=3)

    # Upper 91 m: fluted, gently twisted blue shaft; the radius profile is taken
    # from the visual silhouette, while the total measured height is fixed at 121 m.
    shaft_profile = [
        (29.5, 9.6), (31.0, 9.25), (34.0, 8.55), (39.0, 7.9),
        (47.0, 6.75), (57.0, 6.0), (69.0, 5.55), (80.0, 5.6),
        (88.5, 6.2), (92.0, 7.1), (96.5, 7.6), (99.0, 6.45),
        (104.0, 5.1), (109.2, 4.2), (112.3, 4.65),
    ]
    shaft_bands = []
    for _ring in range(len(shaft_profile) - 1):
        shaft_bands.append(0)
    # Alternating sector materials make the shaft read as glazed tile rather than a plain tube.
    first = len(shaft.vertices)
    segments = 56
    for z, radius in shaft_profile:
        twist = 0.016 * (z - 30.0)
        for j in range(segments):
            a = math.tau * j / segments + twist
            shaft.vertices.append((radius * math.cos(a), radius * math.sin(a), z))
    for ring in range(len(shaft_profile) - 1):
        for j in range(segments):
            j2 = (j + 1) % segments
            material_index = 1 if (j // 3) % 5 == 0 else (0 if (j % 4) else 2)
            shaft.face((first + ring*segments + j, first + ring*segments + j2,
                        first + (ring+1)*segments + j2, first + (ring+1)*segments + j),
                       material_index)
    shaft.face(tuple(first + j for j in reversed(range(segments))), 0)
    last = first + (len(shaft_profile)-1)*segments
    shaft.face(tuple(last + j for j in range(segments)), 0)

    # Gold spiral ribs follow the changing tower radius; narrower companions make
    # the helical feature visually rich without using a single flat diagonal stripe.
    for i in range(4):
        add_helix(goldwork, shaft_profile, i * math.tau / 4, turns=1.55,
                  z0=34.0, z1=109.4, width=0.66, radial_offset=0.18,
                  samples=320, material_index=0)
    for z in (34.5, 41.0, 49.5, 58.5, 69.8, 80.5, 88.8, 99.3, 105.5, 109.4):
        r = radius_at(z, shaft_profile) + 0.19
        add_band(goldwork, z, r, 0.18, width=0.16, segments=56, material_index=1)

    # Circular observation level near 94 m, based on public reports describing
    # a viewing gallery on the 14th floor at around 94 m.
    gallery_profile = [(92.4, 7.1), (92.8, 8.5), (93.2, 9.15),
                       (96.0, 9.15), (96.5, 8.6), (97.0, 7.5)]
    add_loft(glasswork, gallery_profile, segments=56,
             band_materials=[2, 3, 0, 3, 2], caps=False)
    add_band(goldwork, 93.05, 9.2, 0.24, width=0.28, segments=56, material_index=1)
    add_band(goldwork, 96.0, 9.2, 0.20, width=0.25, segments=56, material_index=0)
    for j in range(56):
        a = math.tau * j / 56
        cx, cy = 9.18 * math.cos(a), 9.18 * math.sin(a)
        add_pillar(goldwork, cx, cy, 93.2, 95.95, radius=0.055,
                   segments=6, material_index=1)

    # Crown is a layered gilded volume with twelve curved rising ribs rather than a sphere.
    crown_profile = [(111.4, 4.35), (112.2, 4.9), (113.4, 5.65),
                     (114.4, 5.85), (115.3, 5.45), (116.4, 4.8),
                     (117.6, 4.0), (118.6, 3.05), (119.7, 2.0),
                     (120.7, 0.8), (121.0, 0.18)]
    add_loft(goldwork, crown_profile, segments=56,
             band_materials=[0, 1, 0, 1, 0, 1, 0, 1, 0, 1], caps=True)
    for j in range(12):
        az = math.tau * j / 12
        def crown_curve(t):
            # Start at the lower circlet, flare out into a crown lobe, then return to the tip.
            return 4.3 * (1.0 - t) + 0.22 * t + 1.25 * math.sin(math.pi * t)
        add_tube_rib(goldwork, az, crown_curve, 113.4, 120.9,
                     radius=0.19, rings=36, sides=8, material_index=1)
    add_pillar(goldwork, 0.0, 0.0, 119.2, 121.0, radius=0.23,
               segments=16, material_index=1)

    created = [
        base.build(collection), pavilion.build(collection), shaft.build(collection),
        goldwork.build(collection), glasswork.build(collection), recess.build(collection),
    ]
    created = [obj for obj in created if obj is not None]
    root = bpy.data.collections[ROOT_NAME]
    scene = bpy.context.scene
    scene["dushanbe_monument_model_type"] = "original_parametric_reference_based"
    scene["dushanbe_monument_reference_source"] = "Tajikistan Academy of Architecture and Construction; Khovar news agency"
    scene["dushanbe_monument_target_height_m"] = OVERALL_HEIGHT_M
    scene["dushanbe_monument_lower_section_m"] = LOWER_SECTION_HEIGHT_M
    scene["dushanbe_monument_gate_count"] = GATE_COUNT
    scene["dushanbe_monument_mesh_objects"] = len(created)

    # Ensure preview has reasonable metric bounds and the original low-detail placeholder is excluded.
    bpy.context.view_layer.update()
    actual_top = max((obj.matrix_world @ Vector(corner)).z
                     for obj in created for corner in obj.bound_box)
    if actual_top < 120.5 or actual_top > 122.5:
        raise RuntimeError(f"Monument top should be near 121 m, got {actual_top:.2f} m")
    print("DUSHANBE_ISTIKLOL_MONUMENT_DETAIL_OK")
    print(f"Created {len(created)} detailed mesh objects; target height {OVERALL_HEIGHT_M} m")
    print("Lower architectural section: 30 m; seven entrance motifs; observation ring; twisted shaft; crown.")
    print("Original reference-based reconstruction; ornament/material patterns remain approximate, not photogrammetry.")


if __name__ == "__main__":
    main()
