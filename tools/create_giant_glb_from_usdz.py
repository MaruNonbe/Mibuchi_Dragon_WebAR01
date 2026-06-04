import json
import os

import bpy


PROJECT_ROOT = r"C:\Users\user\Documents\ARDragon\ARDragon\Mibuchi_Dragon_WebAR01"
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
SOURCE_USDZ = os.path.join(ASSETS_DIR, "dragon_web_giant_approach.usdz")
OUTPUT_GLB = os.path.join(ASSETS_DIR, "dragon_web_giant_approach.glb")
REPORT_PATH = os.path.join(ASSETS_DIR, "backup", "giant_approach_glb_report.json")


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def main():
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    clear_scene()

    bpy.ops.wm.usd_import(filepath=SOURCE_USDZ)

    actions = [action.name for action in bpy.data.actions]
    armatures = [obj.name for obj in bpy.context.scene.objects if obj.type == "ARMATURE"]
    meshes = [obj.name for obj in bpy.context.scene.objects if obj.type == "MESH"]

    if bpy.data.actions:
        action = bpy.data.actions[0]
        start, end = action.frame_range
        bpy.context.scene.frame_start = int(start)
        bpy.context.scene.frame_end = int(end)
        bpy.context.scene.render.fps = 24

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

    report = {
        "sourceUsdz": SOURCE_USDZ,
        "outputGlb": OUTPUT_GLB,
        "sourceUsdzExists": os.path.exists(SOURCE_USDZ),
        "outputGlbCreated": os.path.exists(OUTPUT_GLB),
        "outputGlbBytes": os.path.getsize(OUTPUT_GLB) if os.path.exists(OUTPUT_GLB) else 0,
        "actions": actions,
        "armatures": armatures,
        "meshes": meshes,
        "frameStart": bpy.context.scene.frame_start,
        "frameEnd": bpy.context.scene.frame_end,
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("[GIANT_MODEL] sourceUsdzExists=" + str(report["sourceUsdzExists"]))
    print("[GIANT_MODEL] outputGlbCreated=" + str(report["outputGlbCreated"]))
    print("[GIANT_MODEL] actions=" + ",".join(actions))
    print("[GIANT_MODEL_REPORT]" + json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
