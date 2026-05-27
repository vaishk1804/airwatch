# Load test results

Single-process uvicorn (no `--workers`), SQLite backend, MacBook-class hardware.
The numbers below are reproducible — run `make loadtest` against a seeded local
instance and you'll get within ~10% of these.

## Baseline (50 concurrent clients, 1000 requests)

```
Concurrency:       50
Requests/client:   20
Total requests:    1000
Wall time:         5.04s
Throughput:        198 req/s

Latency (ms):
  p50 = 124
  p95 = 418
  p99 = 1167

Error rate:        0.00%
Status codes:      200: 1000
```

## Sustained load (100 concurrent clients, 5000 requests)

```
Concurrency:       100
Requests/client:   50
Total requests:    5000
Wall time:         21.72s
Throughput:        230 req/s

Latency (ms):
  p50 = 255
  p95 = 736
  p99 = 1603

Error rate:        0.00%
Status codes:      200: 5000
```

## Endpoint mix

The script weights requests to mirror a realistic dashboard session:

| Endpoint                      | Share |
| ----------------------------- | ----- |
| `GET /dashboard/location/{id}`| 60%   |
| `GET /locations`              | 20%   |
| `GET /summary/bad-days`       | 10%   |
| `GET /healthz`                | 10%   |

## Notes on the architecture decision this measured

The first version of `/dashboard/location/{id}` made a synchronous outbound
call to Open-Meteo on every request. Under 50 concurrent clients that
produced **63 RPS, p50 575 ms, and a 74% error rate** because Open-Meteo
rate-limited and the 403 propagated as a 500. The current version reads
weather from `weather_hourly`, populated by the Celery beat job every hour.
The cold-start path falls back to a one-shot live fetch.

This is the kind of thing the load test was added to catch — not raw
benchmarking, but enforcing the property "dashboard reads never depend on
a third-party API being reachable."
