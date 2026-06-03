import json
import os

from pxr import Usd


PROJECT_ROOT = r"C:\Users\user\Documents\ARDragon\ARDragon\Mibuchi_Dragon_WebAR01"
USDZ_PATH = os.path.join(PROJECT_ROOT, "assets", "dragon_web.usdz")
REPORT_PATH = os.path.join(PROJECT_ROOT, "assets", "backup", "webar_usdz_anim_inspect.json")


def main():
    stage = Usd.Stage.Open(USDZ_PATH)
    time_sampled_attrs = []
    prim_types = {}

    for prim in stage.Traverse():
        prim_type = prim.GetTypeName()
        prim_types[prim_type] = prim_types.get(prim_type, 0) + 1
        for attr in prim.GetAttributes():
            samples = attr.GetTimeSamples()
            if samples:
                time_sampled_attrs.append(
                    {
                        "prim": str(prim.GetPath()),
                        "type": prim_type,
                        "attribute": attr.GetName(),
                        "sampleCount": len(samples),
                        "firstSample": samples[0],
                        "lastSample": samples[-1],
                    }
                )

    report = {
        "usdzPath": USDZ_PATH,
        "startTimeCode": float(stage.GetStartTimeCode()),
        "endTimeCode": float(stage.GetEndTimeCode()),
        "framesPerSecond": float(stage.GetFramesPerSecond()),
        "timeCodesPerSecond": float(stage.GetTimeCodesPerSecond()),
        "primTypes": prim_types,
        "timeSampledAttributeCount": len(time_sampled_attrs),
        "timeSampledAttributes": time_sampled_attrs[:80],
        "usdzAnimationExists": len(time_sampled_attrs) > 0,
    }

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("[WEBAR_ANIM_CHECK] usdzAnimationExists=" + str(report["usdzAnimationExists"]))
    print("[WEBAR_USDZ_ANIM_INSPECT]" + json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
