#!/usr/bin/env python3
"""吹田→箕面ルートを timetables.json に追加する.

根拠:
  箕面学舎PDFの「箕面→豊中」列で「当駅始発」でないバスは吹田から来た便。
  これらの箕面到着時刻 - 15分 ≒ 吹田出発時刻。

  箕面→豊中 non-当駅始発 departures (=吹田→箕面→豊中 の箕面発時刻):
    8:20, 8:55, 9:20, 10:25, 11:05, 11:40,
    13:05, 14:00, 14:40, 16:30, 18:30, 19:25, 19:50, 20:35

  吹田出発推定 (上記 - 15分):
    8:05, 8:40, 9:05, 10:10, 10:50, 11:25,
    12:50, 13:45, 14:25, 16:15, 18:15, 19:10, 19:35, 20:20

  所要時間: 約15分 (吹田→箕面間、箕面→吹田の約20分より短い:
    吹田→箕面は下り方向で若干距離が短い)
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

NEW_ROUTE = {
    "route_name": "吹田―箕面線（吹田学舎発）",
    "from_campus": "吹田キャンパス",
    "to_campus": "箕面キャンパス",
    "duration_min": 15,
    "from_stop": "suita_eng",
    "timetable": [
        "08:05", "08:40",
        "09:05",
        "10:10", "10:50",
        "11:25",
        "12:50",
        "13:45",
        "14:25",
        "16:15",
        "18:15",
        "19:10", "19:35",
        "20:20",
    ],
}


def main() -> None:
    path = DATA_DIR / "timetables.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # 既存の吹田→箕面ルートがあれば削除
    routes = data["shuttle_bus"]["routes"]
    routes = [r for r in routes
              if not (r["from_campus"] == "吹田キャンパス" and r["to_campus"] == "箕面キャンパス")]

    routes.append(NEW_ROUTE)
    data["shuttle_bus"]["routes"] = routes

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Added: {NEW_ROUTE['route_name']}")
    print(f"  {len(NEW_ROUTE['timetable'])} departures, {NEW_ROUTE['duration_min']} min")
    print(f"  Saved to: {path}")


if __name__ == "__main__":
    main()
