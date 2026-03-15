"""経路探索ロジック.

出発キャンパス・到着キャンパス・出発時刻を受け取り、
「最安ルート」と「最速ルート」を計算して返す。
"""

from datetime import datetime, timedelta

from lib.models import Route, Segment
from lib.timetable import (
    get_campus_stations,
    get_next_train,
    get_shuttle_departures,
    get_station_name,
    load_timetables,
)

# 乗換にかかる余裕時間（分）
TRANSFER_MARGIN_MIN = 3
# 1ルートの所要時間上限（分）— これを超える候補は除外
MAX_DURATION_MIN = 120

ALL_CAMPUSES = ["豊中キャンパス", "吹田キャンパス", "箕面キャンパス"]


def search_routes(
    origin: str, destination: str, depart_time: datetime,
    *, shuttle_available: bool = True,
    from_stop: str | None = None,
) -> list[dict]:
    """最安ルートと最速ルートを探索し、dict のリストで返す.

    from_stop: 出発キャンパス内の特定バス停ID（吹田の工学部前等）。
    """
    candidates = _collect_all_candidates(
        origin, destination, depart_time,
        shuttle_available=shuttle_available,
        from_stop=from_stop,
    )

    # 所要時間が上限を超える候補を除外
    candidates = [r for r in candidates if r.total_duration_min <= MAX_DURATION_MIN]

    next_morning = False

    # 候補なし → 翌朝始発で再探索
    if not candidates:
        tomorrow_morning = (depart_time + timedelta(days=1)).replace(
            hour=5, minute=0, second=0, microsecond=0,
        )
        candidates = _collect_all_candidates(
            origin, destination, tomorrow_morning,
            shuttle_available=shuttle_available,
            from_stop=from_stop,
        )
        candidates = [r for r in candidates if r.total_duration_min <= MAX_DURATION_MIN]
        next_morning = True

    if not candidates:
        return []

    MAX_RESULTS = 5

    # バス利用ルートと公共交通のみルートに分離
    bus_routes = [r for r in candidates if any("学内バス" in s.transport for s in r.segments)]
    transit_routes = [r for r in candidates if all("学内バス" not in s.transport for s in r.segments)]

    results: list[Route] = []

    # 学内バス: 最速1件
    if bus_routes:
        best_bus = min(bus_routes, key=lambda r: (r.segments[-1].arrive, r.total_duration_min))
        results.append(best_bus)

    # 公共交通: 経路パターン(summary)が異なるものを到着順で追加
    if transit_routes:
        transit_sorted = sorted(transit_routes, key=lambda r: (r.segments[-1].arrive, r.total_fare))
        seen_patterns: set[str] = set()
        for r in transit_sorted:
            if len(results) >= MAX_RESULTS:
                break
            if r.summary not in seen_patterns:
                seen_patterns.add(r.summary)
                results.append(r)

    if not results:
        best = min(candidates, key=lambda r: (r.segments[-1].arrive, r.total_fare))
        results.append(best)

    # 到着時刻でソート（最速が先）
    results.sort(key=lambda r: (r.segments[-1].arrive, r.total_fare))

    out = []
    for i, route in enumerate(results):
        d = route.to_dict()
        d["route_number"] = i + 1
        d["next_morning"] = next_morning
        out.append(d)
    return out


def _collect_all_candidates(
    origin: str, destination: str, depart_time: datetime,
    *, shuttle_available: bool = True,
    from_stop: str | None = None,
) -> list[Route]:
    """全ルート候補を列挙する."""
    candidates: list[Route] = []

    if shuttle_available:
        # 1) 直通シャトルバス
        candidates.extend(_shuttle_direct(origin, destination, depart_time, from_stop=from_stop))

    # 2) 公共交通機関（徒歩 + 電車 + 徒歩）
    candidates.extend(_transit_routes(origin, destination, depart_time))

    if shuttle_available:
        # 3) シャトルバスで中継キャンパス経由 → シャトル or 公共交通
        candidates.extend(_mixed_routes(origin, destination, depart_time, from_stop=from_stop))

    return candidates


# ------------------------------------------------------------------ #
#  1) 直通シャトルバス
# ------------------------------------------------------------------ #

def _shuttle_direct(
    origin: str, destination: str, depart_time: datetime,
    *, from_stop: str | None = None,
) -> list[Route]:
    """直通のシャトルバス便をルートとして返す（最大3便）."""
    departures = get_shuttle_departures(origin, destination, depart_time, from_stop=from_stop)
    routes = []
    for dep in departures[:3]:
        # Include route detail (stop sequence) if available
        detail = dep.get("route_detail")
        transport_name = f"学内バス（{dep['route_name']}）"
        seg = Segment(
            transport=transport_name,
            from_stop=origin,
            to_stop=destination,
            depart=dep["depart"],
            arrive=dep["arrive"],
            fare=0,
        )
        route = Route(segments=[seg])
        # attach route_detail as extra metadata
        route._route_details = {transport_name: detail} if detail else {}
        routes.append(route)
    return routes


# ------------------------------------------------------------------ #
#  2) 公共交通機関ルート
# ------------------------------------------------------------------ #

def _transit_routes(
    origin: str, destination: str, depart_time: datetime
) -> list[Route]:
    """キャンパス→徒歩→駅→(電車1~2本)→駅→徒歩→キャンパス のルートを列挙."""
    data = load_timetables()
    origin_stations = get_campus_stations(origin)
    dest_stations = get_campus_stations(destination)

    # 乗換候補駅 = 複数路線が乗り入れる駅
    transfer_ids = [
        sid for sid, info in data["stations"].items()
        if len(info["lines"]) > 1
    ]

    routes: list[Route] = []

    for os in origin_stations:
        for ds in dest_stations:
            # --- 直通（乗換なし）---
            route = _try_direct_train(origin, destination, os, ds, depart_time)
            if route:
                routes.append(route)

            # --- 1回乗換 ---
            for ts_id in transfer_ids:
                if ts_id in (os["station_id"], ds["station_id"]):
                    continue
                route = _try_one_transfer(
                    origin, destination, os, ds, ts_id, depart_time
                )
                if route:
                    routes.append(route)

    return routes


def _try_direct_train(
    origin: str, destination: str,
    os: dict, ds: dict,
    depart_time: datetime,
) -> Route | None:
    """直通電車1本で行けるルートを組み立てる."""
    walk_arrive = depart_time + timedelta(minutes=os["walk_min"])
    train = get_next_train(os["station_id"], ds["station_id"], walk_arrive)
    if not train:
        return None

    campus_arrive = train["arrive"] + timedelta(minutes=ds["walk_min"])

    return Route(segments=[
        _walk_seg(origin, get_station_name(os["station_id"]),
                  depart_time, walk_arrive),
        _train_seg(train, os["station_id"], ds["station_id"]),
        _walk_seg(get_station_name(ds["station_id"]), destination,
                  train["arrive"], campus_arrive),
    ])


def _get_through_fare(from_id: str, to_id: str) -> int | None:
    """直通運賃を検索する（同一運賃体系内の通し運賃）."""
    data = load_timetables()
    for seg in data["train_segments"]:
        if seg["from"] == from_id and seg["to"] == to_id:
            return seg["fare"]
    return None


def _try_one_transfer(
    origin: str, destination: str,
    os: dict, ds: dict, transfer_id: str,
    depart_time: datetime,
) -> Route | None:
    """1回乗換ルートを組み立てる."""
    walk_arrive = depart_time + timedelta(minutes=os["walk_min"])

    train1 = get_next_train(os["station_id"], transfer_id, walk_arrive)
    if not train1:
        return None

    transfer_ready = train1["arrive"] + timedelta(minutes=TRANSFER_MARGIN_MIN)
    train2 = get_next_train(transfer_id, ds["station_id"], transfer_ready)
    if not train2:
        return None

    # 同一路線の乗継は通し運賃を適用
    if train1["line"] == train2["line"]:
        through_fare = _get_through_fare(os["station_id"], ds["station_id"])
        if through_fare is not None:
            # 通し運賃を2区間に按分: 1区間目に全額、2区間目を0円
            train1 = {**train1, "fare": through_fare}
            train2 = {**train2, "fare": 0}

    campus_arrive = train2["arrive"] + timedelta(minutes=ds["walk_min"])

    return Route(segments=[
        _walk_seg(origin, get_station_name(os["station_id"]),
                  depart_time, walk_arrive),
        _train_seg(train1, os["station_id"], transfer_id),
        _train_seg(train2, transfer_id, ds["station_id"]),
        _walk_seg(get_station_name(ds["station_id"]), destination,
                  train2["arrive"], campus_arrive),
    ])


# ------------------------------------------------------------------ #
#  3) シャトル経由 → 中継キャンパスから公共交通 or シャトル
# ------------------------------------------------------------------ #

def _mixed_routes(
    origin: str, destination: str, depart_time: datetime,
    *, from_stop: str | None = None,
) -> list[Route]:
    """シャトルバスで中継キャンパスへ行き、そこから先は別手段で目的地へ向かう."""
    routes: list[Route] = []

    for mid_campus in ALL_CAMPUSES:
        if mid_campus in (origin, destination):
            continue

        shuttle_deps = get_shuttle_departures(origin, mid_campus, depart_time, from_stop=from_stop)
        if not shuttle_deps:
            continue

        # 最初の便だけ使う（候補を絞る）
        first = shuttle_deps[0]
        shuttle_seg = Segment(
            transport=f"学内バス（{first['route_name']}）",
            from_stop=origin,
            to_stop=mid_campus,
            depart=first["depart"],
            arrive=first["arrive"],
            fare=0,
        )

        # 中継 → 目的地: シャトル
        shuttle2_deps = get_shuttle_departures(mid_campus, destination, first["arrive"])
        if shuttle2_deps:
            s2 = shuttle2_deps[0]
            seg2 = Segment(
                transport=f"学内バス（{s2['route_name']}）",
                from_stop=mid_campus,
                to_stop=destination,
                depart=s2["depart"],
                arrive=s2["arrive"],
                fare=0,
            )
            routes.append(Route(segments=[shuttle_seg, seg2]))

        # 中継 → 目的地: 公共交通
        transit = _transit_routes(mid_campus, destination, first["arrive"])
        for tr in transit[:2]:
            routes.append(Route(segments=[shuttle_seg] + tr.segments))

    return routes


# ------------------------------------------------------------------ #
#  ヘルパー
# ------------------------------------------------------------------ #

def _walk_seg(from_stop: str, to_stop: str, depart: datetime, arrive: datetime) -> Segment:
    return Segment(
        transport="徒歩",
        from_stop=from_stop,
        to_stop=to_stop,
        depart=depart,
        arrive=arrive,
        fare=0,
    )


def _train_seg(train: dict, from_id: str, to_id: str) -> Segment:
    return Segment(
        transport=train["line_name"],
        from_stop=get_station_name(from_id),
        to_stop=get_station_name(to_id),
        depart=train["depart"],
        arrive=train["arrive"],
        fare=train["fare"],
    )
