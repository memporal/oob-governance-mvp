from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

import numpy as np
from sklearn.ensemble import IsolationForest


@dataclass
class Sample:
    timestamp: datetime
    value: float


def detect_timeseries_anomaly(samples: list[Sample], new_sample: Sample) -> bool:
    """Train locally from historical series and detect outlier deterministically."""
    if len(samples) < 24:
        return False

    by_hour: dict[int, list[float]] = defaultdict(list)
    for s in samples:
        by_hour[s.timestamp.hour].append(float(s.value))

    def feature(s: Sample) -> list[float]:
        hour_vals = by_hour.get(s.timestamp.hour, [s.value])
        baseline = float(np.mean(hour_vals)) if hour_vals else float(s.value)
        ratio = float(s.value) / (baseline + 1e-6)
        return [float(s.timestamp.hour), float(s.timestamp.weekday()), float(s.value), baseline, ratio]

    X = np.array([feature(s) for s in samples], dtype=float)
    model = IsolationForest(contamination=0.08, random_state=42)
    model.fit(X)

    pred = model.predict(np.array([feature(new_sample)], dtype=float))[0]
    return bool(pred == -1)
