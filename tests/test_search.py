"""経路探索・時刻表のテスト."""

from datetime import datetime

from lib.models import Route, Segment
from lib.search import search_routes, _collect_all_candidates
from lib.timetable import (
    get_campus_stations,
    get_line_name,
    get_next_train,
    get_shuttle_departures,
    get_shuttle_status,
    get_shuttle_last_time,
    get_station_name,
    is_shuttle_suspended,
)


# ==================================================================
#  models
# ==================================================================

def test_route_total_fare():
    r = Route(segments=[
        Segment("バスA", "X", "Y", datetime(2026, 1, 1, 9, 0), datetime(2026, 1, 1, 9, 15), 0),
        Segment("電車B", "Y", "Z", datetime(2026, 1, 1, 9, 20), datetime(2026, 1, 1, 9, 40), 200),
    ])
    assert r.total_fare == 200
    assert r.total_duration_min == 40
    assert r.summary == "バスA → 電車B"


def test_route_to_dict():
    r = Route(segments=[
        Segment("学内バス", "豊中", "吹田", datetime(2026, 1, 1, 9, 0), datetime(2026, 1, 1, 9, 20), 0),
    ])
    d = r.to_dict()
    assert d["fare"] == 0
    assert d["duration_min"] == 20
    assert d["segments"][0]["depart"] == "09:00"


# ==================================================================
#  stations / lines
# ==================================================================

def test_get_campus_stations():
    ids = [s["station_id"] for s in get_campus_stations("豊中キャンパス")]
    assert "ishibashi" in ids and "shibahara" in ids


def test_get_station_name():
    assert get_station_name("ishibashi") == "石橋阪大前"
    assert get_station_name("minoh_funaba") == "箕面船場阪大前"


def test_get_line_name():
    assert get_line_name("monorail") == "大阪モノレール"
    assert get_line_name("kita_osaka_kyuko") == "北大阪急行"


# ==================================================================
#  suspension calendar
# ==================================================================

def test_suspension_weekend():
    from datetime import date
    sus, reason = is_shuttle_suspended(date(2025, 6, 7))  # 通常の土曜
    assert sus is True
    assert "土日" in reason


def test_suspension_summer():
    from datetime import date
    sus, reason = is_shuttle_suspended(date(2025, 8, 15))  # 夏季休業中
    assert sus is True
    assert "夏季" in reason


def test_suspension_normal_weekday():
    from datetime import date
    sus, _ = is_shuttle_suspended(date(2025, 6, 2))  # 通常平日
    assert sus is False


def test_suspension_spring_break():
    from datetime import date
    sus, reason = is_shuttle_suspended(date(2026, 3, 2))  # 春季休業（月曜）
    assert sus is True
    assert "春季" in reason


# ==================================================================
#  shuttle departures (real data)
# ==================================================================

def test_shuttle_weekday_real():
    dt = datetime(2025, 6, 2, 8, 0)  # 月曜・通常授業期間
    deps = get_shuttle_departures("豊中キャンパス", "吹田キャンパス", dt)
    assert len(deps) > 0
    assert deps[0]["depart"].hour == 8
    assert deps[0]["duration_min"] == 25


def test_shuttle_count():
    dt = datetime(2025, 6, 2, 0, 0)
    deps = get_shuttle_departures("豊中キャンパス", "吹田キャンパス", dt)
    assert len(deps) == 30


def test_shuttle_weekend_empty():
    dt = datetime(2026, 1, 3, 9, 0)
    assert get_shuttle_departures("豊中キャンパス", "吹田キャンパス", dt) == []


def test_shuttle_summer_empty():
    dt = datetime(2025, 8, 20, 9, 0)  # 夏季休業中
    assert get_shuttle_departures("豊中キャンパス", "吹田キャンパス", dt) == []


def test_shuttle_minoh_to_suita():
    dt = datetime(2025, 6, 2, 0, 0)
    deps = get_shuttle_departures("箕面キャンパス", "吹田キャンパス", dt)
    assert len(deps) == 11
    assert deps[0]["depart"].strftime("%H:%M") == "07:35"


# ==================================================================
#  shuttle status
# ==================================================================

def test_status_running():
    dt = datetime(2025, 6, 2, 9, 0)
    status, _ = get_shuttle_status("豊中キャンパス", "吹田キャンパス", dt)
    assert status == "running"


def test_status_ended():
    dt = datetime(2025, 6, 2, 20, 30)
    status, _ = get_shuttle_status("豊中キャンパス", "吹田キャンパス", dt)
    assert status == "ended"


def test_status_suspended():
    dt = datetime(2025, 8, 20, 9, 0)  # 夏季休業
    status, _ = get_shuttle_status("豊中キャンパス", "吹田キャンパス", dt)
    assert status == "suspended"


def test_status_suita_minoh_running():
    """吹田→箕面の直通バスが運行中."""
    dt = datetime(2025, 6, 2, 9, 0)
    status, _ = get_shuttle_status("吹田キャンパス", "箕面キャンパス", dt)
    assert status == "running"


def test_shuttle_last():
    assert get_shuttle_last_time("豊中キャンパス", "吹田キャンパス") == "20:10"


# ==================================================================
#  trains (real fares)
# ==================================================================

def test_train_monorail_fare():
    dt = datetime(2025, 6, 2, 9, 0)
    r = get_next_train("shibahara", "senri_chuo", dt)
    assert r is not None
    assert r["fare"] == 250  # 実運賃
    assert r["duration_min"] == 6


def test_train_monorail_shibahara_handai():
    dt = datetime(2025, 6, 2, 9, 0)
    r = get_next_train("shibahara", "handai_byoinmae", dt)
    assert r is not None
    assert r["fare"] == 380  # 万博乗換
    assert r["duration_min"] == 20


def test_train_kitakyu():
    dt = datetime(2025, 6, 2, 9, 0)
    r = get_next_train("senri_chuo", "minoh_funaba", dt)
    assert r is not None
    assert r["fare"] == 160  # 実運賃
    assert r["duration_min"] == 3


def test_train_hankyu():
    dt = datetime(2025, 6, 2, 9, 0)
    r = get_next_train("ishibashi", "hotarugaike", dt)
    assert r is not None
    assert r["fare"] == 170
    assert r["duration_min"] == 2


def test_train_after_last():
    dt = datetime(2025, 6, 2, 23, 59)
    assert get_next_train("shibahara", "handai_byoinmae", dt) is None


# ==================================================================
#  search_routes
# ==================================================================

def test_toyonaka_suita_weekday_both_routes():
    """平日: 学内バスと公共交通の両方が返る."""
    dt = datetime(2025, 6, 2, 9, 0)
    results = search_routes("豊中キャンパス", "吹田キャンパス", dt)
    assert len(results) >= 2
    has_bus = any(r["fare"] == 0 for r in results)
    has_transit = any(r["fare"] > 0 for r in results)
    assert has_bus
    assert has_transit
    assert results[0]["route_number"] == 1


def test_toyonaka_suita_weekend():
    """土曜: 公共交通のみ."""
    dt = datetime(2025, 6, 7, 10, 0)
    results = search_routes("豊中キャンパス", "吹田キャンパス", dt)
    assert len(results) >= 1
    for r in results:
        assert r["fare"] > 0


def test_shuttle_disabled():
    dt = datetime(2025, 6, 2, 9, 0)
    results = search_routes("豊中キャンパス", "吹田キャンパス", dt, shuttle_available=False)
    for r in results:
        assert r["fare"] > 0


def test_toyonaka_minoh():
    dt = datetime(2025, 6, 2, 9, 0)
    results = search_routes("豊中キャンパス", "箕面キャンパス", dt)
    has_bus = any(r["fare"] == 0 for r in results)
    assert has_bus


def test_minoh_toyonaka():
    dt = datetime(2025, 6, 2, 10, 0)
    results = search_routes("箕面キャンパス", "豊中キャンパス", dt)
    has_bus = any(r["fare"] == 0 for r in results)
    assert has_bus


def test_bus_ended_fallback():
    """バス終了後: 公共交通のみ."""
    dt = datetime(2025, 6, 2, 21, 0)
    results = search_routes("豊中キャンパス", "吹田キャンパス", dt)
    assert len(results) >= 1
    for r in results:
        assert r["fare"] > 0


def test_late_night_next_morning():
    """深夜 → 翌朝始発ルートが返る."""
    dt = datetime(2025, 6, 2, 23, 58)
    results = search_routes("豊中キャンパス", "吹田キャンパス", dt)
    assert len(results) >= 1
    assert results[0]["next_morning"] is True


def test_daytime_not_next_morning():
    dt = datetime(2025, 6, 2, 9, 0)
    results = search_routes("豊中キャンパス", "吹田キャンパス", dt)
    assert results[0]["next_morning"] is False


def test_candidates_count():
    dt = datetime(2025, 6, 2, 9, 0)
    candidates = _collect_all_candidates("豊中キャンパス", "吹田キャンパス", dt)
    assert len(candidates) >= 4
