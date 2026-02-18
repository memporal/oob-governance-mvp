#!/usr/bin/env bash
set -euo pipefail

cleanup() {
  docker compose down -v >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "[1/7] Starting stack"
docker compose up -d --build

echo "[2/7] Waiting for API"
for _ in {1..90}; do
  if curl -fsS http://localhost:8000/health >/dev/null; then
    break
  fi
  sleep 2
done
curl -fsS http://localhost:8000/health >/dev/null

echo "[3/7] Seeding DB"
docker compose exec -T app python scripts/seed.py

echo "[4/7] Sending syslog messages"
for i in $(seq 1 20); do
  asn=$((65000 + i))
  line="<134>1 2026-01-01T00:00:00Z edge-router bgp - - - site=site-a link=wan1 asn=${asn}"
  payload=$(printf '{"line":"%s","iq_samples":[0.1,0.8,-0.2,0.9,0.0,0.2]}' "$line")
  curl -fsS -X POST http://localhost:8000/ingest/syslog \
    -H 'content-type: application/json' \
    -d "$payload" >/dev/null
done

echo "[5/7] Verifying /fleet"
fleet_json="$(curl -fsS http://localhost:8000/fleet)"
FLEET_JSON="$fleet_json" python - <<'PY'
import json, os
fleet = json.loads(os.environ["FLEET_JSON"])
assert fleet["sites"] > 0, fleet
assert fleet["links"] > 0, fleet
print(f"fleet ok: {fleet}")
PY

echo "[6/7] Verifying /alerts"
alerts_json="$(curl -fsS http://localhost:8000/alerts)"
ALERTS_JSON="$alerts_json" python - <<'PY'
import json, os
alerts = json.loads(os.environ["ALERTS_JSON"])
assert len(alerts) > 0, alerts
assert any(a["event_type"] in {"new_asn","behavioral_anomaly","hardware_spoofing"} for a in alerts), alerts
print(f"alerts ok: {len(alerts)} events")
PY

echo "[7/7] Verifying /triage"
triage=$(curl -fsS -X POST http://localhost:8000/triage -H 'content-type: application/json' -d '{"question":"Why is site-a risky?"}')
TRIAGE_JSON="$triage" python - <<'PY'
import json, os
body = json.loads(os.environ["TRIAGE_JSON"])
assert "answer" in body, body
print("triage ok")
PY

echo "Smoke test passed"
