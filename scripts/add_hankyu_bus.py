#!/usr/bin/env python3
"""阪急バス（千里中央↔阪大本部前）をtimetables.jsonに追加する.

出典:
  NAVITIME バス時刻表 + 駅探 運賃情報
  千里中央→阪大本部前: 250円, 約13分, 7:19始発〜17:09終発, 約15分間隔
  阪大本部前→千里中央: 250円, 約23分, 8:57始発〜19時台終発, 約30分間隔

千里中央駅は既にモノレール/北大阪急行の駅として存在。
阪大本部前は吹田キャンパス内のバス停（nearby_stationsにsenri_chuoへの
阪急バスルートとして組込む）。
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    path = DATA_DIR / "timetables.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # 1. 路線追加
    data["lines"]["hankyu_bus"] = {"name": "阪急バス", "type": "bus"}

    # 2. 駅（バス停）追加: 阪大本部前
    data["stations"]["handai_honbu"] = {
        "name": "阪大本部前",
        "lines": ["hankyu_bus"],
    }

    # 千里中央に阪急バスを追加
    if "hankyu_bus" not in data["stations"]["senri_chuo"]["lines"]:
        data["stations"]["senri_chuo"]["lines"].append("hankyu_bus")

    # 3. 吹田キャンパスに阪大本部前を最寄り駅（バス停）として追加
    suita_stations = data["campuses"]["吹田キャンパス"]["nearby_stations"]
    if not any(s["station_id"] == "handai_honbu" for s in suita_stations):
        suita_stations.append({"station_id": "handai_honbu", "walk_min": 3})

    # 4. train_segments に阪急バス区間を追加
    bus_segments = [
        # 千里中央 → 阪大本部前
        {
            "line": "hankyu_bus",
            "from": "senri_chuo",
            "to": "handai_honbu",
            "duration_min": 13,
            "fare": 250,
            "first_departure": "07:19",
            "last_departure": "17:09",
            "frequency_min": 15,
        },
        # 阪大本部前 → 千里中央
        {
            "line": "hankyu_bus",
            "from": "handai_honbu",
            "to": "senri_chuo",
            "duration_min": 23,
            "fare": 250,
            "first_departure": "08:57",
            "last_departure": "19:30",
            "frequency_min": 30,
        },
    ]

    # 既存の阪急バスセグメントを除去してから追加
    data["train_segments"] = [
        s for s in data["train_segments"] if s.get("line") != "hankyu_bus"
    ]
    data["train_segments"].extend(bus_segments)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Added 阪急バス (千里中央 ↔ 阪大本部前):")
    for s in bus_segments:
        print(f"  {s['from']} → {s['to']}  {s['duration_min']}min  {s['fare']}yen  every {s['frequency_min']}min")
    print(f"Added 阪大本部前 as nearby station for 吹田キャンパス (walk 3min)")


if __name__ == "__main__":
    main()
