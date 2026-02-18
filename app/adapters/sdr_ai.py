from __future__ import annotations

import os

import httpx


SDR_AI_URL = os.getenv("SDR_AI_URL", "http://sdr-ai:8100")


def classify_iq_samples(iq_samples: list[float]) -> dict[str, float | str] | None:
    if not iq_samples:
        return None
    try:
        with httpx.Client(timeout=2.0) as client:
            resp = client.post(f"{SDR_AI_URL}/classify", json={"iq_samples": iq_samples})
            resp.raise_for_status()
            return resp.json()
    except Exception:
        return None
