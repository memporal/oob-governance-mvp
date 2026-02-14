# OOB Governance MVP

Minimal FastAPI + Postgres service that ingests syslog-style lines, stores observations, and raises drift alerts for newly observed ASNs.

## Requirements
- Docker + Docker Compose
- (Optional local dev) Python 3.11+

## Start the stack
```bash
docker compose up --build
```

App endpoints:
- API: `http://localhost:8000`
- Postgres: `localhost:5432` (`oob/oob`, db `oob`)

## Seed baseline data
In another shell after startup:
```bash
docker compose exec app python scripts/seed.py
```

## Run smoke test (end-to-end)
This command starts compose, seeds, ingests 20 messages, validates fleet and drift alerts, then tears down:
```bash
./scripts/smoke_test.sh
```

## Example API calls
Health:
```bash
curl -s http://localhost:8000/health
```

Ingest one syslog line:
```bash
curl -s -X POST http://localhost:8000/ingest/syslog \
  -H 'content-type: application/json' \
  -d '{"line":"<134>1 2026-01-01T00:00:00Z edge-router bgp - - - site=site-a link=wan1 asn=65001"}'
```

Fleet summary:
```bash
curl -s http://localhost:8000/fleet
```

Alerts:
```bash
curl -s http://localhost:8000/alerts
```

## Migrations
Alembic is used with one initial migration.

Apply migrations manually:
```bash
docker compose exec app alembic upgrade head
```

The container start command already runs `alembic upgrade head` before launching Uvicorn.

## Tests
```bash
pytest -q
```

## Scheduler safety
- APScheduler starts only when `ENABLE_SCHEDULER=true`.
- Scheduler startup is guarded by a Postgres advisory lock (`pg_try_advisory_lock`) so only one process runs it, preventing duplicate runs under reload/multi-worker scenarios.
