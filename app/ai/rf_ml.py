from __future__ import annotations

import json
from pathlib import Path

import numpy as np

MODEL_PATH = Path("/models/rf_signature_model.json")


class RFSignatureClassifier:
    """Tiny edge classifier over raw I/Q samples.

    This is intentionally lightweight for air-gapped edge deployments.
    """

    def __init__(self, model_path: Path = MODEL_PATH):
        if model_path.exists():
            payload = json.loads(model_path.read_text())
        else:
            payload = {"weights": [3.2, -2.7, 1.9], "bias": -0.4}
        self.weights = np.array(payload["weights"], dtype=float)
        self.bias = float(payload["bias"])

    @staticmethod
    def _features(iq_samples: list[float]) -> np.ndarray:
        arr = np.array(iq_samples, dtype=float)
        if arr.size == 0:
            return np.array([0.0, 0.0, 0.0])
        # Simple RF fingerprint features: variance, mean absolute phase-delta proxy, kurtosis-like measure
        variance = float(np.var(arr))
        phase_noise_proxy = float(np.mean(np.abs(np.diff(arr)))) if arr.size > 1 else 0.0
        centered = arr - np.mean(arr)
        fourth = float(np.mean(centered**4)) if arr.size > 0 else 0.0
        second = float(np.mean(centered**2)) if arr.size > 0 else 1.0
        kurtosis_proxy = fourth / (second**2 + 1e-9)
        return np.array([variance, phase_noise_proxy, kurtosis_proxy])

    def predict(self, iq_samples: list[float]) -> dict[str, float | str]:
        x = self._features(iq_samples)
        score = float(np.dot(self.weights, x) + self.bias)
        prob_clone = 1.0 / (1.0 + np.exp(-score))
        label = "clone_suspected" if prob_clone >= 0.5 else "authentic"
        return {"label": label, "score": round(prob_clone, 6)}
