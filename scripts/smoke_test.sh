#!/usr/bin/env bash
set -euo pipefail

cleanup() {
  docker compose down -v >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "[1/6] Starting stack"
docker compose up -d --build

echo "[2/6] Waiting for API"
for _ in {1..60}; do
  if curl -fsS http://localhost:8000/health >/dev/null; then
    break
  fi
  sleep 2
done
curl -fsS http://localhost:8000/health >/dev/null

echo "[3/6] Seeding DB"
docker compose exec -T app python scripts/seed.py

echo "[4/6] Sending syslog messages"
for i in $(seq 1 20); do
  asn=$((65000 + i))
  line="<134>1 2026-01-01T00:00:00Z edge-router bgp - - - site=site-a link=wan1 asn=${asn}"
  curl -fsS -X POST http://localhost:8000/ingest/syslog \
    -H 'content-type: application/json' \
    -d "{\"line\":\"${line}\"}" >/dev/null
done

echo "[5/6] Verifying /fleet"
fleet_json="$(curl -fsS http://localhost:8000/fleet)"
FLEET_JSON="$fleet_json" python - <<'PY'
import json
import os

fleet = json.loads(os.environ["FLEET_JSON"])
assert fleet["sites"] > 0, fleet
assert fleet["links"] > 0, fleet
print(f"fleet ok: {fleet}")
PY

echo "[6/6] Verifying /alerts"
alerts_json="$(curl -fsS http://localhost:8000/alerts)"
ALERTS_JSON="$alerts_json" python - <<'PY'
import json
import os

alerts = json.loads(os.environ["ALERTS_JSON"])
assert len(alerts) > 0, alerts
assert any(a["event_type"] == "new_asn" for a in alerts), alerts
print(f"alerts ok: {len(alerts)} events")
PY

echo "Smoke test passed"
