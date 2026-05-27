# AirWatch API

FastAPI + Celery backend. See [the root README](../../README.md) for the
overall project description and [`docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md)
for the data flow.

## Local dev

```bash
# From repo root:
make up           # postgres + redis + api + worker + beat in Docker
make migrate      # apply alembic migrations
make seed         # insert seed locations
make ingest       # trigger the first ingest run
```

Or run the API outside Docker against a Postgres + Redis you already have:

```bash
cp ../../.env.example ../../.env  # then fill in DATABASE_URL / REDIS_URL
make api          # uvicorn with --reload on :8000
make worker       # in another terminal
make beat         # in another terminal
```

## API surface

| Method | Path                                       | Purpose                                  |
| ------ | ------------------------------------------ | ---------------------------------------- |
| GET    | `/healthz`                                 | Liveness                                 |
| GET    | `/readyz`                                  | Readiness (pings the DB)                 |
| GET    | `/locations`                               | List monitored locations                 |
| GET    | `/locations/{id}`                          | Single location                          |
| GET    | `/dashboard/location/{id}?hours=&bad_threshold=` | PM2.5 + weather + metrics + correlation |
| GET    | `/summary/bad-days?days=`                  | Leaderboard of bad-air days              |
| GET    | `/summary/bad-days-trend?location_id=&days=` | 90-day bad-day trend for one location  |
| GET    | `/subscriptions?email=`                    | List subscriptions for an email          |
| POST   | `/subscriptions`                           | Upsert a subscription                    |
| POST   | `/admin/ingest/air?hours=`                 | Manually trigger air ingestion           |
| POST   | `/admin/ingest/weather?hours=`             | Manually trigger weather ingestion       |
| POST   | `/admin/aggregate/daily?days=&threshold=`  | Rebuild daily metrics                    |
| POST   | `/admin/alerts/send?threshold=`            | Enqueue the alert task                   |

Interactive docs: `http://localhost:8000/docs` (Swagger UI).

## Testing

```bash
make test         # 27 tests, ~1s
make lint         # ruff
make check        # everything
```

Tests are split into:

- `tests/test_insights_service.py` — pure-function unit tests for analytics
- `tests/test_normalizers.py` — Open-Meteo payload normalization
- `tests/test_api_integration.py` — FastAPI TestClient against SQLite
- `tests/test_health.py` — health endpoints

## Load testing

```bash
make loadtest                   # 50 concurrent, 1000 reqs total
make loadtest C=100 N=50        # 100 concurrent, 5000 reqs total
```

Source: [`scripts/loadtest.py`](./scripts/loadtest.py).
Numbers: [`docs/LOAD_TEST_RESULTS.md`](../../docs/LOAD_TEST_RESULTS.md).
