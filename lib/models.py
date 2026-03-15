"""経路検索で使用するデータモデル."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Segment:
    """経路の1区間（乗車1回分）."""

    transport: str  # 交通手段名（例: "学内連絡バス", "大阪モノレール"）
    from_stop: str  # 乗車駅・停留所
    to_stop: str  # 降車駅・停留所
    depart: datetime  # 出発時刻
    arrive: datetime  # 到着時刻
    fare: int  # 運賃（円）。学内バスは0

    @property
    def duration_min(self) -> int:
        return int((self.arrive - self.depart).total_seconds() // 60)


@dataclass
class Route:
    """検索結果の1経路（複数Segmentで構成）."""

    segments: list[Segment] = field(default_factory=list)

    @property
    def total_fare(self) -> int:
        return sum(s.fare for s in self.segments)

    @property
    def total_duration_min(self) -> int:
        if not self.segments:
            return 0
        return int(
            (self.segments[-1].arrive - self.segments[0].depart).total_seconds() // 60
        )

    @property
    def summary(self) -> str:
        return " → ".join(s.transport for s in self.segments)

    def to_dict(self) -> dict:
        return {
            "summary": self.summary,
            "duration_min": self.total_duration_min,
            "fare": self.total_fare,
            "segments": [
                {
                    "transport": s.transport,
                    "from": s.from_stop,
                    "to": s.to_stop,
                    "depart": s.depart.strftime("%H:%M"),
                    "arrive": s.arrive.strftime("%H:%M"),
                    "duration_min": s.duration_min,
                    "fare": s.fare,
                }
                for s in self.segments
            ],
        }
