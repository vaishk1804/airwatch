# AirWatch architecture

## At a glance

AirWatch is a small monorepo with three runtime processes (API, worker, beat),
a Postgres database, and a Redis broker. The data flow is **ingest → aggregate
→ serve → alert**:

1. **Beat** schedules ingest jobs every hour
2. **Worker** runs the jobs: it fetches hourly PM2.5 from OpenAQ (with Open-Meteo
   air-quality as a fallback) and hourly weather from Open-Meteo, then upserts
   into Postgres
3. Once a day, **worker** aggregates the hourly readings into `daily_metrics`
   (avg / max / bad_hours / bad_day) and runs the alert job, which emails any
   subscription whose location had a "bad day"
4. **API** serves the React dashboard out of the DB — no third-party calls in
   the request path (see [LOAD_TEST_RESULTS.md](./LOAD_TEST_RESULTS.md) for why)

## Component diagram

```mermaid
flowchart LR
    User[Browser] -->|HTTP| Web[React + Vite]
    Web -->|REST| API[FastAPI]

    subgraph Backend[Python backend]
        API
        Beat[Celery beat<br/>scheduler]
        Worker[Celery worker]
    end

    API <-->|SQLAlchemy| PG[(PostgreSQL)]
    Worker <-->|SQLAlchemy| PG
    Beat -->|enqueue| Redis[(Redis)]
    Redis -->|consume| Worker

    Worker -->|hourly| OpenAQ[OpenAQ v3 API]
    Worker -->|hourly| Meteo[Open-Meteo API]
    Worker -->|daily digest| SMTP[SMTP server]
```

## Data model

```mermaid
erDiagram
    locations ||--o{ aq_measurements   : "many readings"
    locations ||--o{ weather_hourly    : "many readings"
    locations ||--o{ daily_metrics     : "rolled up daily"
    locations ||--o{ subscriptions     : "alerts per location"

    locations {
        int id PK
        string name UK
        string state
        string country
        float lat
        float lon
    }
    aq_measurements {
        int id PK
        int location_id FK
        datetime timestamp_utc
        string parameter
        float value
        string unit
        string source
    }
    weather_hourly {
        int id PK
        int location_id FK
        datetime timestamp_utc
        float temp_c
        float rh
        float wind_kmh
    }
    daily_metrics {
        int id PK
        int location_id FK
        date day
        float pm25_avg
        float pm25_max
        int bad_hours
        int bad_day
        float threshold
    }
    subscriptions {
        int id PK
        string email
        int location_id FK
        float threshold
        int is_active
    }
```

Indexes that matter for hot paths:

| Table              | Index                                                  | Hot read                                       |
| ------------------ | ------------------------------------------------------ | ---------------------------------------------- |
| `aq_measurements`  | `(location_id, timestamp_utc)`                         | Dashboard PM2.5 time series                    |
| `aq_measurements`  | `unique (location_id, timestamp_utc, parameter, source)` | Idempotent upsert (`ON CONFLICT DO NOTHING`) |
| `weather_hourly`   | `(location_id, timestamp_utc)`                         | Dashboard weather time series                  |
| `daily_metrics`    | `(location_id, day)`                                   | Summary leaderboard + trend                    |
| `subscriptions`    | `unique (email, location_id)`                          | Idempotent subscription upsert                 |

## Job schedule

| Task                       | Cadence  | What it does                                                                                  |
| -------------------------- | -------- | --------------------------------------------------------------------------------------------- |
| `ingest_air_task`          | hourly   | Pull hourly PM2.5 for every location. OpenAQ first; Open-Meteo air-quality if OpenAQ has nothing in radius. |
| `ingest_weather_task`      | hourly   | Pull hourly temp/RH/wind from Open-Meteo                                                      |
| `aggregate_daily_task`     | every 6h | Group hourlies by day, compute `pm25_avg`, `pm25_max`, `bad_hours`, `bad_day`                 |
| `send_alerts_task`         | daily    | Email any subscription whose location had a `bad_day` yesterday                               |

All four are wired in `app/worker.py:beat_schedule`. The worker has automatic
exponential backoff (`autoretry_for=(Exception,)`, `retry_backoff=True`,
`max_retries=3`) for the two ingest tasks since upstream APIs are flaky.

## Request flow: `GET /dashboard/location/{id}`

```mermaid
sequenceDiagram
    participant U as Browser
    participant API as FastAPI
    participant DB as Postgres

    U->>API: GET /dashboard/location/1?hours=24
    API->>DB: SELECT location WHERE id=1
    DB-->>API: row
    API->>DB: SELECT pm25 series (last 24h)
    DB-->>API: rows
    API->>DB: SELECT weather series (last 24h)
    DB-->>API: rows
    Note over API: summarize_pm25 + align_series_by_time<br/>+ correlation_insights (pure Python)
    API-->>U: { location, pm25, weather, metrics, aligned, correlation }
```

Note: no outbound HTTP from the API in the steady state. Cold-start (empty
`weather_hourly`) is the one path where the API calls Open-Meteo, and only
for weather, never blocking the PM2.5 chart.

## Deployment shape

`render.yaml` declares three services off the same Docker image (`apps/api/Dockerfile`):

- `airwatch-api` — uvicorn, runs `python app/scripts/migrate.py && uvicorn app.main:app`
- `airwatch-worker` — `celery -A app.worker.celery_app worker`
- `airwatch-beat` — `celery -A app.worker.celery_app beat`

Locally, `infra/docker-compose.yml` runs all three plus Postgres and Redis.
The frontend deploys separately as a Vite static build.
