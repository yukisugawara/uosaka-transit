#!/usr/bin/env python3
"""shuttle_bus routes に from_stop / to_stop を追加する.

吹田キャンパスのバス停:
  - 人間科学部前 (suita_human)
  - 工学部前 (suita_eng)
  - コンベンションセンター前 (suita_conv)

豊中・箕面はキャンパス全体で1つのバス停扱い:
  - 豊中学舎 (toyonaka)
  - 箕面学舎 (minoh)
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# route_name → (from_stop, to_stop) マッピング
STOP_MAP = {
    "豊中―吹田線（豊中学舎発）": ("toyonaka", None),  # 吹田側は全停留所に停車
    "吹田―豊中線（工学部前発）": ("suita_eng", "toyonaka"),
    "吹田―豊中線（人間科学部前発）": ("suita_human", "toyonaka"),
    "豊中―箕面線（豊中学舎発）": ("toyonaka", "minoh"),
    "箕面―豊中線（箕面学舎発）": ("minoh", "toyonaka"),
    "箕面―吹田線（箕面学舎発）": ("minoh", None),  # 吹田側は全停留所に停車
}


def main() -> None:
    path = DATA_DIR / "timetables.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    for route in data["shuttle_bus"]["routes"]:
        name = route["route_name"]
        if name in STOP_MAP:
            fs, ts = STOP_MAP[name]
            if fs:
                route["from_stop"] = fs
            if ts:
                route["to_stop"] = ts

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Updated routes:")
    for route in data["shuttle_bus"]["routes"]:
        fs = route.get("from_stop", "-")
        ts = route.get("to_stop", "-")
        print(f"  {route['route_name']:40s}  from_stop={fs:15s}  to_stop={ts}")


if __name__ == "__main__":
    main()
