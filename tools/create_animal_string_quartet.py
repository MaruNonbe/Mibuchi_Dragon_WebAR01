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
MAT_BRASS = None
MAT_SILVER = None
MAT_DRUM = None
MAT_SPECIES = {}
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
    elif species == "dog":
        cone("dog_ear_L", (-0.22, -0.03, 1.98), 0.09, 0.035, 0.34, fur_mat, parent, rot=(0.75, 0.42, 0.18))
        cone("dog_ear_R", (0.22, -0.03, 1.98), 0.09, 0.035, 0.34, fur_mat, parent, rot=(0.75, -0.42, -0.18))
        cylinder_between("dog_tail", (0.0, 0.40, 1.02), (0.24, 0.70, 1.34), 0.055, fur_mat, parent)
    elif species == "squirrel":
        sphere("squirrel_ear_L", (-0.22, -0.02, 2.08), (0.080, 0.050, 0.105), fur_mat, parent)
        sphere("squirrel_ear_R", (0.22, -0.02, 2.08), (0.080, 0.050, 0.105), fur_mat, parent)
        cone("squirrel_tail", (0.0, 0.55, 1.30), 0.23, 0.11, 1.05, fur_mat, parent, rot=(0.70, 0.0, 0.0))
        sphere("squirrel_tail_tip", (0.0, 0.70, 1.78), (0.16, 0.12, 0.18), accent_mat, parent)
    elif species == "panda":
        sphere("panda_ear_L", (-0.25, -0.02, 2.06), (0.11, 0.07, 0.11), MAT_DARK, parent)
        sphere("panda_ear_R", (0.25, -0.02, 2.06), (0.11, 0.07, 0.11), MAT_DARK, parent)
        sphere("panda_eye_patch_L", (-0.105, -0.283, 1.93), (0.075, 0.018, 0.060), MAT_DARK, parent, segments=16)
        sphere("panda_eye_patch_R", (0.105, -0.283, 1.93), (0.075, 0.018, 0.060), MAT_DARK, parent, segments=16)
    elif species == "penguin":
        cone("penguin_beak", (0, -0.41, 1.83), 0.040, 0.012, 0.18, MAT_GOLD, parent, vertices=16, rot=(math.radians(90), 0, 0))
        cylinder_between("penguin_flipper_L", (-0.26, -0.02, 1.32), (-0.52, -0.12, 1.02), 0.045, fur_mat, parent)
        cylinder_between("penguin_flipper_R", (0.26, -0.02, 1.32), (0.52, -0.12, 1.02), 0.045, fur_mat, parent)
    elif species == "tanuki":
        cone("tanuki_ear_L", (-0.22, -0.02, 2.08), 0.11, 0.02, 0.26, fur_mat, parent, rot=(0.2, 0.45, 0.0))
        cone("tanuki_ear_R", (0.22, -0.02, 2.08), 0.11, 0.02, 0.26, fur_mat, parent, rot=(0.2, -0.45, 0.0))
        sphere("tanuki_mask_L", (-0.115, -0.285, 1.925), (0.075, 0.016, 0.055), MAT_DARK, parent, segments=16)
        sphere("tanuki_mask_R", (0.115, -0.285, 1.925), (0.075, 0.016, 0.055), MAT_DARK, parent, segments=16)
        sphere("tanuki_tail", (0.0, 0.48, 1.03), (0.16, 0.22, 0.18), fur_mat, parent)
    elif species in {"deer", "kamoshika"}:
        sphere(f"{species}_ear_L", (-0.25, -0.02, 2.02), (0.080, 0.045, 0.13), fur_mat, parent)
        sphere(f"{species}_ear_R", (0.25, -0.02, 2.02), (0.080, 0.045, 0.13), fur_mat, parent)
        for side, x in [("L", -0.12), ("R", 0.12)]:
            cylinder_between(f"{species}_antler_{side}_main", (x, -0.01, 2.12), (x * 1.35, -0.02, 2.40), 0.018, MAT_WOOD_DARK, parent, vertices=10)
            cylinder_between(f"{species}_antler_{side}_branch", (x * 1.20, -0.02, 2.28), (x * 1.90, -0.02, 2.36), 0.012, MAT_WOOD_DARK, parent, vertices=8)
    elif species == "bird":
        cone("bird_beak", (0, -0.41, 1.84), 0.045, 0.010, 0.20, MAT_GOLD, parent, vertices=16, rot=(math.radians(90), 0, 0))
        cone("bird_crest", (0, -0.01, 2.17), 0.050, 0.010, 0.22, fur_mat, parent, vertices=12, rot=(0.25, 0, 0))
    elif species == "frog":
        sphere("frog_eye_bump_L", (-0.13, -0.10, 2.08), (0.095, 0.070, 0.080), fur_mat, parent)
        sphere("frog_eye_bump_R", (0.13, -0.10, 2.08), (0.095, 0.070, 0.080), fur_mat, parent)
        curve_between("frog_smile", (-0.13, -0.37, 1.78), (0.13, -0.37, 1.78), MAT_DARK, 0.006, parent)
    elif species == "sheep":
        for i, x in enumerate([-0.18, 0, 0.18]):
            sphere(f"sheep_wool_top_{i}", (x, -0.02, 2.12), (0.10, 0.075, 0.09), accent_mat, parent, segments=16)
        sphere("sheep_ear_L", (-0.25, -0.02, 2.00), (0.075, 0.045, 0.115), fur_mat, parent)
        sphere("sheep_ear_R", (0.25, -0.02, 2.00), (0.075, 0.045, 0.115), fur_mat, parent)
    return head


def create_body(parent, species, fur_mat, accent_mat):
    sphere(f"{species}_torso", (0, 0, 1.15), (0.31, 0.23, 0.48), fur_mat, parent)
    sphere(f"{species}_belly", (0, -0.205, 1.12), (0.19, 0.055, 0.30), accent_mat, parent)
    sphere(f"{species}_neck", (0, 0, 1.54), (0.13, 0.12, 0.14), fur_mat, parent)

    cylinder_between(f"{species}_leg_L", (-0.12, 0.02, 0.76), (-0.18, -0.02, 0.28), 0.07, fur_mat, parent)
    cylinder_between(f"{species}_leg_R", (0.12, 0.02, 0.76), (0.18, -0.02, 0.28), 0.07, fur_mat, parent)
    sphere(f"{species}_foot_L", (-0.20, -0.12, 0.18), (0.11, 0.18, 0.055), fur_mat, parent)
    sphere(f"{species}_foot_R", (0.20, -0.12, 0.18), (0.11, 0.18, 0.055), fur_mat, parent)


def create_arms(parent, species, fur_mat, instrument=None):
    wind = instrument in {"flute", "clarinet", "trumpet", "trombone"}
    percussion = instrument in {"snare", "tambourine", "marimba", "bass_drum"}
    cello = instrument == "cello"
    if cello:
        cylinder_between(f"{species}_left_upper_arm", (-0.24, -0.03, 1.45), (-0.43, -0.25, 1.11), 0.045, fur_mat, parent)
        cylinder_between(f"{species}_left_forearm", (-0.43, -0.25, 1.11), (-0.20, -0.46, 0.96), 0.040, fur_mat, parent)
        cylinder_between(f"{species}_right_upper_arm", (0.24, -0.03, 1.45), (0.48, -0.20, 1.14), 0.045, fur_mat, parent)
        cylinder_between(f"{species}_right_forearm", (0.48, -0.20, 1.14), (0.62, -0.82, 1.06), 0.040, fur_mat, parent)
        sphere(f"{species}_left_paw", (-0.20, -0.46, 0.96), (0.06, 0.055, 0.06), fur_mat, parent)
        sphere(f"{species}_right_paw", (0.62, -0.82, 1.06), (0.06, 0.055, 0.06), fur_mat, parent)
    elif wind:
        cylinder_between(f"{species}_left_upper_arm", (-0.24, -0.03, 1.42), (-0.38, -0.30, 1.55), 0.045, fur_mat, parent)
        cylinder_between(f"{species}_left_forearm", (-0.38, -0.30, 1.55), (-0.22, -0.56, 1.68), 0.040, fur_mat, parent)
        cylinder_between(f"{species}_right_upper_arm", (0.24, -0.03, 1.42), (0.38, -0.30, 1.55), 0.045, fur_mat, parent)
        cylinder_between(f"{species}_right_forearm", (0.38, -0.30, 1.55), (0.22, -0.56, 1.68), 0.040, fur_mat, parent)
        sphere(f"{species}_left_paw", (-0.22, -0.56, 1.68), (0.06, 0.055, 0.06), fur_mat, parent)
        sphere(f"{species}_right_paw", (0.22, -0.56, 1.68), (0.06, 0.055, 0.06), fur_mat, parent)
    elif percussion:
        cylinder_between(f"{species}_left_upper_arm", (-0.24, -0.03, 1.42), (-0.40, -0.25, 1.28), 0.045, fur_mat, parent)
        cylinder_between(f"{species}_left_forearm", (-0.40, -0.25, 1.28), (-0.24, -0.54, 1.34), 0.040, fur_mat, parent)
        cylinder_between(f"{species}_right_upper_arm", (0.24, -0.03, 1.42), (0.40, -0.25, 1.28), 0.045, fur_mat, parent)
        cylinder_between(f"{species}_right_forearm", (0.40, -0.25, 1.28), (0.24, -0.54, 1.34), 0.040, fur_mat, parent)
        sphere(f"{species}_left_paw", (-0.24, -0.54, 1.34), (0.06, 0.055, 0.06), fur_mat, parent)
        sphere(f"{species}_right_paw", (0.24, -0.54, 1.34), (0.06, 0.055, 0.06), fur_mat, parent)
    else:
        cylinder_between(f"{species}_left_upper_arm", (-0.24, -0.03, 1.42), (-0.47, -0.24, 1.30), 0.045, fur_mat, parent)
        cylinder_between(f"{species}_left_forearm", (-0.47, -0.24, 1.30), (-0.22, -0.47, 1.43), 0.040, fur_mat, parent)
        cylinder_between(f"{species}_right_upper_arm", (0.24, -0.03, 1.42), (0.45, -0.36, 1.49), 0.045, fur_mat, parent)
        cylinder_between(f"{species}_right_forearm", (0.45, -0.36, 1.49), (0.50, -0.76, 1.57), 0.040, fur_mat, parent)
        sphere(f"{species}_left_paw", (-0.22, -0.47, 1.43), (0.06, 0.055, 0.06), fur_mat, parent)
        sphere(f"{species}_right_paw", (0.50, -0.76, 1.57), (0.06, 0.055, 0.06), fur_mat, parent)


def create_string_instrument(parent, name, kind):
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


def create_wind_instrument(parent, name, kind, phase=0):
    inst = empty(f"{name}_{kind}_wind_anim", parent=parent)
    inst.location = (0.00, -0.61, 1.70)
    inst.rotation_euler = (math.radians(88), 0, 0)

    if kind == "flute":
        inst.location = (0.00, -0.60, 1.74)
        inst.rotation_euler = (math.radians(92), 0, math.radians(2))
        cylinder_between(f"{name}_flute_body", (-0.46, 0, 0), (0.46, 0, 0), 0.030, MAT_SILVER, inst, vertices=24)
        cylinder_between(f"{name}_flute_lip_plate", (-0.09, -0.018, 0.018), (0.05, -0.018, 0.018), 0.014, MAT_GOLD, inst, vertices=16)
        for i, x in enumerate([-0.28, -0.16, -0.04, 0.08, 0.20, 0.32]):
            sphere(f"{name}_flute_key_{i}", (x, -0.032, 0.025), (0.026, 0.010, 0.026), MAT_DARK, inst, segments=12)
    elif kind == "clarinet":
        inst.location = (0.48, -0.43, 1.82)
        inst.rotation_euler = (math.radians(112), 0, math.radians(-8))
        cylinder_between(f"{name}_clarinet_body", (-0.42, 0, 0), (0.38, 0, 0), 0.036, MAT_DARK, inst, vertices=24)
        cone(f"{name}_clarinet_bell", (0.48, 0, 0), 0.075, 0.036, 0.16, MAT_DARK, inst, vertices=24, rot=(0, math.radians(90), 0))
        cube(f"{name}_clarinet_reed", (-0.48, 0.015, 0), (0.055, 0.010, 0.018), MAT_WOOD_DARK, inst)
        for i, x in enumerate([-0.22, -0.09, 0.04, 0.17, 0.30]):
            sphere(f"{name}_clarinet_key_{i}", (x, -0.038, 0.028), (0.023, 0.008, 0.023), MAT_SILVER, inst, segments=12)
    elif kind == "trumpet":
        inst.location = (0.48, -0.43, 1.82)
        inst.rotation_euler = (math.radians(90), 0, math.radians(-2))
        cylinder_between(f"{name}_trumpet_mouthpiece", (-0.48, 0, 0), (-0.35, 0, 0), 0.020, MAT_SILVER, inst, vertices=20)
        cylinder_between(f"{name}_trumpet_pipe", (-0.35, 0, 0), (0.28, 0, 0), 0.030, MAT_BRASS, inst, vertices=24)
        cone(f"{name}_trumpet_bell", (0.48, 0, 0), 0.18, 0.04, 0.28, MAT_BRASS, inst, vertices=32, rot=(0, math.radians(90), 0))
        for i, x in enumerate([-0.10, 0.02, 0.14]):
            cylinder(f"{name}_trumpet_valve_{i}", (x, -0.03, 0.105), 0.025, 0.16, MAT_BRASS, inst, vertices=16, rot=(math.radians(90), 0, 0))
        bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.018, major_segments=32, minor_segments=8, location=(-0.18, 0.0, -0.05))
        loop = bpy.context.object
        loop.name = f"{name}_trumpet_loop"
        loop.parent = inst
        loop.rotation_euler = (math.radians(90), 0, 0)
        loop.data.materials.append(MAT_BRASS)
    else:
        inst.location = (0.56, -0.43, 1.82)
        inst.rotation_euler = (math.radians(92), 0, math.radians(-8))
        cylinder_between(f"{name}_trombone_mouthpiece", (-0.56, 0, 0.01), (-0.44, -0.01, 0.03), 0.022, MAT_SILVER, inst, vertices=20)
        cylinder_between(f"{name}_trombone_slide_outer", (-0.44, -0.04, 0.05), (0.42, -0.04, 0.05), 0.018, MAT_BRASS, inst, vertices=16)
        cylinder_between(f"{name}_trombone_slide_inner", (-0.44, 0.04, -0.05), (0.42, 0.04, -0.05), 0.018, MAT_BRASS, inst, vertices=16)
        cone(f"{name}_trombone_bell", (0.55, 0, 0.08), 0.16, 0.045, 0.25, MAT_BRASS, inst, vertices=32, rot=(0, math.radians(90), 0))

    base_loc = inst.location.copy()
    for frame, lift in [(1, 0), (42, 0.035), (84, -0.010), (126, 0.030), (160, 0)]:
        inst.location = (base_loc.x, base_loc.y, base_loc.z + lift)
        inst.keyframe_insert(data_path="location", frame=frame + phase)
    finalize_animation(inst)
    return inst


def percussion_hit_target(kind, side):
    x = -0.11 if side == "L" else 0.11
    if kind == "marimba":
        return (x * 1.9, -0.72, 1.18)
    if kind == "bass_drum":
        return (x * 1.1, -0.73, 1.02)
    if kind == "tambourine":
        return (0.18 if side == "R" else -0.18, -0.55, 1.43)
    return (x, -0.68, 1.18)


def create_percussion_sticks(parent, name, kind, phase=0):
    for side, paw in [("L", (-0.24, -0.54, 1.34)), ("R", (0.24, -0.54, 1.34))]:
        target = Vector(percussion_hit_target(kind, side))
        paw_vec = Vector(paw)
        local_target = target - paw_vec
        stick = empty(f"{name}_{kind}_stick_{side}_hand_anim", loc=paw, parent=parent)
        cylinder_between(f"{name}_{kind}_stick_{side}", (0, 0, 0), local_target, 0.012, MAT_BOW, stick, vertices=12)
        sphere(f"{name}_{kind}_stick_tip_{side}", local_target, (0.035, 0.035, 0.035), MAT_GOLD, stick, segments=12)
        base_rot = stick.rotation_euler.copy()
        swing = 0.22 if side == "L" else -0.22
        for frame, rx, rz in [(1, -0.18, 0), (32, 0.10, swing), (64, -0.10, -swing * 0.5), (96, 0.12, swing * 0.8), (128, -0.16, -swing * 0.4), (160, -0.18, 0)]:
            stick.rotation_euler = (base_rot.x + rx, base_rot.y, base_rot.z + rz)
            stick.keyframe_insert(data_path="rotation_euler", frame=frame + phase)
        finalize_animation(stick)


def create_percussion_instrument(parent, name, kind, phase=0):
    inst = empty(f"{name}_{kind}_percussion_anim", parent=parent)

    if kind == "snare":
        inst.location = (0.03, -0.58, 1.08)
        cylinder(f"{name}_snare_shell", (0, 0, 0), 0.23, 0.18, MAT_DRUM, inst, vertices=48, rot=(math.radians(90), 0, 0))
        cylinder(f"{name}_snare_top", (0, -0.095, 0), 0.235, 0.012, MAT_CREAM, inst, vertices=48, rot=(math.radians(90), 0, 0))
    elif kind == "tambourine":
        inst.location = (0.04, -0.55, 1.38)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=0.030, major_segments=48, minor_segments=10, location=(0, 0, 0))
        ring = bpy.context.object
        ring.name = f"{name}_tambourine_ring"
        ring.parent = inst
        ring.rotation_euler = (math.radians(90), 0, 0)
        ring.data.materials.append(MAT_WOOD)
        for i in range(8):
            angle = i * math.tau / 8
            sphere(f"{name}_tambourine_jingle_{i}", (math.cos(angle) * 0.22, 0, math.sin(angle) * 0.22), (0.035, 0.008, 0.035), MAT_SILVER, inst, segments=12)
    elif kind == "marimba":
        inst.location = (0.02, -0.72, 0.92)
        for i, x in enumerate([-0.32, -0.20, -0.08, 0.04, 0.16, 0.28]):
            cube(f"{name}_marimba_bar_{i}", (x, 0, 0.22), (0.045, 0.12, 0.025), MAT_WOOD, inst)
            cylinder_between(f"{name}_marimba_pipe_{i}", (x, 0, -0.12), (x, 0, 0.15), 0.018, MAT_BRASS, inst, vertices=16)
        cylinder_between(f"{name}_marimba_rail_front", (-0.42, -0.13, 0.08), (0.40, -0.13, 0.08), 0.014, MAT_DARK, inst, vertices=12)
        cylinder_between(f"{name}_marimba_rail_back", (-0.42, 0.13, 0.08), (0.40, 0.13, 0.08), 0.014, MAT_DARK, inst, vertices=12)
    else:
        inst.location = (0.00, -0.62, 1.00)
        cylinder(f"{name}_bass_drum_shell", (0, 0, 0), 0.34, 0.20, MAT_DRUM, inst, vertices=48, rot=(math.radians(90), 0, 0))
        cylinder(f"{name}_bass_drum_head", (0, -0.105, 0), 0.345, 0.012, MAT_CREAM, inst, vertices=48, rot=(math.radians(90), 0, 0))

    create_percussion_sticks(parent, name, kind, phase=phase)

    base_rot = inst.rotation_euler.copy()
    for frame, rz in [(1, -0.05), (38, 0.06), (76, -0.04), (114, 0.05), (160, -0.05)]:
        inst.rotation_euler = (base_rot.x, base_rot.y, base_rot.z + rz)
        inst.keyframe_insert(data_path="rotation_euler", frame=frame + phase)
    finalize_animation(inst)
    return inst


def create_instrument(parent, name, kind, phase=0):
    if kind in {"violin", "viola", "cello"}:
        return create_string_instrument(parent, name, kind)
    if kind in {"flute", "clarinet", "trumpet", "trombone"}:
        return create_wind_instrument(parent, name, kind, phase=phase)
    return create_percussion_instrument(parent, name, kind, phase=phase)


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


def create_character(species, fur_mat, accent_mat, instrument, loc, rot_z, phase, scale=1.0):
    root = empty(f"{species}_quartet_player", loc=loc, rot=(0, 0, math.radians(rot_z)))
    root.scale = (scale, scale, scale)
    create_body(root, species, fur_mat, accent_mat)
    head = create_face(root, species, fur_mat, accent_mat)
    create_arms(root, species, fur_mat, instrument=instrument)
    create_instrument(root, species, instrument, phase=phase)
    if instrument in {"violin", "viola", "cello"}:
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
        ("fox", (-1.65, -2.05), (-2.65, -0.62)),
        ("rabbit", (1.65, -2.05), (2.65, -0.62)),
        ("bear", (-3.15, 1.45), (-1.35, 0.88)),
        ("cat", (3.15, 1.45), (1.35, 0.88)),
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


def create_station_arrival_event(station_name="長井駅"):
    event = empty("flower_nagai_line_arrival_event")
    arrival_text = f"{station_name}到着"

    # Keep the platform cue low so children can stand visually between the animals.
    cube("platform_yellow_safety_line", (0, -2.05, 0.035), (2.8, 0.035, 0.018), MAT_GOLD, event)

    # Station sign: each station GLB carries its own station name for WebAR preview checks.
    sign = empty("nagai_station_sign_group", loc=(0, 1.04, 2.38), parent=event)
    cube("nagai_station_sign_board", (0, 0, 0), (1.15, 0.035, 0.30), MAT_WHITE, sign)
    cube("nagai_station_sign_top_line", (0, -0.04, 0.25), (1.12, 0.012, 0.025), MAT_STATION_BLUE, sign)
    cube("nagai_station_sign_bottom_line", (0, -0.04, -0.25), (1.12, 0.012, 0.025), MAT_STATION_RED, sign)
    text_object("station_name_label", station_name, (0, -0.085, 0.045), 0.20, MAT_DARK, sign, rot=(math.radians(90), 0, 0))
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
        f"アナウンス: {arrival_text}",
        (0, -1.72, 2.28),
        0.13,
        MAT_CREAM,
        event,
        rot=(math.radians(70), 0, 0),
    )
    animate_dancing_text(announcement, phase=0, bounce=0.045, twist=0.035)

    # Dancing title characters are separated so each letter can move independently.
    title_group = empty("dancing_title_nagai_arrival", loc=(0, -1.48, 3.02), parent=event)
    chars = list(arrival_text)
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
    bpy.ops.mesh.primitive_torus_add(major_radius=0.68, minor_radius=0.014, major_segments=96, minor_segments=8, location=(0, -0.22, 0.045))
    spot = bpy.context.object
    spot.name = "web_ar_player_standing_spot_between_animals"
    spot.data.materials.append(MAT_GOLD)
    spot.parent = event
    text_object("web_ar_center_label", "ここで一緒に演奏", (0, -0.22, 0.075), 0.075, MAT_CREAM, event, rot=(math.radians(90), 0, 0))


def setup_materials():
    global MAT_SPECIES
    global MAT_FOX, MAT_RABBIT, MAT_BEAR, MAT_CAT, MAT_CREAM, MAT_DARK
    global MAT_PINK, MAT_WOOD, MAT_WOOD_DARK, MAT_STRING, MAT_BOW, MAT_STAGE, MAT_GOLD
    global MAT_STATION_BLUE, MAT_STATION_RED, MAT_WHITE, MAT_TRAIN_GREEN
    global MAT_BRASS, MAT_SILVER, MAT_DRUM

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
    MAT_BRASS = make_mat("warm_brass_metal", (0.95, 0.62, 0.18, 1), 0.28, 0.55)
    MAT_SILVER = make_mat("soft_silver_metal", (0.78, 0.82, 0.86, 1), 0.22, 0.65)
    MAT_DRUM = make_mat("festival_drum_shell", (0.72, 0.16, 0.12, 1), 0.38)
    MAT_SPECIES = {
        "fox": MAT_FOX,
        "rabbit": MAT_RABBIT,
        "bear": MAT_BEAR,
        "cat": MAT_CAT,
        "dog": make_mat("dog_caramel_fur", (0.78, 0.48, 0.23, 1)),
        "squirrel": make_mat("squirrel_cinnamon_fur", (0.82, 0.35, 0.12, 1)),
        "panda": make_mat("panda_white_fur", (0.94, 0.91, 0.84, 1)),
        "penguin": make_mat("penguin_blue_black", (0.05, 0.10, 0.14, 1)),
        "tanuki": make_mat("tanuki_gray_brown_fur", (0.42, 0.34, 0.25, 1)),
        "deer": make_mat("deer_warm_brown_fur", (0.63, 0.39, 0.18, 1)),
        "bird": make_mat("bird_sky_blue_feathers", (0.32, 0.58, 0.82, 1)),
        "kamoshika": make_mat("kamoshika_smoky_gray_fur", (0.48, 0.50, 0.47, 1)),
        "frog": make_mat("frog_fresh_green_skin", (0.20, 0.62, 0.28, 1)),
        "sheep": make_mat("sheep_warm_gray_face", (0.56, 0.52, 0.48, 1)),
    }


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


VARIANT_CONFIGS = {
    "strings": {
        "filename": "nagai_station_strings.glb",
        "players": [
            ("fox", "violin", (-1.95, -0.62, 0), 28, 0),
            ("rabbit", "violin", (1.95, -0.62, 0), -28, 12),
            ("bear", "viola", (-1.35, 0.88, 0), 18, 24),
            ("cat", "cello", (1.35, 0.88, 0), -18, 36),
        ],
    },
    "winds": {
        "filename": "nagai_station_winds.glb",
        "players": [
            ("cat", "flute", (-1.95, -0.62, 0), 26, 0),
            ("rabbit", "clarinet", (1.95, -0.62, 0), -26, 12),
            ("fox", "trumpet", (-1.35, 0.88, 0), 18, 24),
            ("bear", "trombone", (1.35, 0.88, 0), -18, 36),
        ],
    },
    "percussion": {
        "filename": "nagai_station_percussion.glb",
        "players": [
            ("bear", "snare", (-1.95, -0.62, 0), 26, 0),
            ("fox", "tambourine", (1.95, -0.62, 0), -26, 12),
            ("rabbit", "marimba", (-1.35, 0.88, 0), 18, 24),
            ("cat", "bass_drum", (1.35, 0.88, 0), -18, 36),
        ],
    },
}

STATION_VARIANT_CONFIGS = {
    "akayu": ("akayu_strings_fox_rabbit.glb", "赤湯駅", [
        ("fox", "violin", (-1.95, -0.62, 0), 28, 0),
        ("rabbit", "violin", (1.95, -0.62, 0), -28, 12),
        ("deer", "viola", (-1.35, 0.88, 0), 18, 24),
        ("cat", "cello", (1.35, 0.88, 0), -18, 36),
    ]),
    "nanyo_city_hall": ("nanyo_city_hall_cats_woodwinds.glb", "南陽市役所駅", [
        ("cat", "flute", (-1.95, -0.62, 0), 26, 0),
        ("cat", "clarinet", (1.95, -0.62, 0), -26, 12),
        ("bird", "flute", (-1.35, 0.88, 0), 18, 24),
        ("rabbit", "clarinet", (1.35, 0.88, 0), -18, 36),
    ]),
    "miyauchi": ("miyauchi_dogs_brass.glb", "宮内駅", [
        ("dog", "trumpet", (-1.95, -0.62, 0), 26, 0),
        ("dog", "trombone", (1.95, -0.62, 0), -26, 12),
        ("bear", "trumpet", (-1.35, 0.88, 0), 18, 24),
        ("fox", "trombone", (1.35, 0.88, 0), -18, 36),
    ]),
    "orihata": ("orihata_squirrels_percussion.glb", "おりはた駅", [
        ("squirrel", "snare", (-1.95, -0.62, 0), 26, 0),
        ("squirrel", "tambourine", (1.95, -0.62, 0), -26, 12),
        ("frog", "marimba", (-1.35, 0.88, 0), 18, 24),
        ("tanuki", "bass_drum", (1.35, 0.88, 0), -18, 36),
    ]),
    "ringo": ("ringo_panda_penguin_jazz.glb", "梨郷駅", [
        ("panda", "trumpet", (-1.95, -0.62, 0), 26, 0),
        ("penguin", "clarinet", (1.95, -0.62, 0), -26, 12),
        ("cat", "flute", (-1.35, 0.88, 0), 18, 24),
        ("bear", "trombone", (1.35, 0.88, 0), -18, 36),
    ]),
    "nishi_otsuka": ("nishi_otsuka_tanuki_taiko.glb", "西大塚駅", [
        ("tanuki", "bass_drum", (-1.95, -0.62, 0), 26, 0),
        ("tanuki", "snare", (1.95, -0.62, 0), -26, 12),
        ("fox", "tambourine", (-1.35, 0.88, 0), 18, 24),
        ("rabbit", "marimba", (1.35, 0.88, 0), -18, 36),
    ]),
    "imaizumi": ("imaizumi_deer_flutes.glb", "今泉駅", [
        ("deer", "flute", (-1.95, -0.62, 0), 26, 0),
        ("deer", "clarinet", (1.95, -0.62, 0), -26, 12),
        ("bird", "flute", (-1.35, 0.88, 0), 18, 24),
        ("cat", "clarinet", (1.35, 0.88, 0), -18, 36),
    ]),
    "tokiniwa": ("tokiniwa_bears_low_brass.glb", "時庭駅", [
        ("bear", "trombone", (-1.95, -0.62, 0), 26, 0),
        ("bear", "trumpet", (1.95, -0.62, 0), -26, 12),
        ("dog", "trombone", (-1.35, 0.88, 0), 18, 24),
        ("panda", "trumpet", (1.35, 0.88, 0), -18, 36),
    ]),
    "minami_nagai": ("minami_nagai_rabbit_clarinets.glb", "南長井駅", [
        ("rabbit", "clarinet", (-1.95, -0.62, 0), 26, 0),
        ("rabbit", "flute", (1.95, -0.62, 0), -26, 12),
        ("cat", "clarinet", (-1.35, 0.88, 0), 18, 24),
        ("bird", "flute", (1.35, 0.88, 0), -18, 36),
    ]),
    "nagai": ("nagai_main_string_quartet.glb", "長井駅", [
        ("fox", "violin", (-1.95, -0.62, 0), 28, 0),
        ("rabbit", "violin", (1.95, -0.62, 0), -28, 12),
        ("bear", "viola", (-1.35, 0.88, 0), 18, 24),
        ("cat", "cello", (1.35, 0.88, 0), -18, 36),
    ]),
    "ayame_koen": ("ayame_koen_birds_piccolo.glb", "あやめ公園駅", [
        ("bird", "flute", (-1.95, -0.62, 0), 26, 0),
        ("bird", "clarinet", (1.95, -0.62, 0), -26, 12),
        ("penguin", "flute", (-1.35, 0.88, 0), 18, 24),
        ("rabbit", "clarinet", (1.35, 0.88, 0), -18, 36),
    ]),
    "uzen_narita": ("uzen_narita_fox_sax_band.glb", "羽前成田駅", [
        ("fox", "trumpet", (-1.95, -0.62, 0), 26, 0),
        ("fox", "clarinet", (1.95, -0.62, 0), -26, 12),
        ("cat", "flute", (-1.35, 0.88, 0), 18, 24),
        ("dog", "trombone", (1.35, 0.88, 0), -18, 36),
    ]),
    "shirousagi": ("shirousagi_white_rabbit_bells.glb", "白兎駅", [
        ("rabbit", "tambourine", (-1.95, -0.62, 0), 26, 0),
        ("rabbit", "snare", (1.95, -0.62, 0), -26, 12),
        ("sheep", "marimba", (-1.35, 0.88, 0), 18, 24),
        ("panda", "bass_drum", (1.35, 0.88, 0), -18, 36),
    ]),
    "koguwa": ("koguwa_kamoshika_horns.glb", "蚕桑駅", [
        ("kamoshika", "trumpet", (-1.95, -0.62, 0), 26, 0),
        ("kamoshika", "trombone", (1.95, -0.62, 0), -26, 12),
        ("deer", "trumpet", (-1.35, 0.88, 0), 18, 24),
        ("dog", "trombone", (1.35, 0.88, 0), -18, 36),
    ]),
    "ayukai": ("ayukai_frogs_marimba.glb", "鮎貝駅", [
        ("frog", "marimba", (-1.95, -0.62, 0), 26, 0),
        ("frog", "snare", (1.95, -0.62, 0), -26, 12),
        ("bird", "tambourine", (-1.35, 0.88, 0), 18, 24),
        ("tanuki", "bass_drum", (1.35, 0.88, 0), -18, 36),
    ]),
    "shikinosato": ("shikinosato_sheep_trombones.glb", "四季の郷駅", [
        ("sheep", "trombone", (-1.95, -0.62, 0), 26, 0),
        ("sheep", "trumpet", (1.95, -0.62, 0), -26, 12),
        ("deer", "trombone", (-1.35, 0.88, 0), 18, 24),
        ("panda", "trumpet", (1.35, 0.88, 0), -18, 36),
    ]),
    "arato": ("arato_finale_all_stars.glb", "荒砥駅", [
        ("fox", "violin", (-2.25, -0.58, 0), 30, 0, 0.74),
        ("rabbit", "trumpet", (2.25, -0.58, 0), -30, 12, 0.74),
        ("bear", "bass_drum", (-1.35, 0.42, 0), 14, 24, 0.64),
        ("cat", "flute", (1.35, 0.42, 0), -14, 36, 0.64),
        ("dog", "trombone", (-2.70, 0.42, 0), 22, 48, 0.62),
        ("squirrel", "tambourine", (2.70, 0.42, 0), -22, 60, 0.62),
        ("frog", "marimba", (-1.85, 1.18, 0), 15, 72, 0.58),
        ("tanuki", "snare", (1.85, 1.18, 0), -15, 84, 0.58),
        ("deer", "viola", (-2.75, 1.86, 0), 14, 96, 0.54),
        ("bird", "flute", (-1.68, 2.05, 0), 9, 108, 0.54),
        ("panda", "trumpet", (-0.62, 2.18, 0), 4, 120, 0.54),
        ("penguin", "clarinet", (0.62, 2.18, 0), -4, 132, 0.54),
        ("kamoshika", "trombone", (1.68, 2.05, 0), -9, 144, 0.54),
        ("sheep", "bass_drum", (2.75, 1.86, 0), -14, 156, 0.54),
    ]),
}

for station_key, (filename, station_name, players) in STATION_VARIANT_CONFIGS.items():
    VARIANT_CONFIGS[f"station_{station_key}"] = {
        "filename": os.path.join("stations", filename),
        "station_name": station_name,
        "players": players,
    }


def species_material(species):
    return MAT_SPECIES[species]


def resolve_variant_config(variant):
    config = VARIANT_CONFIGS[variant]
    return {
        "filename": config["filename"],
        "station_name": config.get("station_name", "長井駅"),
        "players": [
            (
                entry[0],
                species_material(entry[0]),
                MAT_CREAM,
                entry[1],
                entry[2],
                entry[3],
                entry[4],
                entry[5] if len(entry) > 5 else 1.0,
            )
            for entry in config["players"]
        ],
    }


def export_webar_glb(filename):
    if not EXPORT_GLTF_FOR_WEBAR:
        return

    base_dir = os.path.join(PROJECT_DIR, "ARDragon", "Mibuchi_Dragon_WebAR01")
    if not os.path.isdir(base_dir):
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        except NameError:
            base_dir = os.getcwd()

    export_dir = os.path.join(base_dir, "gps-webar", "assets")
    os.makedirs(export_dir, exist_ok=True)
    export_path = os.path.join(export_dir, filename)
    os.makedirs(os.path.dirname(export_path), exist_ok=True)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=export_path,
        export_format="GLB",
        use_selection=True,
        export_animations=True,
        export_apply=True,
    )
    print(f"Exported GPS WebAR GLB: {export_path}")


def build_scene(variant):
    clear_scene()
    setup_materials()
    config = resolve_variant_config(variant)
    setup_render()
    create_stage()
    create_backdrop()
    create_station_arrival_event(config["station_name"])

    for player in config["players"]:
        create_character(*player)

    create_lighting_and_camera()

    bpy.context.scene.frame_set(FRAME_START)
    export_webar_glb(config["filename"])
    print(f"Created animated animal {variant} scene.")


def main():
    requested = os.environ.get("NAGAI_AR_VARIANT", "all")
    if requested == "all":
        variants = ["strings", "winds", "percussion"]
    elif requested == "station_all":
        variants = [f"station_{key}" for key in STATION_VARIANT_CONFIGS.keys()]
    else:
        variants = [requested]
    for variant in variants:
        if variant not in VARIANT_CONFIGS:
            raise ValueError(f"Unknown NAGAI_AR_VARIANT: {variant}")
        build_scene(variant)


if __name__ == "__main__":
    main()
