#!/usr/bin/env python3
"""timetables.json を実データで一括更新するスクリプト.

更新内容:
  1. train_segments — 公式運賃表・時刻表に基づく実データ
  2. shuttle_bus.suspension_dates — 運休日カレンダー（HP_r7bus_unkyu.pdf 2025年度版）
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# ================================================================== #
#  鉄道 — 実データ (2025年 公式運賃表より)
# ================================================================== #
# 出典:
#   大阪モノレール公式 運賃表 https://www.osaka-monorail.co.jp/station/*/ticket/
#   北大阪急行 運賃表 https://www.kita-kyu.co.jp/pdf/fares.pdf
#   阪急電鉄 運賃検索 https://fare.hankyu.co.jp/
#
# 所要時間:
#   大阪モノレール 駅間約3分, 万博記念公園乗換+待ち約5分
#   北大阪急行 千里中央〜箕面船場阪大前 約3分
#   阪急 石橋阪大前〜蛍池 約2分, 山田〜北千里 約3分

REAL_TRAIN_SEGMENTS = [
    # ---- 大阪モノレール 本線 ----
    # 柴原阪大前 ↔ 蛍池（1駅, 3分）
    {"line": "monorail", "from": "shibahara", "to": "hotarugaike",
     "duration_min": 3, "fare": 200,
     "first_departure": "05:39", "last_departure": "23:56", "frequency_min": 10},
    {"line": "monorail", "from": "hotarugaike", "to": "shibahara",
     "duration_min": 3, "fare": 200,
     "first_departure": "05:45", "last_departure": "23:56", "frequency_min": 10},

    # 柴原阪大前 ↔ 千里中央（2駅, 6分）
    {"line": "monorail", "from": "shibahara", "to": "senri_chuo",
     "duration_min": 6, "fare": 250,
     "first_departure": "05:45", "last_departure": "23:56", "frequency_min": 10},
    {"line": "monorail", "from": "senri_chuo", "to": "shibahara",
     "duration_min": 6, "fare": 250,
     "first_departure": "05:39", "last_departure": "23:50", "frequency_min": 10},

    # 柴原阪大前 ↔ 山田（3駅, 9分）
    {"line": "monorail", "from": "shibahara", "to": "yamada",
     "duration_min": 9, "fare": 290,
     "first_departure": "05:45", "last_departure": "23:56", "frequency_min": 10},
    {"line": "monorail", "from": "yamada", "to": "shibahara",
     "duration_min": 9, "fare": 290,
     "first_departure": "05:39", "last_departure": "23:47", "frequency_min": 10},

    # ---- 大阪モノレール 本線+彩都線（万博記念公園乗換）----
    # 柴原阪大前 ↔ 阪大病院前（本線→万博乗換→彩都線, 約20分）
    {"line": "monorail", "from": "shibahara", "to": "handai_byoinmae",
     "duration_min": 20, "fare": 380,
     "first_departure": "05:45", "last_departure": "23:30", "frequency_min": 10},
    {"line": "monorail", "from": "handai_byoinmae", "to": "shibahara",
     "duration_min": 20, "fare": 380,
     "first_departure": "05:43", "last_departure": "23:30", "frequency_min": 10},

    # 阪大病院前 ↔ 千里中央（彩都線→万博乗換→本線, 約15分）
    {"line": "monorail", "from": "handai_byoinmae", "to": "senri_chuo",
     "duration_min": 15, "fare": 290,
     "first_departure": "05:43", "last_departure": "23:41", "frequency_min": 10},
    {"line": "monorail", "from": "senri_chuo", "to": "handai_byoinmae",
     "duration_min": 15, "fare": 290,
     "first_departure": "05:39", "last_departure": "23:30", "frequency_min": 10},

    # 阪大病院前 ↔ 山田（彩都線→万博乗換→本線1駅, 約10分）
    {"line": "monorail", "from": "handai_byoinmae", "to": "yamada",
     "duration_min": 10, "fare": 250,
     "first_departure": "05:43", "last_departure": "23:41", "frequency_min": 10},
    {"line": "monorail", "from": "yamada", "to": "handai_byoinmae",
     "duration_min": 10, "fare": 250,
     "first_departure": "05:45", "last_departure": "23:30", "frequency_min": 10},

    # ---- 北大阪急行 ----
    # 千里中央 ↔ 箕面船場阪大前（1駅, 3分）
    {"line": "kita_osaka_kyuko", "from": "senri_chuo", "to": "minoh_funaba",
     "duration_min": 3, "fare": 160,
     "first_departure": "05:26", "last_departure": "23:57", "frequency_min": 8},
    {"line": "kita_osaka_kyuko", "from": "minoh_funaba", "to": "senri_chuo",
     "duration_min": 3, "fare": 160,
     "first_departure": "05:30", "last_departure": "23:53", "frequency_min": 8},

    # ---- 阪急千里線 ----
    # 山田 ↔ 北千里（2駅, 3分）
    {"line": "hankyu_senri", "from": "yamada", "to": "kita_senri",
     "duration_min": 3, "fare": 170,
     "first_departure": "05:25", "last_departure": "23:58", "frequency_min": 8},
    {"line": "hankyu_senri", "from": "kita_senri", "to": "yamada",
     "duration_min": 3, "fare": 170,
     "first_departure": "05:22", "last_departure": "23:55", "frequency_min": 8},

    # ---- 阪急宝塚線 ----
    # 石橋阪大前 ↔ 蛍池（1駅, 2分）
    {"line": "hankyu_takarazuka", "from": "ishibashi", "to": "hotarugaike",
     "duration_min": 2, "fare": 170,
     "first_departure": "05:15", "last_departure": "00:05", "frequency_min": 7},
    {"line": "hankyu_takarazuka", "from": "hotarugaike", "to": "ishibashi",
     "duration_min": 2, "fare": 170,
     "first_departure": "05:18", "last_departure": "00:08", "frequency_min": 7},
]

# ================================================================== #
#  運休日カレンダー (HP_r7bus_unkyu.pdf 2025年度版)
# ================================================================== #
# 令和7年 = 2025, 令和8年 = 2026

SUSPENSION_DATES = [
    {"from": "2025-04-01", "to": "2025-04-09", "reason": "春季休業"},
    {"from": "2025-05-01", "to": "2025-05-02", "reason": "大学行事"},
    {"from": "2025-08-08", "to": "2025-09-30", "reason": "夏季休業"},
    {"from": "2025-10-31", "to": "2025-10-31", "reason": "大学行事"},
    {"from": "2025-11-04", "to": "2025-11-04", "reason": "大学行事"},
    {"from": "2025-11-27", "to": "2025-11-27", "reason": "大学行事"},
    {"from": "2025-12-29", "to": "2026-01-03", "reason": "冬季休業"},
    {"from": "2026-01-16", "to": "2026-01-16", "reason": "大学行事"},
    {"from": "2026-02-09", "to": "2026-03-31", "reason": "春季休業"},
]


def main() -> None:
    path = DATA_DIR / "timetables.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # 鉄道データ更新
    data["train_segments"] = REAL_TRAIN_SEGMENTS

    # 運休日カレンダー追加
    data["shuttle_bus"]["suspension_dates"] = SUSPENSION_DATES

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("=== 鉄道データ更新 ===")
    for seg in REAL_TRAIN_SEGMENTS:
        print(f"  {seg['from']:20s} -> {seg['to']:20s}  {seg['duration_min']:2d}分  {seg['fare']:3d}円  ({seg['line']})")
    print(f"  計 {len(REAL_TRAIN_SEGMENTS)} 区間")

    print("\n=== 運休日カレンダー ===")
    for d in SUSPENSION_DATES:
        print(f"  {d['from']} ~ {d['to']}  {d['reason']}")

    print(f"\n保存先: {path}")


if __name__ == "__main__":
    main()
