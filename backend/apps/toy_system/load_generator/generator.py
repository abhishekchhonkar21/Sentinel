"""Continuous load generator — httpx-based traffic against the toy system."""

from __future__ import annotations

import argparse
import asyncio
import random
import sys
import time
import uuid
from dataclasses import dataclass

import httpx

DEFAULT_BASE_URL = "http://localhost:8080"
CUSTOMERS = [f"cust-{i}" for i in range(1, 21)]
SKUS = [
    {"sku": "widget-001", "quantity": 1},
    {"sku": "widget-001", "quantity": 2},
    {"sku": "widget-pro", "quantity": 1},
    {"sku": "gadget-100", "quantity": 3},
]


@dataclass
class GeneratorStats:
    ok: int = 0
    failed: int = 0
    total_latency_ms: float = 0.0


def _build_order_payload() -> dict:
    item = random.choice(SKUS)
    return {
        "customer_id": random.choice(CUSTOMERS),
        "items": [item],
    }


async def _place_order(client: httpx.AsyncClient, base_url: str, stats: GeneratorStats) -> None:
    payload = _build_order_payload()
    trace_id = str(uuid.uuid4())
    started = time.perf_counter()
    try:
        response = await client.post(
            f"{base_url}/api/v1/orders",
            json=payload,
            headers={"X-Trace-Id": trace_id},
        )
        elapsed_ms = (time.perf_counter() - started) * 1000
        stats.total_latency_ms += elapsed_ms
        if response.is_success:
            stats.ok += 1
            print(
                f'{{"event":"request_ok","status":{response.status_code},'
                f'"latency_ms":{elapsed_ms:.1f},"trace_id":"{trace_id}"}}'
            )
        else:
            stats.failed += 1
            print(
                f'{{"event":"request_failed","status":{response.status_code},'
                f'"latency_ms":{elapsed_ms:.1f},"trace_id":"{trace_id}",'
                f'"body":{response.text[:200]!r}}}'
            )
    except httpx.HTTPError as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000
        stats.failed += 1
        print(
            f'{{"event":"request_error","error":{str(exc)!r},'
            f'"latency_ms":{elapsed_ms:.1f},"trace_id":"{trace_id}"}}'
        )


async def run_generator(*, base_url: str, rps: float, duration: float | None) -> GeneratorStats:
    stats = GeneratorStats()
    interval = 1.0 / rps if rps > 0 else 1.0
    deadline = time.monotonic() + duration if duration else None

    async with httpx.AsyncClient(timeout=30.0) as client:
        while deadline is None or time.monotonic() < deadline:
            loop_start = time.monotonic()
            await _place_order(client, base_url, stats)
            elapsed = time.monotonic() - loop_start
            sleep_for = max(0.0, interval - elapsed)
            await asyncio.sleep(sleep_for)

    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate continuous order traffic")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--rps", type=float, default=3.0, help="Target requests per second")
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Run for N seconds then exit (default: run until Ctrl+C)",
    )
    args = parser.parse_args(argv)

    print(
        f'{{"event":"generator_started","base_url":"{args.base_url}",'
        f'"rps":{args.rps},"duration":{args.duration}}}'
    )

    try:
        stats = asyncio.run(
            run_generator(base_url=args.base_url.rstrip("/"), rps=args.rps, duration=args.duration)
        )
    except KeyboardInterrupt:
        print('{"event":"generator_stopped","reason":"keyboard_interrupt"}')
        return 0

    total = stats.ok + stats.failed
    avg_latency = stats.total_latency_ms / total if total else 0.0
    print(
        f'{{"event":"generator_finished","ok":{stats.ok},"failed":{stats.failed},'
        f'"avg_latency_ms":{avg_latency:.1f}}}'
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
