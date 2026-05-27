"""
loadtest.py — concurrent load test for the AirWatch API.

Fires N concurrent clients, each looping M requests against a mix of
read endpoints. Reports p50 / p95 / p99 latency, RPS, and error rate.

Usage:
    python apps/api/scripts/loadtest.py \\
        --base-url http://localhost:8000 \\
        --concurrency 50 \\
        --requests-per-client 40

Why httpx + asyncio (not locust): zero extra deps beyond what the API
already pins in requirements.txt, and runs in one shot from CI.
"""
from __future__ import annotations

import argparse
import asyncio
import random
import statistics
import time
from dataclasses import dataclass, field

import httpx


@dataclass
class Results:
    latencies_ms: list[float] = field(default_factory=list)
    errors: int = 0
    by_status: dict[int, int] = field(default_factory=dict)

    def record(self, status: int, latency_ms: float):
        self.latencies_ms.append(latency_ms)
        self.by_status[status] = self.by_status.get(status, 0) + 1
        if status >= 500 or status == 0:
            self.errors += 1


async def one_client(
    client_id: int,
    base_url: str,
    requests_per_client: int,
    location_ids: list[int],
    results: Results,
):
    """A single virtual user looping through a realistic mix of read endpoints."""
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        for _ in range(requests_per_client):
            # Weighted endpoint mix mirroring a realistic dashboard session:
            #   60% dashboard reads, 20% locations list, 10% summary, 10% health
            roll = random.random()
            if roll < 0.6 and location_ids:
                loc = random.choice(location_ids)
                hours = random.choice([24, 48, 168])
                path = f"/dashboard/location/{loc}?hours={hours}&bad_threshold=35"
            elif roll < 0.8:
                path = "/locations"
            elif roll < 0.9:
                path = "/summary/bad-days?days=30"
            else:
                path = "/healthz"

            t0 = time.perf_counter()
            try:
                r = await client.get(path)
                status = r.status_code
            except httpx.HTTPError:
                status = 0
            elapsed_ms = (time.perf_counter() - t0) * 1000
            results.record(status, elapsed_ms)


async def run(args):
    # Pull real location IDs so dashboard requests hit valid routes
    async with httpx.AsyncClient(base_url=args.base_url, timeout=10) as client:
        try:
            r = await client.get("/locations")
            location_ids = [row["id"] for row in r.json()] if r.status_code == 200 else []
        except Exception:
            location_ids = []
    if not location_ids:
        print("[warn] No locations returned; dashboard requests will skip.")
        location_ids = [1]

    results = Results()
    t_start = time.perf_counter()

    await asyncio.gather(
        *[
            one_client(i, args.base_url, args.requests_per_client, location_ids, results)
            for i in range(args.concurrency)
        ]
    )

    wall_seconds = time.perf_counter() - t_start
    total = len(results.latencies_ms)

    if total == 0:
        print("No requests completed.")
        return

    latencies = sorted(results.latencies_ms)
    p50 = latencies[int(0.50 * (total - 1))]
    p95 = latencies[int(0.95 * (total - 1))]
    p99 = latencies[int(0.99 * (total - 1))]

    print("=" * 60)
    print("AirWatch API load test")
    print("=" * 60)
    print(f"  Base URL:          {args.base_url}")
    print(f"  Concurrency:       {args.concurrency}")
    print(f"  Requests/client:   {args.requests_per_client}")
    print(f"  Total requests:    {total}")
    print(f"  Wall time:         {wall_seconds:.2f}s")
    print(f"  Throughput:        {total / wall_seconds:.1f} req/s")
    print()
    print("  Latency (ms):")
    print(f"    p50 = {p50:.1f}")
    print(f"    p95 = {p95:.1f}")
    print(f"    p99 = {p99:.1f}")
    print(f"    avg = {statistics.mean(latencies):.1f}")
    print(f"    max = {max(latencies):.1f}")
    print()
    print(f"  Error rate:        {results.errors / total * 100:.2f}% ({results.errors}/{total})")
    print("  Status codes:")
    for status, count in sorted(results.by_status.items()):
        marker = " " if 200 <= status < 400 else "!"
        print(f"   {marker} {status or 'network-error'}: {count}")

    # Non-zero exit on any 5xx so CI can fail noisily
    if results.errors > 0:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description="Async load test for AirWatch API.")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--concurrency", type=int, default=50)
    parser.add_argument("--requests-per-client", type=int, default=40)
    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
