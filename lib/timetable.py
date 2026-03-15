"""時刻表データの読み込みと管理."""

import json
from datetime import date, datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

_cache: dict | None = None


def load_timetables() -> dict:
    """data/timetables.json を読み込んで返す（キャッシュ付き）."""
    global _cache
    if _cache is None:
        path = DATA_DIR / "timetables.json"
        with open(path, encoding="utf-8") as f:
            _cache = json.load(f)
    return _cache


# ------------------------------------------------------------------ #
#  駅・路線マスタ
# ------------------------------------------------------------------ #

def get_campus_stations(campus: str) -> list[dict]:
    """キャンパスに紐づく最寄り駅リスト（station_id, walk_min）を返す."""
    data = load_timetables()
    return data["campuses"][campus]["nearby_stations"]


def get_station_name(station_id: str) -> str:
    data = load_timetables()
    return data["stations"][station_id]["name"]


def get_line_name(line_id: str) -> str:
    data = load_timetables()
    return data["lines"][line_id]["name"]


# ------------------------------------------------------------------ #
#  運休日判定
# ------------------------------------------------------------------ #

def is_shuttle_suspended(target: date) -> tuple[bool, str]:
    """指定日が学内バス運休日かどうか判定する.

    Returns:
        (True/False, 理由文字列)
    """
    # カレンダー運休日を先にチェック（休業期間中の土日は休業理由を表示）
    data = load_timetables()
    for period in data["shuttle_bus"].get("suspension_dates", []):
        start = date.fromisoformat(period["from"])
        end = date.fromisoformat(period["to"])
        if start <= target <= end:
            return True, period["reason"]

    # 土日
    if target.weekday() >= 5:
        return True, "土日のため運休"

    return False, ""


# ------------------------------------------------------------------ #
#  学内バス
# ------------------------------------------------------------------ #

def get_bus_stops(campus: str) -> list[dict]:
    """キャンパスのバス停一覧を返す。バス停が定義されていなければ空リスト."""
    data = load_timetables()
    return data["campuses"].get(campus, {}).get("bus_stops", [])


def get_shuttle_departures(
    from_campus: str, to_campus: str, after: datetime,
    *, from_stop: str | None = None,
) -> list[dict]:
    """指定時刻以降の学内バス出発便を返す.

    from_stop を指定すると、そのバス停から発車する便のみに絞り込む。
    """
    suspended, _ = is_shuttle_suspended(after.date())
    if suspended:
        return []

    data = load_timetables()
    results = []
    for route in data["shuttle_bus"]["routes"]:
        if route["from_campus"] != from_campus or route["to_campus"] != to_campus:
            continue
        # バス停フィルタ
        if from_stop and route.get("from_stop") and route["from_stop"] != from_stop:
            continue
        for time_str in route["timetable"]:
            h, m = map(int, time_str.split(":"))
            depart = after.replace(hour=h, minute=m, second=0, microsecond=0)
            if depart < after:
                continue
            arrive = depart + timedelta(minutes=route["duration_min"])
            results.append(
                {
                    "depart": depart,
                    "arrive": arrive,
                    "duration_min": route["duration_min"],
                    "route_name": route["route_name"],
                    "from_stop": route.get("from_stop"),
                    "to_stop": route.get("to_stop"),
                }
            )
    results.sort(key=lambda x: x["depart"])
    return results


def get_shuttle_status(
    from_campus: str, to_campus: str, at: datetime
) -> tuple[str, str]:
    """学内バスの運行ステータスを返す.

    Returns:
        (status, reason)
        status: "running" / "ended" / "suspended" / "none"
    """
    suspended, reason = is_shuttle_suspended(at.date())
    if suspended:
        return "suspended", reason

    data = load_timetables()
    has_route = False
    for route in data["shuttle_bus"]["routes"]:
        if route["from_campus"] != from_campus or route["to_campus"] != to_campus:
            continue
        has_route = True
        for time_str in route["timetable"]:
            h, m = map(int, time_str.split(":"))
            depart = at.replace(hour=h, minute=m, second=0, microsecond=0)
            if depart >= at:
                return "running", ""

    if has_route:
        return "ended", "本日の運行は終了"
    return "none", "この区間に直通バスはありません"


def get_shuttle_last_time(from_campus: str, to_campus: str) -> str | None:
    """指定区間の最終バス時刻を返す."""
    data = load_timetables()
    last = None
    for route in data["shuttle_bus"]["routes"]:
        if route["from_campus"] != from_campus or route["to_campus"] != to_campus:
            continue
        if route["timetable"]:
            t = route["timetable"][-1]
            if last is None or t > last:
                last = t
    return last


# ------------------------------------------------------------------ #
#  鉄道
# ------------------------------------------------------------------ #

def get_next_train(
    from_station: str, to_station: str, after: datetime
) -> dict | None:
    """指定時刻以降の次の電車を返す."""
    data = load_timetables()
    for seg in data["train_segments"]:
        if seg["from"] != from_station or seg["to"] != to_station:
            continue

        first_h, first_m = map(int, seg["first_departure"].split(":"))
        last_h, last_m = map(int, seg["last_departure"].split(":"))
        first_time = after.replace(hour=first_h, minute=first_m, second=0, microsecond=0)
        last_time = after.replace(hour=last_h, minute=last_m, second=0, microsecond=0)

        # 終電が日付をまたぐ場合（例: 00:05）
        if last_time < first_time:
            last_time += timedelta(days=1)

        if after > last_time:
            return None

        if after <= first_time:
            depart = first_time
        else:
            elapsed = (after - first_time).total_seconds() / 60
            next_slot = (int(elapsed) // seg["frequency_min"] + 1) * seg["frequency_min"]
            depart = first_time + timedelta(minutes=next_slot)
            if depart > last_time:
                return None

        arrive = depart + timedelta(minutes=seg["duration_min"])
        return {
            "depart": depart,
            "arrive": arrive,
            "duration_min": seg["duration_min"],
            "fare": seg["fare"],
            "line": seg["line"],
            "line_name": get_line_name(seg["line"]),
        }

    return None
