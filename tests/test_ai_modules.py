from datetime import datetime, timedelta

from app.ai.anomaly import Sample, detect_timeseries_anomaly
from app.ai.rf_ml import RFSignatureClassifier


def test_rf_classifier_shape_and_label():
    clf = RFSignatureClassifier()
    out = clf.predict([0.1, 0.2, -0.4, 0.7, 1.2])
    assert out["label"] in {"authentic", "clone_suspected"}
    assert 0.0 <= out["score"] <= 1.0


def test_isolation_forest_anomaly_deterministic():
    base = datetime(2026, 1, 1, 2, 0, 0)
    history = [Sample(timestamp=base + timedelta(days=i), value=100.0) for i in range(35)]
    normal = Sample(timestamp=base + timedelta(days=36), value=103.0)
    spike = Sample(timestamp=base + timedelta(days=36, hours=12), value=5000.0)

    assert detect_timeseries_anomaly(history, normal) is False
    assert detect_timeseries_anomaly(history, spike) is True
