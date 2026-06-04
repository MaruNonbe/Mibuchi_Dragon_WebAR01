import json
import math
import os
import shutil

import bpy
from mathutils import Vector


PROJECT_ROOT = r"C:\Users\user\Documents\ARDragon\ARDragon\Mibuchi_Dragon_WebAR01"
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
BACKUP_DIR = os.path.join(ASSETS_DIR, "backup")
SOURCE_GLB = os.path.join(ASSETS_DIR, "dragon_web.glb")
OUTPUT_GLB = os.path.join(ASSETS_DIR, "dragon_web_giant_approach.glb")
OUTPUT_USDZ = os.path.join(ASSETS_DIR, "dragon_web_giant_approach.usdz")
REPORT_PATH = os.path.join(BACKUP_DIR, "giant_approach_route_report.json")

ACTION_NAME = "Giant_Approach_Overhead_Circle"
FPS = 24
DURATION_SECONDS = 16.0
FRAME_START = 0
FRAME_END = int(DURATION_SECONDS * FPS)
GIANT_SCALE = 2.8


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def backup_existing():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if os.path.exists(OUTPUT_GLB):
        shutil.copy2(OUTPUT_GLB, os.path.join(BACKUP_DIR, "dragon_web_giant_approach_before_route_fix.glb"))
    if os.path.exists(OUTPUT_USDZ):
        shutil.copy2(OUTPUT_USDZ, os.path.join(BACKUP_DIR, "dragon_web_giant_approach_before_route_fix.usdz"))


def find_armature():
    armatures = [obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"]
    if not armatures:
        raise RuntimeError("No armature found.")
    return armatures[0]


def remove_all_actions():
    for obj in bpy.context.scene.objects:
        obj.animation_data_clear()
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)


def create_floor_shadow_anchor():
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=1.25, depth=0.006, location=(0, 0, 0.003))
    anchor = bpy.context.object
    anchor.name = "GiantApproachFloorAnchor"
    anchor.scale = (1.7, 0.86, 1.0)
    mat = bpy.data.materials.new("GiantApproachFloorAnchor_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.015, 0.025, 0.025, 0.14)
        bsdf.inputs["Alpha"].default_value = 0.14
        bsdf.inputs["Roughness"].default_value = 0.92
    mat.blend_method = "BLEND"
    anchor.data.materials.append(mat)
    return anchor


def smoothstep(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def bezier(p0, p1, p2, p3, t):
    u = 1.0 - t
    return (u ** 3) * p0 + 3.0 * (u ** 2) * t * p1 + 3.0 * u * (t ** 2) * p2 + (t ** 3) * p3


def route_position(t):
    # Viewer is assumed near the floor anchor looking forward into -Y.
    # The dragon starts far ahead, approaches, skims overhead, climbs, then circles high.
    if t < 0.62:
        u = smoothstep(t / 0.62)
        return bezier(
            Vector((-4.8, -15.0, 6.2)),
            Vector((-2.8, -11.5, 5.7)),
            Vector((1.4, -5.2, 4.6)),
            Vector((0.0, -1.35, 4.15)),
            u,
        )

    if t < 0.78:
        u = smoothstep((t - 0.62) / 0.16)
        return bezier(
            Vector((0.0, -1.35, 4.15)),
            Vector((0.55, 0.2, 4.45)),
            Vector((1.65, 2.8, 5.65)),
            Vector((2.5, 5.0, 7.2)),
            u,
        )

    u = (t - 0.78) / 0.22
    angle = math.tau * u + 0.35
    center = Vector((0.0, 4.2, 7.0))
    return Vector((
        center.x + math.cos(angle) * 3.0,
        center.y + math.sin(angle) * 2.1,
        center.z + math.sin(angle + 0.8) * 0.45,
    ))


def tangent_at(t):
    dt = 1.0 / FRAME_END
    p0 = route_position(max(0.0, t - dt))
    p1 = route_position(min(1.0, t + dt))
    tangent = p1 - p0
    if tangent.length < 0.0001:
        return Vector((0.0, -1.0, 0.0))
    return tangent.normalized()


def look_rotation(tangent):
    # Imported dragon faces roughly local -Y.
    return tangent.to_track_quat("-Y", "Z")


def insert_route_animation(armature):
    bpy.context.scene.frame_start = FRAME_START
    bpy.context.scene.frame_end = FRAME_END
    bpy.context.scene.render.fps = FPS

    action = bpy.data.actions.new(ACTION_NAME)
    armature.animation_data_create()
    armature.animation_data.action = action
    armature.rotation_mode = "QUATERNION"

    for frame in range(FRAME_START, FRAME_END + 1):
        t = (frame - FRAME_START) / (FRAME_END - FRAME_START)
        bpy.context.scene.frame_set(frame)
        armature.location = route_position(t)
        armature.rotation_quaternion = look_rotation(tangent_at(t))
        armature.scale = (GIANT_SCALE, GIANT_SCALE, GIANT_SCALE)
        armature.keyframe_insert(data_path="location", frame=frame)
        armature.keyframe_insert(data_path="rotation_quaternion", frame=frame)
        armature.keyframe_insert(data_path="scale", frame=frame)

    return action


def route_report():
    samples = [route_position(i / 160.0) for i in range(161)]
    heights = [p.z for p in samples]
    distances_to_viewer = [p.length for p in samples]
    return {
        "durationSeconds": DURATION_SECONDS,
        "giantScale": GIANT_SCALE,
        "startPosition": list(route_position(0.0)),
        "overheadPosition": list(route_position(0.62)),
        "circleCenterApprox": [0.0, 4.2, 7.0],
        "heightMin": min(heights),
        "heightMax": max(heights),
        "minDistanceToViewer": min(distances_to_viewer),
        "whiskerFix": "No head/spine/whisker bone animation; route is applied to ARDragonArmature root only.",
    }


def export_glb():
    bpy.ops.export_scene.gltf(
        filepath=OUTPUT_GLB,
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
        filepath=OUTPUT_USDZ,
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
        root_prim_path="/GiantDragonApproach",
    )


def main():
    backup_existing()
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=SOURCE_GLB)
    remove_all_actions()

    armature = find_armature()
    create_floor_shadow_anchor()
    action = insert_route_animation(armature)

    export_glb()
    export_usdz()

    report = {
        "sourceGlb": SOURCE_GLB,
        "outputGlb": OUTPUT_GLB,
        "outputUsdz": OUTPUT_USDZ,
        "actionName": action.name,
        "outputGlbCreated": os.path.exists(OUTPUT_GLB),
        "outputUsdzCreated": os.path.exists(OUTPUT_USDZ),
        "outputGlbBytes": os.path.getsize(OUTPUT_GLB) if os.path.exists(OUTPUT_GLB) else 0,
        "outputUsdzBytes": os.path.getsize(OUTPUT_USDZ) if os.path.exists(OUTPUT_USDZ) else 0,
        **route_report(),
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("[GIANT_APPROACH_ROUTE] glbCreated=" + str(report["outputGlbCreated"]))
    print("[GIANT_APPROACH_ROUTE] usdzCreated=" + str(report["outputUsdzCreated"]))
    print("[GIANT_APPROACH_ROUTE] actionName=" + action.name)
    print("[GIANT_APPROACH_ROUTE] giantScale=" + str(GIANT_SCALE))
    print("[GIANT_APPROACH_ROUTE] heightRange=" + f"{report['heightMin']:.2f}-{report['heightMax']:.2f}")
    print("[GIANT_APPROACH_ROUTE] minDistanceToViewer=" + f"{report['minDistanceToViewer']:.2f}")
    print("[GIANT_APPROACH_ROUTE] whiskerDetachedFix=True")
    print("[GIANT_APPROACH_ROUTE_REPORT]" + json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
