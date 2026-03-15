#!/usr/bin/env python3
"""吹田↔箕面のバス停経由情報を更新する.

実際のルート:
  吹田→箕面: 工学部前 発 → 人間科学部前 経由 → 箕面着
             (コンベンションセンター前は通らない)
  箕面→吹田: 箕面 発 → コンベンションセンター前 経由 → 工学部前 着
             (人間科学部前には行かない)
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    path = DATA_DIR / "timetables.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    for route in data["shuttle_bus"]["routes"]:
        name = route["route_name"]

        if name == "吹田―箕面線（吹田学舎発）":
            route["from_stop"] = "suita_eng"
            route["stops_via"] = ["suita_human"]
            route["to_stop"] = "minoh"
            route["route_detail"] = {
                "ja": "工学部前 → 人間科学部前 → 箕面学舎",
                "en": "Engineering → Human Sciences → Minoh",
            }

        elif name == "箕面―吹田線（箕面学舎発）":
            route["from_stop"] = "minoh"
            route["stops_via"] = ["suita_conv"]
            route["to_stop"] = "suita_eng"
            route["route_detail"] = {
                "ja": "箕面学舎 → コンベンションセンター前 → 工学部前",
                "en": "Minoh → Convention Center → Engineering",
            }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Updated stop details:")
    for route in data["shuttle_bus"]["routes"]:
        if "route_detail" in route:
            print(f"  {route['route_name']}")
            print(f"    {route['route_detail']['ja']}")
            print(f"    from={route.get('from_stop')} via={route.get('stops_via')} to={route.get('to_stop')}")


if __name__ == "__main__":
    main()
