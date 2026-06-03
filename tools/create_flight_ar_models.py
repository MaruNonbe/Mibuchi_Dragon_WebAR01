import json
import math
import os

import bpy
from mathutils import Euler, Quaternion, Vector


PROJECT_ROOT = r"C:\Users\user\Documents\ARDragon\ARDragon\Mibuchi_Dragon_WebAR01"
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
SOURCE_GLB = os.path.join(ASSETS_DIR, "dragon_web.glb")
FLIGHT_GLB = os.path.join(ASSETS_DIR, "dragon_web_flight.glb")
FLIGHT_USDZ = os.path.join(ASSETS_DIR, "dragon_web_flight.usdz")
BACKUP_DIR = os.path.join(ASSETS_DIR, "backup")
REPORT_PATH = os.path.join(BACKUP_DIR, "flight_ar_model_report.json")

ACTION_NAME = "Flight_Loop_12s"
FPS = 24
DURATION_SECONDS = 12.0
FRAME_START = 0
FRAME_END = int(DURATION_SECONDS * FPS)

ROUTE_WIDTH = 5.2
ROUTE_DEPTH = 3.4
BASE_HEIGHT = 3.25
HEIGHT_AMPLITUDE = 0.45
FLOOR_SHADOW_RADIUS = 0.95


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def create_shadow_anchor():
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=FLOOR_SHADOW_RADIUS, depth=0.006, location=(0, 0, 0.003))
    anchor = bpy.context.object
    anchor.name = "FlightFloorShadowAnchor"
    anchor.scale = (1.55, 0.78, 1.0)

    mat = bpy.data.materials.new("FlightFloorShadowAnchor_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.015, 0.025, 0.025, 0.16)
        bsdf.inputs["Alpha"].default_value = 0.16
        bsdf.inputs["Roughness"].default_value = 0.92
    mat.blend_method = "BLEND"
    anchor.data.materials.append(mat)
    return anchor


def find_armature():
    armatures = [obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"]
    if not armatures:
        raise RuntimeError("No armature found in GLB.")
    return armatures[0]


def remove_old_actions():
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)


def route_position(theta):
    x = (ROUTE_WIDTH * 0.5) * math.cos(theta)
    y = -3.25 + (ROUTE_DEPTH * 0.5) * math.sin(theta)
    z = BASE_HEIGHT + HEIGHT_AMPLITUDE * math.sin(theta + 0.75) + 0.12 * math.sin(theta * 2.0 - 0.4)
    return Vector((x, y, z))


def route_tangent(theta):
    dx = -(ROUTE_WIDTH * 0.5) * math.sin(theta)
    dy = (ROUTE_DEPTH * 0.5) * math.cos(theta)
    dz = HEIGHT_AMPLITUDE * math.cos(theta + 0.75) + 0.24 * math.cos(theta * 2.0 - 0.4)
    tangent = Vector((dx, dy, dz))
    if tangent.length < 0.0001:
        return Vector((0, -1, 0))
    return tangent.normalized()


def look_rotation_for_tangent(tangent):
    # The imported dragon points roughly along local -Y, so track -Y to the flight tangent.
    return tangent.to_track_quat("-Y", "Z")


def wave_quaternion(bone_index, theta, is_head=False, is_tail=False):
    phase = theta * 2.0 - bone_index * 0.55
    if is_head:
        yaw = math.sin(phase - 0.25) * 3.0
        pitch = math.sin(phase + 0.5) * 5.0
    elif is_tail:
        yaw = math.sin(phase) * 18.0
        pitch = math.sin(phase + 1.0) * 5.0
    else:
        yaw_amp = 8.0 if bone_index < 2 else 12.0 if bone_index < 8 else 15.0
        yaw = math.sin(phase) * yaw_amp
        pitch = math.sin(phase + 1.1) * 4.5
    return Euler((math.radians(pitch), 0.0, math.radians(yaw)), "XYZ").to_quaternion()


def insert_flight_animation(armature):
    bpy.context.scene.frame_start = FRAME_START
    bpy.context.scene.frame_end = FRAME_END
    bpy.context.scene.render.fps = FPS

    action = bpy.data.actions.new(ACTION_NAME)
    armature.animation_data_create()
    armature.animation_data.action = action
    armature.rotation_mode = "QUATERNION"

    pose_bones = armature.pose.bones
    spine_bones = []
    for i in range(12):
        bone = pose_bones.get(f"spine_{i:02d}")
        if bone:
            bone.rotation_mode = "QUATERNION"
            spine_bones.append((i, bone, bone.rotation_quaternion.copy()))

    head_bone = pose_bones.get("head")
    head_base = None
    if head_bone:
        head_bone.rotation_mode = "QUATERNION"
        head_base = head_bone.rotation_quaternion.copy()

    tail_bone = pose_bones.get("tail_tip")
    tail_base = None
    if tail_bone:
        tail_bone.rotation_mode = "QUATERNION"
        tail_base = tail_bone.rotation_quaternion.copy()

    for frame in range(FRAME_START, FRAME_END + 1):
        t = (frame - FRAME_START) / (FRAME_END - FRAME_START)
        theta = math.tau * t
        position = route_position(theta)
        tangent = route_tangent(theta)
        rotation = look_rotation_for_tangent(tangent)

        bpy.context.scene.frame_set(frame)
        armature.location = position
        armature.rotation_quaternion = rotation
        armature.keyframe_insert(data_path="location", frame=frame)
        armature.keyframe_insert(data_path="rotation_quaternion", frame=frame)

        for bone_index, bone, base_rotation in spine_bones:
            bone.rotation_quaternion = base_rotation @ wave_quaternion(bone_index, theta)
            bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

        if head_bone and head_base:
            head_bone.rotation_quaternion = head_base @ wave_quaternion(0, theta, is_head=True)
            head_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

        if tail_bone and tail_base:
            tail_bone.rotation_quaternion = tail_base @ wave_quaternion(12, theta, is_tail=True)
            tail_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    return {
        "actionName": action.name,
        "spineBoneCount": len(spine_bones),
        "headAnimated": head_bone is not None,
        "tailAnimated": tail_bone is not None,
    }


def export_glb():
    bpy.ops.export_scene.gltf(
        filepath=FLIGHT_GLB,
        export_format="GLB",
        export_animations=True,
        export_animation_mode="ACTIONS",
        export_force_sampling=True,
        export_apply=True,
        export_materials="EXPORT",
        export_image_format="AUTO",
        export_yup=True,
    )


def export_usdz():
    bpy.ops.wm.usd_export(
        filepath=FLIGHT_USDZ,
        export_animation=True,
        export_armatures=True,
        only_deform_bones=False,
        export_meshes=True,
        export_materials=True,
        export_uvmaps=True,
        export_normals=True,
        export_textures_mode="NEW",
        evaluation_mode="RENDER",
        selected_objects_only=False,
        relative_paths=False,
        root_prim_path="/DragonFlight",
    )


def compute_route_report():
    samples = [route_position(math.tau * i / 120.0) for i in range(121)]
    heights = [p.z for p in samples]
    xs = [p.x for p in samples]
    ys = [p.y for p in samples]
    start_gap = (samples[0] - samples[-1]).length
    return {
        "animationDuration": DURATION_SECONDS,
        "dragonHeightMin": min(heights),
        "dragonHeightMax": max(heights),
        "dragonHeightAverage": sum(heights) / len(heights),
        "routeWidth": max(xs) - min(xs),
        "routeDepth": max(ys) - min(ys),
        "loopStartEndGap": start_gap,
        "loopSmooth": start_gap < 0.001,
    }


def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=SOURCE_GLB)
    remove_old_actions()
    anchor = create_shadow_anchor()
    armature = find_armature()
    anim_report = insert_flight_animation(armature)

    export_glb()
    export_usdz()

    route_report = compute_route_report()
    report = {
        "sourceGlb": SOURCE_GLB,
        "flightGlb": FLIGHT_GLB,
        "flightUsdz": FLIGHT_USDZ,
        "floorAnchorCreated": anchor is not None,
        "floorAnchorName": anchor.name if anchor else None,
        "selectedAction": ACTION_NAME,
        "frameStart": FRAME_START,
        "frameEnd": FRAME_END,
        "fps": FPS,
        "flightGlbCreated": os.path.exists(FLIGHT_GLB),
        "flightUsdzCreated": os.path.exists(FLIGHT_USDZ),
        "flightGlbBytes": os.path.getsize(FLIGHT_GLB) if os.path.exists(FLIGHT_GLB) else 0,
        "flightUsdzBytes": os.path.getsize(FLIGHT_USDZ) if os.path.exists(FLIGHT_USDZ) else 0,
        **route_report,
        **anim_report,
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("[WEBAR_FLIGHT_AR] flightGlbCreated=" + str(report["flightGlbCreated"]))
    print("[WEBAR_FLIGHT_AR] flightUsdzCreated=" + str(report["flightUsdzCreated"]))
    print("[WEBAR_FLIGHT_AR] animationDuration=" + str(DURATION_SECONDS))
    print("[WEBAR_FLIGHT_AR] dragonHeight=" + f"{route_report['dragonHeightMin']:.2f}-{route_report['dragonHeightMax']:.2f}")
    print("[WEBAR_FLIGHT_AR] routeWidth=" + f"{route_report['routeWidth']:.2f}")
    print("[WEBAR_FLIGHT_AR] routeDepth=" + f"{route_report['routeDepth']:.2f}")
    print("[WEBAR_FLIGHT_AR] loopSmooth=" + str(route_report["loopSmooth"]))
    print("[WEBAR_FLIGHT_AR_REPORT]" + json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
