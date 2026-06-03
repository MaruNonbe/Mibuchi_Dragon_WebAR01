import json
import math
import os

import bpy


PROJECT_ROOT = r"C:\Users\user\Documents\ARDragon\ARDragon\Mibuchi_Dragon_WebAR01"
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
SOURCE_GLB = os.path.join(ASSETS_DIR, "dragon_web.glb")
SKY_GLB = os.path.join(ASSETS_DIR, "dragon_web_sky.glb")
SKY_USDZ = os.path.join(ASSETS_DIR, "dragon_web_sky.usdz")
BACKUP_DIR = os.path.join(ASSETS_DIR, "backup")
REPORT_PATH = os.path.join(BACKUP_DIR, "sky_ar_model_report.json")

SKY_HEIGHT_METERS = 3.2
PREFERRED_ACTION = "Idle_S_Curve_Loop"


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def imported_roots():
    child_names = set()
    for obj in bpy.context.scene.objects:
        if obj.parent:
            child_names.add(obj.name)
    return [obj for obj in bpy.context.scene.objects if obj.name not in child_names]


def create_shadow_anchor():
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=0.85, depth=0.006, location=(0, 0, 0.003))
    anchor = bpy.context.object
    anchor.name = "FloorShadowAnchor"
    anchor.scale = (1.45, 0.72, 1.0)
    mat = bpy.data.materials.new("FloorShadowAnchor_Mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.02, 0.03, 0.03, 0.18)
        bsdf.inputs["Alpha"].default_value = 0.18
        bsdf.inputs["Roughness"].default_value = 0.9
    mat.blend_method = "BLEND"
    mat.use_screen_refraction = False
    anchor.data.materials.append(mat)
    return anchor


def assign_preferred_action():
    action = bpy.data.actions.get(PREFERRED_ACTION)
    if action is None and bpy.data.actions:
        action = bpy.data.actions[0]
    if action is None:
        return None

    for obj in bpy.context.scene.objects:
        if obj.type == "ARMATURE":
            obj.animation_data_create()
            obj.animation_data.action = action
            if obj.animation_data.nla_tracks:
                for track in obj.animation_data.nla_tracks:
                    track.mute = True

    start, end = action.frame_range
    bpy.context.scene.frame_start = int(start)
    bpy.context.scene.frame_end = int(end)
    bpy.context.scene.render.fps = 24
    return action


def create_sky_offset_root():
    roots = imported_roots()
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, SKY_HEIGHT_METERS))
    sky_root = bpy.context.object
    sky_root.name = "SkyOffsetRoot_3_2m"

    for obj in roots:
        if obj == sky_root:
            continue
        obj.location.z += SKY_HEIGHT_METERS

    return sky_root


def export_glb():
    bpy.ops.export_scene.gltf(
        filepath=SKY_GLB,
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
        filepath=SKY_USDZ,
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
        root_prim_path="/DragonSky",
    )


def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=SOURCE_GLB)

    actions = [action.name for action in bpy.data.actions]
    selected_action = assign_preferred_action()
    sky_root = create_sky_offset_root()
    anchor = create_shadow_anchor()

    export_glb()
    export_usdz()

    armatures = [obj.name for obj in bpy.context.scene.objects if obj.type == "ARMATURE"]
    skinned_meshes = [
        obj.name
        for obj in bpy.context.scene.objects
        if obj.type == "MESH" and any(mod.type == "ARMATURE" for mod in obj.modifiers)
    ]
    report = {
        "sourceGlb": SOURCE_GLB,
        "skyGlb": SKY_GLB,
        "skyUsdz": SKY_USDZ,
        "dragonHeightMeters": SKY_HEIGHT_METERS,
        "floorAnchorCreated": anchor is not None,
        "floorAnchorName": anchor.name if anchor else None,
        "skyRootName": sky_root.name,
        "actions": actions,
        "selectedAction": selected_action.name if selected_action else None,
        "frameStart": bpy.context.scene.frame_start,
        "frameEnd": bpy.context.scene.frame_end,
        "fps": bpy.context.scene.render.fps,
        "armatures": armatures,
        "skinnedMeshes": skinned_meshes,
        "skyGlbCreated": os.path.exists(SKY_GLB),
        "skyUsdzCreated": os.path.exists(SKY_USDZ),
        "skyGlbBytes": os.path.getsize(SKY_GLB) if os.path.exists(SKY_GLB) else 0,
        "skyUsdzBytes": os.path.getsize(SKY_USDZ) if os.path.exists(SKY_USDZ) else 0,
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("[SKY_AR_MODEL] skyGlbCreated=" + str(report["skyGlbCreated"]))
    print("[SKY_AR_MODEL] skyUsdzCreated=" + str(report["skyUsdzCreated"]))
    print("[SKY_AR_MODEL] dragonHeightMeters=" + str(SKY_HEIGHT_METERS))
    print("[SKY_AR_MODEL] floorAnchorCreated=" + str(report["floorAnchorCreated"]))
    print("[SKY_AR_MODEL] selectedAction=" + str(report["selectedAction"]))
    print("[SKY_AR_MODEL_REPORT]" + json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
