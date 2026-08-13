# FutureFix — Gear Line 3 Dashboard

## Run
docker compose up -d
python3 -m venv venv && source venv/bin/activate
pip install fastapi uvicorn psycopg2-binary pytest
python scripts/load.py
uvicorn backend.main:app --reload --port 8000
cd frontend && python3 -m http.server 5500

Open http://localhost:5500/index.html

## Stack
- **PostgreSQL** (required) via Docker Compose — schema auto-loads from `database/init/*.sql`.
- **FastAPI + raw SQL**, no ORM — keeps the schema and queries directly visible.
- **Plain HTML + Chart.js**, no build step — fastest to ship in the time available.

## Schema
9 tables (`machines`, `part_master`, `downtime_reasons`, `reject_reasons`, `shifts`,
`machine_states`, `production_events`, `telemetry`, `app_config`), linked by foreign keys.
`telemetry` uses a composite primary key `(machine_id, ts)` to reject duplicate rows.

## Dirty data
- Sentinel value `-999` in `spindle_current_a` → converted to `NULL` at load time.
- Duplicate telemetry rows → rejected by the primary key.
- Malformed rows → quarantined and counted, never silently dropped.
- Loader is idempotent — re-running it produces identical row counts.

## OEE assumptions
Unmanned shift excluded from planned time; planned breaks excluded; setup/changeover and
short stops both count as Availability loss; Performance counts all parts produced (good +
rework + scrap); rework counts as not-good for Quality. Full reasoning in `findings.md`.

## Configurability
`app_config` table drives machine order, OEE thresholds, and default time window via
`GET/PUT /api/config` — no hardcoded values in the frontend, no restart needed to change.

## Tests
`pytest tests/` — checks OEE values are valid and reconciles one shift's Availability
against a hand-computed value from the raw tables.

## AI tooling
Used Claude for architecture guidance and code scaffolding. Reviewed and understood
throughout; can explain any line.