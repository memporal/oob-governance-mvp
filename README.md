# OOB Governance MVP (Air-Gapped AI Edition)

This repo runs an offline governance stack with:
- FastAPI governance engine (`app`)
- Postgres state store (`db`)
- Local RF classifier service (`sdr-ai`)
- Local LLM triage service (`local-llm`)

No internet dependency is required at runtime after images/models are loaded.

## Hardware profile
- CPU: 8+ cores recommended
- RAM: 16GB-32GB recommended
- GPU: Optional but recommended (Jetson/T4/A2 class) for `sdr-ai` and local LLM inference

## Start
```bash
docker compose up --build
```

## Seed
```bash
docker compose exec app python scripts/seed.py
```

## Smoke test
```bash
./scripts/smoke_test.sh
```

## API quick checks
Health:
```bash
curl -s http://localhost:8000/health
```

Ingest syslog (with optional I/Q samples for RF-ML spoof detection):
```bash
curl -s -X POST http://localhost:8000/ingest/syslog \
  -H 'content-type: application/json' \
  -d '{"line":"<134>1 2026-01-01T00:00:00Z edge-router bgp - - - site=site-a link=wan1 asn=65001","iq_samples":[0.1,0.5,-0.2,0.9,0.4]}'
```

Fleet:
```bash
curl -s http://localhost:8000/fleet
```

Alerts:
```bash
curl -s http://localhost:8000/alerts
```

LLM triage:
```bash
curl -s -X POST http://localhost:8000/triage \
  -H 'content-type: application/json' \
  -d '{"question":"Why is Site A high risk?"}'
```

## AI components
1. **Local Signal Intelligence (RF-ML)**
   - `sdr-ai` runs a lightweight classifier over raw I/Q samples.
   - Returns `authentic` vs `clone_suspected` with confidence score.

2. **Behavioral Anomaly Detection (Time-Series AI)**
   - `app.state_engine` trains an IsolationForest from local historical telemetry.
   - Generates `behavioral_anomaly` drift events when outliers occur.

3. **Semantic Search & Triage (Local LLM)**
   - `/triage` assembles recent drift/syslog context and queries local Ollama.
   - Keeps data local; no external APIs.

## Migrations
```bash
docker compose exec app alembic upgrade head
```

The app container runs this automatically at startup.

## Tests
```bash
pytest -q
```
