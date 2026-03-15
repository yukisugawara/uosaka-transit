"""多言語対応 (日本語 / English)."""

STRINGS: dict[str, dict[str, str]] = {
    # hero
    "subtitle": {
        "ja": "Osaka University Inter-Campus Route Finder",
        "en": "Osaka University Inter-Campus Route Finder",
    },
    # campus selector
    "from": {"ja": "\U0001F7E3 出発", "en": "\U0001F7E3 From"},
    "to": {"ja": "\U0001F7E2 到着", "en": "\U0001F7E2 To"},
    # campus short names
    "toyonaka": {"ja": "豊中", "en": "Toyonaka"},
    "suita": {"ja": "吹田", "en": "Suita"},
    "minoh": {"ja": "箕面", "en": "Minoh"},
    # time
    "depart_now": {"ja": "\u23F0 いま出発", "en": "\u23F0 Depart now"},
    "depart_at": {"ja": "\u23F0 {time} 発", "en": "\u23F0 Depart {time}"},
    "date_label": {"ja": "\U0001F4C5 日付", "en": "\U0001F4C5 Date"},
    "time_label": {"ja": "\u23F0 時刻", "en": "\u23F0 Time"},
    # shuttle status
    "shuttle_running": {"ja": "\u2705 学内バス運行日", "en": "\u2705 Campus bus running"},
    "shuttle_suspended": {
        "ja": "\U0001F6AB {reason}",
        "en": "\U0001F6AB Bus suspended: {reason}",
    },
    "exclude_bus": {"ja": "学内バスを除外する", "en": "Exclude campus bus"},
    # search
    "search_btn": {"ja": "\u2728 ルートを検索", "en": "\u2728 Search routes"},
    "searching": {"ja": "検索中...", "en": "Searching..."},
    "same_campus": {
        "ja": "同じキャンパスが選ばれています",
        "en": "Same campus selected for both",
    },
    # status messages
    "bus_ended": {
        "ja": "\U0001F68C 本日の学内バスは終了しました{last}",
        "en": "\U0001F68C Campus bus service has ended for today{last}",
    },
    "no_direct_bus": {
        "ja": "この区間に直通バスはありません。経由便・公共交通で検索しました。",
        "en": "No direct campus bus for this route. Showing transfer / public transit options.",
    },
    "no_route": {
        "ja": "ルートが見つかりませんでした。時刻を変えて試してみてください。",
        "en": "No routes found. Try a different time.",
    },
    "next_morning": {
        "ja": "\U0001F305 本日の運行は終了しています。翌朝の始発ルートを表示します。",
        "en": "\U0001F305 Service has ended. Showing first routes tomorrow morning.",
    },
    # route labels
    "label_bus": {"ja": "学内バス", "en": "Campus Bus"},
    "label_transit": {"ja": "公共交通", "en": "Public Transit"},
    "label_fastest": {"ja": "最速ルート", "en": "Fastest"},
    # segments
    "walk": {"ja": "徒歩", "en": "Walk"},
    "min": {"ja": "分", "en": "min"},
    "yen": {"ja": "円", "en": "\u00A5"},
    "free_label": {"ja": "0円 FREE", "en": "FREE"},
    # suspension reasons
    "reason_weekend": {"ja": "土日のため運休", "en": "Weekend (no service)"},
    "reason_spring": {"ja": "春季休業", "en": "Spring break"},
    "reason_summer": {"ja": "夏季休業", "en": "Summer break"},
    "reason_winter": {"ja": "冬季休業", "en": "Winter break"},
    "reason_event": {"ja": "大学行事", "en": "University event"},
    # bus stops
    "all_stops": {"ja": "すべての停留所", "en": "All stops"},
    "bus_stop_label": {"ja": "\U0001F68F 停留所", "en": "\U0001F68F Bus stop"},
    # footer
    "footer": {
        "ja": "学内バス: 2025/4/1改正ダイヤ（平日運行）\u00A0\u00A0|\u00A0\u00A0"
              "鉄道: 大阪モノレール・北大阪急行・阪急電鉄 公式運賃に基づく",
        "en": "Campus bus: 2025/4/1 revised timetable (weekdays)\u00A0\u00A0|\u00A0\u00A0"
              "Rail: Osaka Monorail \u00B7 Kita-Osaka Kyuko \u00B7 Hankyu (official fares)",
    },
}

# transport name translations (for result cards)
TRANSPORT: dict[str, dict[str, str]] = {
    "徒歩": {"ja": "徒歩", "en": "Walk"},
    "大阪モノレール": {"ja": "大阪モノレール", "en": "Osaka Monorail"},
    "阪急宝塚線": {"ja": "阪急宝塚線", "en": "Hankyu Takarazuka Line"},
    "阪急千里線": {"ja": "阪急千里線", "en": "Hankyu Senri Line"},
    "北大阪急行": {"ja": "北大阪急行", "en": "Kita-Osaka Kyuko"},
    "阪急バス": {"ja": "阪急バス", "en": "Hankyu Bus"},
}

# campus full-name translations
CAMPUS_NAME: dict[str, dict[str, str]] = {
    "豊中キャンパス": {"ja": "豊中キャンパス", "en": "Toyonaka Campus"},
    "吹田キャンパス": {"ja": "吹田キャンパス", "en": "Suita Campus"},
    "箕面キャンパス": {"ja": "箕面キャンパス", "en": "Minoh Campus"},
}

# station name translations
STATION_NAME: dict[str, dict[str, str]] = {
    "石橋阪大前": {"ja": "石橋阪大前", "en": "Ishibashi-Handaimae"},
    "柴原阪大前": {"ja": "柴原阪大前", "en": "Shibahara-Handaimae"},
    "阪大病院前": {"ja": "阪大病院前", "en": "Handai-Byoinmae"},
    "北千里": {"ja": "北千里", "en": "Kita-Senri"},
    "千里中央": {"ja": "千里中央", "en": "Senri-Chuo"},
    "箕面船場阪大前": {"ja": "箕面船場阪大前", "en": "Minoh-Funaba-Handaimae"},
    "山田": {"ja": "山田", "en": "Yamada"},
    "蛍池": {"ja": "蛍池", "en": "Hotarugaike"},
    "阪大本部前": {"ja": "阪大本部前", "en": "Handai Honbu-mae"},
    "人間科学部前": {"ja": "人間科学部前", "en": "Human Sciences Bldg."},
    "工学部前": {"ja": "工学部前", "en": "Engineering Bldg."},
    "コンベンションセンター前": {"ja": "コンベンションセンター前", "en": "Convention Center"},
}


def t(key: str, lang: str, **kwargs: str) -> str:
    """翻訳文字列を返す."""
    s = STRINGS.get(key, {}).get(lang, STRINGS.get(key, {}).get("ja", key))
    if kwargs:
        s = s.format(**kwargs)
    return s


def t_transport(name: str, lang: str) -> str:
    """交通手段名を翻訳する。学内バス路線名はそのまま返す."""
    if "学内バス" in name:
        if lang == "en":
            route = name.replace("学内バス（", "").rstrip("）")
            return f"Campus Bus ({route})"
        return name
    for ja, translations in TRANSPORT.items():
        if ja in name:
            return translations.get(lang, name)
    return name


def t_place(name: str, lang: str) -> str:
    """場所名（キャンパス名・駅名）を翻訳する."""
    if name in CAMPUS_NAME:
        return CAMPUS_NAME[name].get(lang, name)
    if name in STATION_NAME:
        return STATION_NAME[name].get(lang, name)
    return name


def t_reason(reason: str, lang: str) -> str:
    """運休理由を翻訳する."""
    for key in ("reason_weekend", "reason_spring", "reason_summer",
                "reason_winter", "reason_event"):
        ja = STRINGS[key]["ja"]
        if ja in reason or reason == ja:
            return STRINGS[key].get(lang, reason)
    return reason
