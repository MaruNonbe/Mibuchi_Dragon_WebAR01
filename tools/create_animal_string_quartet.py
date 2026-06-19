import math
import os
import bpy
from mathutils import Vector


# Animal string quartet generator for Blender.
# Run this script in Blender's Text Editor, or:
# blender --python create_animal_string_quartet.py


FRAME_START = 1
FRAME_END = 160
EXPORT_GLTF_FOR_WEBAR = True
PROJECT_DIR = r"C:\Users\user\Documents\ARDragon"


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def make_mat(name, color, roughness=0.55, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


MAT_FOX = None
MAT_RABBIT = None
MAT_BEAR = None
MAT_CAT = None
MAT_CREAM = None
MAT_DARK = None
MAT_PINK = None
MAT_WOOD = None
MAT_WOOD_DARK = None
MAT_STRING = None
MAT_BOW = None
MAT_STAGE = None
MAT_GOLD = None
MAT_STATION_BLUE = None
MAT_STATION_RED = None
MAT_WHITE = None
MAT_TRAIN_GREEN = None
JAPANESE_FONT = None


def assign_mat(obj, mat):
    obj.data.materials.append(mat)
    return obj


def shade_smooth(obj):
    if obj and hasattr(obj.data, "polygons"):
        for poly in obj.data.polygons:
            poly.use_smooth = True
    return obj


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    if parent:
        obj.parent = parent
    obj.location = loc
    obj.rotation_euler = rot
    return obj


def sphere(name, loc, scale, mat, parent=None, segments=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=16, location=(0, 0, 0))
    obj = bpy.context.object
    obj.name = name
    if parent:
        obj.parent = parent
    obj.location = loc
    obj.scale = scale
    assign_mat(obj, mat)
    return shade_smooth(obj)


def cube(name, loc, scale, mat, parent=None):
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    obj = bpy.context.object
    obj.name = name
    if parent:
        obj.parent = parent
    obj.location = loc
    obj.scale = scale
    assign_mat(obj, mat)
    return obj


def cylinder(name, loc, radius, depth, mat, parent=None, vertices=32, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=(0, 0, 0))
    obj = bpy.context.object
    obj.name = name
    if parent:
        obj.parent = parent
    obj.location = loc
    obj.rotation_euler = rot
    assign_mat(obj, mat)
    return shade_smooth(obj)


def cone(name, loc, radius1, radius2, depth, mat, parent=None, vertices=32, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices,
        radius1=radius1,
        radius2=radius2,
        depth=depth,
        location=(0, 0, 0),
    )
    obj = bpy.context.object
    obj.name = name
    if parent:
        obj.parent = parent
    obj.location = loc
    obj.rotation_euler = rot
    assign_mat(obj, mat)
    return shade_smooth(obj)


def cylinder_between(name, start, end, radius, mat, parent=None, vertices=24):
    start = Vector(start)
    end = Vector(end)
    mid = (start + end) * 0.5
    direction = end - start
    length = direction.length
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=length, location=(0, 0, 0))
    obj = bpy.context.object
    obj.name = name
    if parent:
        obj.parent = parent
    obj.location = mid
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    assign_mat(obj, mat)
    return shade_smooth(obj)


def curve_between(name, start, end, mat, bevel_depth=0.006, parent=None):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 1
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(1)
    spline.points[0].co = (start[0], start[1], start[2], 1)
    spline.points[1].co = (end[0], end[1], end[2], 1)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    if parent:
        obj.parent = parent
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)
    obj.data.materials.append(mat)
    return obj


def get_japanese_font():
    global JAPANESE_FONT
    if JAPANESE_FONT is not None:
        return JAPANESE_FONT

    candidates = [
        r"C:\Windows\Fonts\YuGothM.ttc",
        r"C:\Windows\Fonts\YuGothR.ttc",
        r"C:\Windows\Fonts\msgothic.ttc",
        r"C:\Windows\Fonts\meiryo.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                JAPANESE_FONT = bpy.data.fonts.load(path)
                return JAPANESE_FONT
            except RuntimeError:
                pass
    return None


def text_object(name, body, loc, size, mat, parent=None, rot=(math.radians(74), 0, 0)):
    curve = bpy.data.curves.new(name, "FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.006
    font = get_japanese_font()
    if font:
        curve.font = font
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    if parent:
        obj.parent = parent
    obj.location = loc
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    return obj


def animate_dancing_text(obj, phase=0, bounce=0.12, twist=0.11):
    base_loc = obj.location.copy()
    base_rot = obj.rotation_euler.copy()
    for frame, z, rz in [(1, 0, 0), (28, bounce, twist), (56, 0.02, -twist), (84, bounce * 0.8, twist), (112, 0, 0)]:
        obj.location = (base_loc.x, base_loc.y, base_loc.z + z)
        obj.rotation_euler = (base_rot.x, base_rot.y, base_rot.z + rz)
        obj.keyframe_insert(data_path="location", frame=frame + phase)
        obj.keyframe_insert(data_path="rotation_euler", frame=frame + phase)
    finalize_animation(obj)


def finalize_animation(obj, add_cycles=True):
    if not obj.animation_data or not obj.animation_data.action:
        return

    action = obj.animation_data.action
    fcurves = getattr(action, "fcurves", None)
    if not fcurves:
        return

    for fcurve in fcurves:
        for key in fcurve.keyframe_points:
            key.interpolation = "BEZIER"
        if add_cycles:
            try:
                fcurve.modifiers.new(type="CYCLES")
            except RuntimeError:
                pass


def add_keyframed_cycle(obj, data_path, frames_values):
    for frame, value in frames_values:
        setattr(obj, data_path, value)
        obj.keyframe_insert(data_path=data_path, frame=frame)
    finalize_animation(obj)


def animate_loop(obj, loc_amp=0.045, rot_amp=0.05, phase=0):
    f1 = FRAME_START + phase
    f2 = 40 + phase
    f3 = 80 + phase
    f4 = 120 + phase
    f5 = FRAME_END + phase
    base_loc = obj.location.copy()
    base_rot = obj.rotation_euler.copy()
    for frame, z, ry in [
        (f1, 0, 0),
        (f2, loc_amp, rot_amp),
        (f3, 0, 0),
        (f4, loc_amp * 0.7, -rot_amp),
        (f5, 0, 0),
    ]:
        obj.location = (base_loc.x, base_loc.y, base_loc.z + z)
        obj.rotation_euler = (base_rot.x, base_rot.y + ry, base_rot.z)
        obj.keyframe_insert(data_path="location", frame=frame)
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    finalize_animation(obj)


def create_face(parent, species, fur_mat, accent_mat):
    head = sphere(f"{species}_head", (0, 0, 1.85), (0.34, 0.30, 0.32), fur_mat, parent)
    muzzle = sphere(f"{species}_muzzle", (0, -0.265, 1.80), (0.18, 0.11, 0.10), accent_mat, parent)
    nose = sphere(f"{species}_nose", (0, -0.36, 1.84), (0.045, 0.025, 0.035), MAT_DARK, parent, segments=16)
    eye_l = sphere(f"{species}_eye_L", (-0.105, -0.26, 1.93), (0.035, 0.022, 0.035), MAT_DARK, parent, segments=16)
    eye_r = sphere(f"{species}_eye_R", (0.105, -0.26, 1.93), (0.035, 0.022, 0.035), MAT_DARK, parent, segments=16)
    eye_hi_l = sphere(f"{species}_eye_highlight_L", (-0.115, -0.278, 1.945), (0.012, 0.006, 0.012), MAT_CREAM, parent, segments=8)
    eye_hi_r = sphere(f"{species}_eye_highlight_R", (0.095, -0.278, 1.945), (0.012, 0.006, 0.012), MAT_CREAM, parent, segments=8)

    if species == "fox":
        cone("fox_ear_L", (-0.22, -0.02, 2.12), 0.12, 0.02, 0.36, fur_mat, parent, rot=(0.25, 0.55, 0.0))
        cone("fox_ear_R", (0.22, -0.02, 2.12), 0.12, 0.02, 0.36, fur_mat, parent, rot=(0.25, -0.55, 0.0))
        cone("fox_tail", (0.0, 0.47, 1.05), 0.13, 0.27, 0.95, fur_mat, parent, rot=(1.25, 0.0, 0.0))
        sphere("fox_tail_tip", (0.0, 0.82, 1.36), (0.18, 0.13, 0.17), accent_mat, parent)
    elif species == "rabbit":
        cylinder("rabbit_ear_L", (-0.14, -0.02, 2.22), 0.055, 0.62, fur_mat, parent, rot=(0.2, 0.24, 0))
        cylinder("rabbit_ear_R", (0.14, -0.02, 2.22), 0.055, 0.62, fur_mat, parent, rot=(0.2, -0.24, 0))
        sphere("rabbit_tail", (0.0, 0.38, 1.05), (0.13, 0.13, 0.13), accent_mat, parent)
    elif species == "bear":
        sphere("bear_ear_L", (-0.25, -0.02, 2.04), (0.105, 0.07, 0.105), fur_mat, parent)
        sphere("bear_ear_R", (0.25, -0.02, 2.04), (0.105, 0.07, 0.105), fur_mat, parent)
    elif species == "cat":
        cone("cat_ear_L", (-0.21, -0.02, 2.10), 0.105, 0.01, 0.30, fur_mat, parent, rot=(0.18, 0.46, 0.0))
        cone("cat_ear_R", (0.21, -0.02, 2.10), 0.105, 0.01, 0.30, fur_mat, parent, rot=(0.18, -0.46, 0.0))
        cylinder_between("cat_tail", (0, 0.38, 0.93), (0.22, 0.62, 1.45), 0.045, fur_mat, parent)
        for i in range(3):
            z = 1.80 + i * 0.035
            curve_between(f"cat_whisker_L_{i}", (-0.06, -0.35, z), (-0.32, -0.47, z + 0.02), MAT_DARK, 0.004, parent)
            curve_between(f"cat_whisker_R_{i}", (0.06, -0.35, z), (0.32, -0.47, z + 0.02), MAT_DARK, 0.004, parent)
    return head


def create_body(parent, species, fur_mat, accent_mat):
    sphere(f"{species}_torso", (0, 0, 1.15), (0.31, 0.23, 0.48), fur_mat, parent)
    sphere(f"{species}_belly", (0, -0.205, 1.12), (0.19, 0.055, 0.30), accent_mat, parent)
    sphere(f"{species}_neck", (0, 0, 1.54), (0.13, 0.12, 0.14), fur_mat, parent)

    cylinder_between(f"{species}_leg_L", (-0.12, 0.02, 0.76), (-0.18, -0.02, 0.28), 0.07, fur_mat, parent)
    cylinder_between(f"{species}_leg_R", (0.12, 0.02, 0.76), (0.18, -0.02, 0.28), 0.07, fur_mat, parent)
    sphere(f"{species}_foot_L", (-0.20, -0.12, 0.18), (0.11, 0.18, 0.055), fur_mat, parent)
    sphere(f"{species}_foot_R", (0.20, -0.12, 0.18), (0.11, 0.18, 0.055), fur_mat, parent)


def create_arms(parent, species, fur_mat, cello=False):
    if cello:
        cylinder_between(f"{species}_left_upper_arm", (-0.24, -0.03, 1.45), (-0.43, -0.25, 1.11), 0.045, fur_mat, parent)
        cylinder_between(f"{species}_left_forearm", (-0.43, -0.25, 1.11), (-0.20, -0.46, 0.96), 0.040, fur_mat, parent)
        cylinder_between(f"{species}_right_upper_arm", (0.24, -0.03, 1.45), (0.48, -0.20, 1.14), 0.045, fur_mat, parent)
        cylinder_between(f"{species}_right_forearm", (0.48, -0.20, 1.14), (0.62, -0.82, 1.06), 0.040, fur_mat, parent)
        sphere(f"{species}_left_paw", (-0.20, -0.46, 0.96), (0.06, 0.055, 0.06), fur_mat, parent)
        sphere(f"{species}_right_paw", (0.62, -0.82, 1.06), (0.06, 0.055, 0.06), fur_mat, parent)
    else:
        cylinder_between(f"{species}_left_upper_arm", (-0.24, -0.03, 1.42), (-0.47, -0.24, 1.30), 0.045, fur_mat, parent)
        cylinder_between(f"{species}_left_forearm", (-0.47, -0.24, 1.30), (-0.22, -0.47, 1.43), 0.040, fur_mat, parent)
        cylinder_between(f"{species}_right_upper_arm", (0.24, -0.03, 1.42), (0.45, -0.36, 1.49), 0.045, fur_mat, parent)
        cylinder_between(f"{species}_right_forearm", (0.45, -0.36, 1.49), (0.50, -0.76, 1.57), 0.040, fur_mat, parent)
        sphere(f"{species}_left_paw", (-0.22, -0.47, 1.43), (0.06, 0.055, 0.06), fur_mat, parent)
        sphere(f"{species}_right_paw", (0.50, -0.76, 1.57), (0.06, 0.055, 0.06), fur_mat, parent)


def create_instrument(parent, name, kind):
    inst = empty(f"{name}_{kind}", parent=parent)
    if kind == "violin":
        inst.location = (0.05, -0.50, 1.45)
        inst.rotation_euler = (math.radians(80), 0, math.radians(-8))
        scale = 1.0
    elif kind == "viola":
        inst.location = (0.06, -0.50, 1.43)
        inst.rotation_euler = (math.radians(80), 0, math.radians(-8))
        scale = 1.12
    else:
        inst.location = (0.03, -0.46, 0.92)
        inst.rotation_euler = (math.radians(88), 0, math.radians(-2))
        scale = 1.55

    sphere(f"{name}_{kind}_upper_bout", (0, 0, 0.13 * scale), (0.16 * scale, 0.055 * scale, 0.20 * scale), MAT_WOOD, inst)
    sphere(f"{name}_{kind}_lower_bout", (0, 0, -0.13 * scale), (0.20 * scale, 0.060 * scale, 0.22 * scale), MAT_WOOD, inst)
    sphere(f"{name}_{kind}_waist_L", (-0.13 * scale, -0.01, 0.0), (0.07 * scale, 0.035 * scale, 0.12 * scale), MAT_WOOD_DARK, inst)
    sphere(f"{name}_{kind}_waist_R", (0.13 * scale, -0.01, 0.0), (0.07 * scale, 0.035 * scale, 0.12 * scale), MAT_WOOD_DARK, inst)
    cylinder_between(f"{name}_{kind}_neck", (0, 0, 0.27 * scale), (0, 0, 0.70 * scale), 0.025 * scale, MAT_WOOD_DARK, inst)
    cube(f"{name}_{kind}_fingerboard", (0, 0.045 * scale, 0.38 * scale), (0.035 * scale, 0.014 * scale, 0.24 * scale), MAT_DARK, inst)
    cube(f"{name}_{kind}_bridge", (0, 0.078 * scale, 0.03 * scale), (0.11 * scale, 0.012 * scale, 0.055 * scale), MAT_CREAM, inst)

    for idx, x in enumerate([-0.055, -0.018, 0.018, 0.055]):
        curve_between(
            f"{name}_{kind}_string_{idx + 1}",
            (x * scale, 0.088 * scale, -0.25 * scale),
            (x * 0.45 * scale, 0.088 * scale, 0.70 * scale),
            MAT_STRING,
            0.0035 * scale,
            inst,
        )

    if kind == "cello":
        cylinder_between(f"{name}_cello_endpin", (0, 0.02, -0.44 * scale), (0, 0.02, -0.80 * scale), 0.01, MAT_STRING, inst)

    return inst


def create_bow(parent, name, cello=False, phase=0):
    bow = empty(f"{name}_bow_anim", parent=parent)
    if cello:
        bow.location = (0.12, -0.82, 1.06)
        bow.rotation_euler = (math.radians(88), 0, math.radians(-2))
        length = 1.02
    else:
        bow.location = (0.08, -0.73, 1.57)
        bow.rotation_euler = (math.radians(80), 0, math.radians(-8))
        length = 0.82

    cylinder_between(f"{name}_bow_stick", (-length * 0.5, 0, 0), (length * 0.5, 0, 0), 0.009, MAT_BOW, bow, vertices=12)
    curve_between(f"{name}_bow_hair", (-length * 0.47, 0.018, 0), (length * 0.47, 0.018, 0), MAT_CREAM, 0.004, bow)
    sphere(f"{name}_bow_frog", (-length * 0.45, 0, 0), (0.035, 0.018, 0.022), MAT_DARK, bow, segments=12)

    base_loc = bow.location.copy()
    base_rot = bow.rotation_euler.copy()
    for frame, offset, roll in [
        (FRAME_START, -0.14, -0.10),
        (40, 0.15, 0.08),
        (80, -0.12, -0.06),
        (120, 0.16, 0.10),
        (FRAME_END, -0.14, -0.10),
    ]:
        f = frame + phase
        bow.location = (base_loc.x + offset, base_loc.y, base_loc.z + math.sin(frame * 0.12) * 0.025)
        bow.rotation_euler = (base_rot.x, base_rot.y + roll, base_rot.z)
        bow.keyframe_insert(data_path="location", frame=f)
        bow.keyframe_insert(data_path="rotation_euler", frame=f)

    finalize_animation(bow)
    return bow


def add_music_notes(parent, name, phase=0):
    notes = []
    for i, (x, z, size) in enumerate([(-0.30, 2.28, 0.08), (0.00, 2.43, 0.07), (0.31, 2.34, 0.06)]):
        curve = bpy.data.curves.new(f"{name}_note_{i}", "FONT")
        curve.body = "♪"
        curve.align_x = "CENTER"
        curve.align_y = "CENTER"
        curve.size = size
        obj = bpy.data.objects.new(f"{name}_note_{i}", curve)
        bpy.context.collection.objects.link(obj)
        obj.parent = parent
        obj.location = (x, -0.64, z)
        obj.rotation_euler = (math.radians(74), 0, 0)
        obj.data.materials.append(MAT_GOLD)
        notes.append(obj)
        base = obj.location.copy()
        for frame, dz in [(1, 0), (55, 0.12), (110, 0.02), (160, 0.15)]:
            obj.location = (base.x, base.y - dz * 0.4, base.z + dz)
            obj.keyframe_insert(data_path="location", frame=frame + phase)
        finalize_animation(obj)
    return notes


def create_character(species, fur_mat, accent_mat, instrument, loc, rot_z, phase):
    root = empty(f"{species}_quartet_player", loc=loc, rot=(0, 0, math.radians(rot_z)))
    create_body(root, species, fur_mat, accent_mat)
    head = create_face(root, species, fur_mat, accent_mat)
    create_arms(root, species, fur_mat, cello=(instrument == "cello"))
    create_instrument(root, species, instrument)
    create_bow(root, species, cello=(instrument == "cello"), phase=phase)
    add_music_notes(root, species, phase=phase)
    animate_loop(root, phase=phase)

    # Head nods independently, suggesting musical phrasing.
    base_rot = head.rotation_euler.copy()
    for frame, rx in [(1, 0), (45, 0.10), (90, -0.05), (135, 0.08), (160, 0)]:
        head.rotation_euler = (base_rot.x + rx, base_rot.y, base_rot.z)
        head.keyframe_insert(data_path="rotation_euler", frame=frame + phase)
    finalize_animation(head)
    return root


def create_stage():
    cylinder("round_wood_stage", (0, 0, -0.035), 3.25, 0.07, MAT_STAGE, vertices=96)
    for r, name in [(2.65, "outer_ring"), (1.72, "inner_ring")]:
        bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.012, major_segments=128, minor_segments=8, location=(0, 0, 0.01))
        obj = bpy.context.object
        obj.name = name
        assign_mat(obj, MAT_WOOD_DARK)

    # Music sheets are on each stand's local -Y side, so rotate that side toward the player.
    stand_specs = [
        ("fox", (-0.92, -1.05), (-1.55, -0.62)),
        ("rabbit", (0.92, -1.05), (1.55, -0.62)),
        ("bear", (-0.88, 0.23), (-1.55, 0.88)),
        ("cat", (0.88, 0.23), (1.55, 0.88)),
    ]
    for i, (player_name, stand_xy, player_xy) in enumerate(stand_specs):
        x, y = stand_xy
        dx = player_xy[0] - x
        dy = player_xy[1] - y
        rot = math.atan2(dx, -dy)
        stand = empty(f"music_stand_{i + 1}", loc=(x, y, 0), rot=(0, 0, rot))
        stand.name = f"{player_name}_music_stand"
        cylinder(f"{player_name}_music_stand_pole", (0, 0, 0.60), 0.015, 1.02, MAT_DARK, stand, vertices=12)
        cube(f"{player_name}_music_stand_desk", (0, -0.035, 1.12), (0.30, 0.025, 0.17), MAT_DARK, stand)
        cube(f"{player_name}_music_sheet", (0, -0.062, 1.15), (0.24, 0.006, 0.13), MAT_CREAM, stand)
        for line in range(4):
            cube(
                f"{player_name}_music_staff_{line}",
                (0, -0.070, 1.105 + line * 0.030),
                (0.19, 0.003, 0.004),
                MAT_STRING,
                stand,
            )


def create_lighting_and_camera():
    bpy.ops.object.light_add(type="AREA", location=(0, -3.6, 4.2))
    key = bpy.context.object
    key.name = "large_softbox_key_light"
    key.data.energy = 650
    key.data.size = 5.0

    bpy.ops.object.light_add(type="POINT", location=(-2.6, 2.2, 2.8))
    rim = bpy.context.object
    rim.name = "warm_rim_light"
    rim.data.energy = 110
    rim.data.color = (1.0, 0.78, 0.50)

    bpy.ops.object.camera_add(location=(0, -5.2, 2.35), rotation=(math.radians(67), 0, 0))
    cam = bpy.context.object
    bpy.context.scene.camera = cam
    cam.name = "quartet_camera"
    cam.data.lens = 32
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 5.2
    cam.data.dof.aperture_fstop = 5.6


def create_backdrop():
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 1.85, 2.05), rotation=(math.radians(90), 0, 0))
    wall = bpy.context.object
    wall.name = "warm_concert_backdrop"
    assign_mat(wall, make_mat("backdrop_warm_gray", (0.30, 0.31, 0.34, 1), 0.8))

    for i, x in enumerate([-2.4, -1.2, 0, 1.2, 2.4]):
        cylinder(f"subtle_backdrop_panel_{i}", (x, 1.80, 2.05), 0.018, 3.4, MAT_GOLD, vertices=16, rot=(math.radians(90), 0, 0))


def create_station_arrival_event():
    event = empty("flower_nagai_line_arrival_event")

    # Platform edge and train front in the background: enough detail for WebAR without heavy geometry.
    cube("platform_yellow_safety_line", (0, -2.05, 0.035), (2.8, 0.035, 0.018), MAT_GOLD, event)
    cube("flower_nagai_train_body", (0, 1.33, 0.70), (1.65, 0.16, 0.52), MAT_WHITE, event)
    cube("flower_nagai_train_window_band", (0, 1.16, 0.86), (1.36, 0.025, 0.16), MAT_STATION_BLUE, event)
    cube("flower_nagai_train_lower_red_line", (0, 1.145, 0.47), (1.52, 0.018, 0.035), MAT_STATION_RED, event)
    cube("flower_nagai_train_green_line", (0, 1.14, 0.39), (1.52, 0.018, 0.028), MAT_TRAIN_GREEN, event)
    sphere("train_headlight_L", (-0.55, 1.12, 0.56), (0.055, 0.014, 0.055), MAT_GOLD, event, segments=16)
    sphere("train_headlight_R", (0.55, 1.12, 0.56), (0.055, 0.014, 0.055), MAT_GOLD, event, segments=16)

    # Station sign: Japanese text is intentionally used because the scene is for Nagai Station.
    sign = empty("nagai_station_sign_group", loc=(0, 0.98, 1.72), parent=event)
    cube("nagai_station_sign_board", (0, 0, 0), (1.15, 0.035, 0.30), MAT_WHITE, sign)
    cube("nagai_station_sign_top_line", (0, -0.04, 0.25), (1.12, 0.012, 0.025), MAT_STATION_BLUE, sign)
    cube("nagai_station_sign_bottom_line", (0, -0.04, -0.25), (1.12, 0.012, 0.025), MAT_STATION_RED, sign)
    text_object("station_name_nagai", "長井駅", (0, -0.085, 0.045), 0.20, MAT_DARK, sign, rot=(math.radians(90), 0, 0))
    text_object("station_line_flower_nagai", "フラワー長井線", (0, -0.085, -0.135), 0.065, MAT_STATION_BLUE, sign, rot=(math.radians(90), 0, 0))

    # Announcement speaker and sound-wave rings.
    speaker = empty("arrival_announcement_speaker", loc=(-1.72, -1.42, 1.85), rot=(0, 0, math.radians(-16)), parent=event)
    cube("speaker_box", (0, 0, 0), (0.18, 0.10, 0.14), MAT_DARK, speaker)
    cone("speaker_horn", (0.23, -0.02, 0), 0.20, 0.07, 0.28, MAT_DARK, speaker, vertices=32, rot=(0, math.radians(90), 0))
    for i, radius in enumerate([0.22, 0.34, 0.46]):
        bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=0.006, major_segments=48, minor_segments=8, location=(-1.36 + i * 0.04, -1.49, 1.85))
        ring = bpy.context.object
        ring.name = f"announcement_sound_wave_{i + 1}"
        ring.rotation_euler = (0, math.radians(90), 0)
        ring.parent = event
        ring.data.materials.append(MAT_GOLD)
        for frame, scale in [(1, 0.65), (35, 1.10), (70, 0.75), (105, 1.20), (140, 0.70)]:
            ring.scale = (scale, scale, scale)
            ring.keyframe_insert(data_path="scale", frame=frame + i * 8)
        finalize_animation(ring)

    announcement = text_object(
        "announcement_caption",
        "アナウンス: 長井駅到着",
        (0, -1.72, 2.28),
        0.13,
        MAT_CREAM,
        event,
        rot=(math.radians(70), 0, 0),
    )
    animate_dancing_text(announcement, phase=0, bounce=0.045, twist=0.035)

    # Dancing title characters are separated so each letter can move independently.
    title_group = empty("dancing_title_nagai_arrival", loc=(0, -1.48, 2.72), parent=event)
    chars = list("長井駅到着")
    spacing = 0.30
    start_x = -spacing * (len(chars) - 1) * 0.5
    for i, char in enumerate(chars):
        mat = MAT_STATION_RED if i in (0, 3, 4) else MAT_GOLD
        obj = text_object(
            f"dancing_arrival_char_{i + 1}_{char}",
            char,
            (start_x + i * spacing, 0, 0),
            0.26,
            mat,
            title_group,
            rot=(math.radians(70), 0, 0),
        )
        animate_dancing_text(obj, phase=i * 5, bounce=0.16, twist=0.13)

    # A marked open spot for the WebAR viewer/player to stand between the quartet members.
    bpy.ops.mesh.primitive_torus_add(major_radius=0.48, minor_radius=0.012, major_segments=96, minor_segments=8, location=(0, -0.30, 0.045))
    spot = bpy.context.object
    spot.name = "web_ar_player_standing_spot_between_animals"
    spot.data.materials.append(MAT_GOLD)
    spot.parent = event
    text_object("web_ar_center_label", "ここで一緒に演奏", (0, -0.30, 0.075), 0.075, MAT_CREAM, event, rot=(math.radians(90), 0, 0))


def setup_materials():
    global MAT_FOX, MAT_RABBIT, MAT_BEAR, MAT_CAT, MAT_CREAM, MAT_DARK
    global MAT_PINK, MAT_WOOD, MAT_WOOD_DARK, MAT_STRING, MAT_BOW, MAT_STAGE, MAT_GOLD
    global MAT_STATION_BLUE, MAT_STATION_RED, MAT_WHITE, MAT_TRAIN_GREEN

    MAT_FOX = make_mat("fox_orange_fur", (0.95, 0.36, 0.10, 1))
    MAT_RABBIT = make_mat("rabbit_ivory_fur", (0.86, 0.82, 0.74, 1))
    MAT_BEAR = make_mat("bear_chocolate_fur", (0.37, 0.20, 0.11, 1))
    MAT_CAT = make_mat("cat_blue_gray_fur", (0.34, 0.43, 0.52, 1))
    MAT_CREAM = make_mat("cream_muzzle_and_sheets", (0.98, 0.91, 0.76, 1))
    MAT_DARK = make_mat("soft_black_details", (0.015, 0.014, 0.014, 1))
    MAT_PINK = make_mat("soft_pink_inner_ears", (0.95, 0.48, 0.56, 1))
    MAT_WOOD = make_mat("varnished_violin_wood", (0.74, 0.31, 0.08, 1), 0.35)
    MAT_WOOD_DARK = make_mat("dark_violin_wood", (0.25, 0.10, 0.035, 1), 0.45)
    MAT_STRING = make_mat("dark_strings", (0.03, 0.025, 0.020, 1), 0.4)
    MAT_BOW = make_mat("bow_warm_wood", (0.44, 0.20, 0.08, 1), 0.42)
    MAT_STAGE = make_mat("stage_deep_teal", (0.08, 0.30, 0.29, 1), 0.72)
    MAT_GOLD = make_mat("soft_stage_gold", (1.0, 0.72, 0.23, 1), 0.38, 0.15)
    MAT_STATION_BLUE = make_mat("flower_nagai_station_blue", (0.05, 0.28, 0.72, 1), 0.42)
    MAT_STATION_RED = make_mat("arrival_event_red", (0.88, 0.06, 0.06, 1), 0.40)
    MAT_WHITE = make_mat("train_and_sign_white", (0.96, 0.96, 0.92, 1), 0.48)
    MAT_TRAIN_GREEN = make_mat("flower_train_green", (0.08, 0.56, 0.34, 1), 0.45)


def setup_render():
    scene = bpy.context.scene
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    scene.frame_set(FRAME_START)
    scene.render.fps = 24
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = 64
    scene.world = bpy.data.worlds.new("concert_hall_world") if scene.world is None else scene.world
    scene.world.color = (0.025, 0.027, 0.03)


def export_webar_glb():
    if not EXPORT_GLTF_FOR_WEBAR:
        return

    base_dir = PROJECT_DIR
    if not os.path.isdir(base_dir):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            base_dir = os.getcwd()

    export_dir = os.path.join(base_dir, "gps-webar", "assets")
    os.makedirs(export_dir, exist_ok=True)
    export_path = os.path.join(export_dir, "nagai_station_quartet.glb")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=export_path,
        export_format="GLB",
        use_selection=True,
        export_animations=True,
        export_apply=True,
    )
    print(f"Exported GPS WebAR GLB: {export_path}")


def main():
    clear_scene()
    setup_materials()
    setup_render()
    create_stage()
    create_backdrop()
    create_station_arrival_event()

    create_character("fox", MAT_FOX, MAT_CREAM, "violin", (-1.55, -0.62, 0), 26, 0)
    create_character("rabbit", MAT_RABBIT, MAT_CREAM, "violin", (1.55, -0.62, 0), -26, 12)
    create_character("bear", MAT_BEAR, MAT_CREAM, "viola", (-1.55, 0.88, 0), 18, 24)
    create_character("cat", MAT_CAT, MAT_CREAM, "cello", (1.55, 0.88, 0), -18, 36)

    create_lighting_and_camera()

    bpy.context.scene.frame_set(FRAME_START)
    export_webar_glb()
    print("Created animated animal string quartet scene.")


if __name__ == "__main__":
    main()
