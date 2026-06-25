import json
import math
import os
import re
from pathlib import Path

import bpy
from mathutils import Vector


FRAME_START = 1
FRAME_END = 160
FRAME_STEP = 8

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "gps-webar" / "assets" / "stations"
MAIN_JS = ROOT / "gps-webar" / "main.js"
REPORT_PATH = ROOT / "gps-webar" / "assets" / "stations" / "station_model_inspection.json"

EXPECTED_STATIONS = [
    ("赤湯駅", "きつね・ウサギ・シカの弦楽四重奏", "akayu_strings_fox_rabbit.glb", ["fox", "rabbit", "deer", "cat"], ["violin", "violin", "viola", "cello"]),
    ("南陽市役所駅", "ネコと小鳥の木管アンサンブル", "nanyo_city_hall_cats_woodwinds.glb", ["cat", "cat", "bird", "rabbit"], ["flute", "clarinet", "flute", "clarinet"]),
    ("宮内駅", "イヌたちの金管ファンファーレ", "miyauchi_dogs_brass.glb", ["dog", "dog", "bear", "fox"], ["trumpet", "trombone", "trumpet", "trombone"]),
    ("おりはた駅", "リスとカエルの打楽器パレード", "orihata_squirrels_percussion.glb", ["squirrel", "squirrel", "frog", "tanuki"], ["snare", "tambourine", "marimba", "bass_drum"]),
    ("梨郷駅", "パンダとペンギンの駅前ジャズ", "ringo_panda_penguin_jazz.glb", ["panda", "penguin", "cat", "bear"], ["trumpet", "clarinet", "flute", "trombone"]),
    ("西大塚駅", "タヌキたちの太鼓リズム", "nishi_otsuka_tanuki_taiko.glb", ["tanuki", "tanuki", "fox", "rabbit"], ["bass_drum", "snare", "tambourine", "marimba"]),
    ("今泉駅", "シカと小鳥のフルート合奏", "imaizumi_deer_flutes.glb", ["deer", "deer", "bird", "cat"], ["flute", "clarinet", "flute", "clarinet"]),
    ("時庭駅", "クマたちの低音ブラス", "tokiniwa_bears_low_brass.glb", ["bear", "bear", "dog", "panda"], ["trombone", "trumpet", "trombone", "trumpet"]),
    ("南長井駅", "ウサギたちのクラリネット隊", "minami_nagai_rabbit_clarinets.glb", ["rabbit", "rabbit", "cat", "bird"], ["clarinet", "flute", "clarinet", "flute"]),
    ("長井駅", "どうぶつ弦楽四重奏", "nagai_main_string_quartet.glb", ["fox", "rabbit", "bear", "cat"], ["violin", "violin", "viola", "cello"]),
    ("あやめ公園駅", "小鳥たちのピッコロ行進曲", "ayame_koen_birds_piccolo.glb", ["bird", "bird", "penguin", "rabbit"], ["flute", "clarinet", "flute", "clarinet"]),
    ("羽前成田駅", "キツネたちのサックスバンド", "uzen_narita_fox_sax_band.glb", ["fox", "fox", "cat", "dog"], ["trumpet", "clarinet", "flute", "trombone"]),
    ("白兎駅", "白ウサギのハンドベル隊", "shirousagi_white_rabbit_bells.glb", ["rabbit", "rabbit", "sheep", "panda"], ["tambourine", "snare", "marimba", "bass_drum"]),
    ("蚕桑駅", "カモシカたちのホルン合奏", "koguwa_kamoshika_horns.glb", ["kamoshika", "kamoshika", "deer", "dog"], ["trumpet", "trombone", "trumpet", "trombone"]),
    ("鮎貝駅", "カエルたちのマリンバ隊", "ayukai_frogs_marimba.glb", ["frog", "frog", "bird", "tanuki"], ["marimba", "snare", "tambourine", "bass_drum"]),
    ("四季の郷駅", "ヒツジたちのトロンボーン隊", "shikinosato_sheep_trombones.glb", ["sheep", "sheep", "deer", "panda"], ["trombone", "trumpet", "trombone", "trumpet"]),
    ("荒砥駅", "全員集合フィナーレ", "arato_finale_all_stars.glb", ["fox", "rabbit", "bear", "cat", "dog", "squirrel", "frog", "tanuki", "deer", "bird", "panda", "penguin", "kamoshika", "sheep"], ["violin", "trumpet", "bass_drum", "flute", "trombone", "tambourine", "marimba", "snare", "viola", "flute", "trumpet", "clarinet", "trombone", "bass_drum"]),
]

INSTRUMENT_KINDS = {
    "violin",
    "viola",
    "cello",
    "flute",
    "clarinet",
    "trumpet",
    "trombone",
    "snare",
    "tambourine",
    "marimba",
    "bass_drum",
}


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def read_main_js_mapping():
    text = MAIN_JS.read_text(encoding="utf-8")
    stations = re.findall(r'\{\s*name:\s*"([^"]+)",\s*latitude:', text)
    variants = re.findall(r'\{\s*variantLabel:\s*"([^"]+)",\s*ensemble:\s*"[^"]+",\s*modelPath:\s*"([^"]+)"\s*\}', text)
    return [(stations[i], variants[i][0], Path(variants[i][1]).name) for i in range(min(len(stations), len(variants), len(EXPECTED_STATIONS)))]


def import_glb(path):
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(path))
    scene = bpy.context.scene
    scene.frame_start = FRAME_START
    scene.frame_end = FRAME_END
    return scene


def apply_runtime_layout():
    # Mirrors gps-webar/main.js stable AR layout spacing so the collision check
    # matches the model after WebAR loads it.
    for obj in bpy.context.scene.objects:
        if obj.name.endswith("_quartet_player") or "_quartet_player." in obj.name:
            if obj.location.y < 0:
                obj.location.x = -2.65 if obj.location.x < 0 else 2.65
        elif obj.name.endswith("_music_stand") or "_music_stand." in obj.name:
            if obj.location.y < -0.5:
                obj.location.x = -1.65 if obj.location.x < 0 else 1.65


def descendants(root):
    result = []
    stack = list(root.children)
    while stack:
        obj = stack.pop()
        result.append(obj)
        stack.extend(list(obj.children))
    return result


def mesh_bbox_world(obj):
    if obj.type not in {"MESH", "CURVE", "FONT"}:
        return None
    try:
        corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    except Exception:
        return None
    mins = Vector((min(p.x for p in corners), min(p.y for p in corners), min(p.z for p in corners)))
    maxs = Vector((max(p.x for p in corners), max(p.y for p in corners), max(p.z for p in corners)))
    return mins, maxs


def is_instrument_or_effect_name(name):
    return (
        any(f"_{kind}" in name for kind in INSTRUMENT_KINDS)
        or "_bow_" in name
        or "_bow_anim" in name
        or "_note_" in name
        or "_mallet_" in name
    )


def group_bbox(root, exclude=None):
    boxes = []
    for obj in [root] + descendants(root):
        if exclude and exclude(obj):
            continue
        box = mesh_bbox_world(obj)
        if box:
            boxes.append(box)
    if not boxes:
        return None
    mins = Vector((min(b[0].x for b in boxes), min(b[0].y for b in boxes), min(b[0].z for b in boxes)))
    maxs = Vector((max(b[1].x for b in boxes), max(b[1].y for b in boxes), max(b[1].z for b in boxes)))
    return mins, maxs


def box_overlap(a, b, shrink=0.0):
    if not a or not b:
        return False
    amin, amax = a
    bmin, bmax = b
    return (
        amin.x + shrink <= bmax.x - shrink and amax.x - shrink >= bmin.x + shrink
        and amin.y + shrink <= bmax.y - shrink and amax.y - shrink >= bmin.y + shrink
        and amin.z + shrink <= bmax.z - shrink and amax.z - shrink >= bmin.z + shrink
    )


def box_gap(a, b):
    amin, amax = a
    bmin, bmax = b
    gaps = [
        max(bmin.x - amax.x, amin.x - bmax.x, 0),
        max(bmin.y - amax.y, amin.y - bmax.y, 0),
        max(bmin.z - amax.z, amin.z - bmax.z, 0),
    ]
    return math.sqrt(sum(g * g for g in gaps))


def roots_matching(pattern):
    return [obj for obj in bpy.context.scene.objects if pattern(obj.name)]


def instrument_roots():
    roots = []
    for obj in bpy.context.scene.objects:
        name = obj.name
        if obj.parent is not None and any(f"_{kind}" in name for kind in INSTRUMENT_KINDS) and obj.type == "EMPTY":
            roots.append(obj)
        elif "_mallet_" in name and obj.type == "MESH":
            roots.append(obj)
    return roots


def find_nearest_right_paw(bow):
    best = None
    best_distance = 10**9
    for obj in bpy.context.scene.objects:
        if "right_paw" not in obj.name:
            continue
        distance = (obj.matrix_world.translation - bow.matrix_world.translation).length
        if distance < best_distance:
            best = obj
            best_distance = distance
    return best, best_distance


def scene_name_contains(station_name):
    names = [obj.name for obj in bpy.context.scene.objects]
    arrival_text = f"{station_name}到着"
    return {
        "station_label_object_exists": any("station_name_label" in name for name in names),
        "arrival_chars_in_object_names": all(char in "".join(names) for char in arrival_text),
    }


def inspect_station(station_name, variant_label, filename, expected_species, expected_instruments):
    path = ASSET_DIR / filename
    result = {
        "station": station_name,
        "variantLabel": variant_label,
        "file": filename,
        "fileExists": path.exists(),
        "expectedSpecies": expected_species,
        "expectedInstruments": expected_instruments,
        "errors": [],
        "warnings": [],
        "clearanceMeters": {},
        "bowHandMaxDistanceMeters": {},
    }
    if not path.exists():
        result["errors"].append("GLB file is missing.")
        return result

    scene = import_glb(path)
    apply_runtime_layout()
    name_check = scene_name_contains(station_name)
    result.update(name_check)
    if not name_check["station_label_object_exists"]:
        result["errors"].append("station_name_label object was not found.")
    if not name_check["arrival_chars_in_object_names"]:
        result["warnings"].append("Arrival title character names do not include every station-name character.")

    object_names = " ".join(obj.name for obj in scene.objects)
    for species in expected_species:
        if species not in object_names:
            result["errors"].append(f"Expected animal species was not found: {species}")
    for instrument in expected_instruments:
        if instrument not in object_names:
            result["errors"].append(f"Expected instrument was not found: {instrument}")

    players = roots_matching(lambda n: n.endswith("_quartet_player") or "_quartet_player." in n)
    stands = roots_matching(lambda n: n.endswith("_music_stand") or "_music_stand." in n)
    instruments = instrument_roots()
    bows = roots_matching(lambda n: "_bow_anim" in n)

    if len(players) != len(expected_species):
        result["errors"].append(f"Expected {len(expected_species)} character roots, found {len(players)}.")
    if len(stands) != 4:
        result["errors"].append(f"Expected 4 music stands, found {len(stands)}.")

    min_gaps = {
        "playerVsStand": 99.0,
        "instrumentVsStand": 99.0,
        "bowVsStand": 99.0,
    }

    collision_events = []
    for frame in range(FRAME_START, FRAME_END + 1, FRAME_STEP):
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        stand_boxes = [(stand, group_bbox(stand)) for stand in stands]

        for player in players:
            pbox = group_bbox(player, exclude=lambda obj: is_instrument_or_effect_name(obj.name))
            for stand, sbox in stand_boxes:
                if not pbox or not sbox:
                    continue
                min_gaps["playerVsStand"] = min(min_gaps["playerVsStand"], box_gap(pbox, sbox))
                if box_overlap(pbox, sbox, shrink=0.025):
                    collision_events.append({"frame": frame, "type": "playerVsStand", "a": player.name, "b": stand.name})

        for inst in instruments:
            ibox = group_bbox(inst)
            for stand, sbox in stand_boxes:
                if not ibox or not sbox:
                    continue
                min_gaps["instrumentVsStand"] = min(min_gaps["instrumentVsStand"], box_gap(ibox, sbox))
                if box_overlap(ibox, sbox, shrink=0.018):
                    collision_events.append({"frame": frame, "type": "instrumentVsStand", "a": inst.name, "b": stand.name})

        for bow in bows:
            bbox = group_bbox(bow)
            for stand, sbox in stand_boxes:
                if not bbox or not sbox:
                    continue
                min_gaps["bowVsStand"] = min(min_gaps["bowVsStand"], box_gap(bbox, sbox))
                if box_overlap(bbox, sbox, shrink=0.012):
                    collision_events.append({"frame": frame, "type": "bowVsStand", "a": bow.name, "b": stand.name})

            paw, distance = find_nearest_right_paw(bow)
            key = bow.name
            result["bowHandMaxDistanceMeters"][key] = max(result["bowHandMaxDistanceMeters"].get(key, 0), round(distance, 4))
            if paw is None or distance > 0.82:
                result["errors"].append(f"Bow is not linked closely enough to a right hand at frame {frame}: {bow.name}, distance={distance:.3f}m")

    result["clearanceMeters"] = {key: round(value, 4) for key, value in min_gaps.items() if value < 90}
    if collision_events:
        result["errors"].append(f"Detected {len(collision_events)} bounding-box collision events.")
        result["collisionEvents"] = collision_events[:20]
    return result


def main():
    report = {
        "checkedFrameRange": [FRAME_START, FRAME_END],
        "frameStep": FRAME_STEP,
        "webMapping": [],
        "stations": [],
        "summary": {},
    }
    actual_mapping = read_main_js_mapping()
    for expected, actual in zip(EXPECTED_STATIONS, actual_mapping):
        station_name, variant_label, filename = expected[:3]
        actual_station, actual_variant, actual_file = actual
        report["webMapping"].append({
            "expectedStation": station_name,
            "actualStation": actual_station,
            "expectedVariantLabel": variant_label,
            "actualVariantLabel": actual_variant,
            "expectedFile": filename,
            "actualFile": actual_file,
            "ok": (station_name, variant_label, filename) == (actual_station, actual_variant, actual_file),
        })

    for expected in EXPECTED_STATIONS:
        report["stations"].append(inspect_station(*expected))

    errors = sum(len(item["errors"]) for item in report["stations"])
    warnings = sum(len(item["warnings"]) for item in report["stations"])
    mapping_errors = [item for item in report["webMapping"] if not item["ok"]]
    report["summary"] = {
        "stationCount": len(report["stations"]),
        "mappingErrors": len(mapping_errors),
        "modelErrors": errors,
        "modelWarnings": warnings,
        "ok": not mapping_errors and errors == 0,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    if not report["summary"]["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
