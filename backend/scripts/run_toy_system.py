#!/usr/bin/env python3
"""Start all toy-system microservices locally (no Docker required).

Usage:
    python backend/scripts/run_toy_system.py          # start all services
    python backend/scripts/run_toy_system.py --check  # health-check only (services already running)

Prerequisites:
    - Python 3.11+ with dependencies installed (pip install -r backend/requirements-dev.txt)
    - MongoDB running locally on mongodb://localhost:27017 (brew services start mongodb-community)
"""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]

# PYTHONPATH entries so all toy_system packages resolve.
PYTHONPATH = os.pathsep.join(
    [
        str(ROOT / "libs" / "sentinel_core" / "src"),
        str(ROOT / "apps" / "toy_system" / "common" / "src"),
        str(ROOT / "apps" / "toy_system" / "external_payment_mock" / "src"),
        str(ROOT / "apps" / "toy_system" / "inventory_service" / "src"),
        str(ROOT / "apps" / "toy_system" / "payments_service" / "src"),
        str(ROOT / "apps" / "toy_system" / "orders_service" / "src"),
        str(ROOT / "apps" / "toy_system" / "api_gateway" / "src"),
    ]
)

# Services started in dependency order (leaf nodes first).
SERVICES: list[tuple[str, str, int]] = [
    ("external-payment-mock", "toy_system.external_payment_mock.main:app", 8084),
    ("inventory-service", "toy_system.inventory_service.main:app", 8083),
    ("payments-service", "toy_system.payments_service.main:app", 8082),
    ("orders-service", "toy_system.orders_service.main:app", 8081),
    ("api-gateway", "toy_system.api_gateway.main:app", 8080),
]

HEALTH_URLS = [f"http://localhost:{port}/api/v1/health" for _, _, port in SERVICES]


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = PYTHONPATH
    env.setdefault("MONGODB_URI", "mongodb://localhost:27017/sentinel")
    return env


def start_services() -> list[subprocess.Popen]:
    """Spawn one uvicorn process per service; return handles for cleanup."""
    procs: list[subprocess.Popen] = []
    env = _env()

    for name, module, port in SERVICES:
        print(f"  starting {name} on :{port}")
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", module, "--host", "127.0.0.1", "--port", str(port)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        procs.append(proc)
        time.sleep(0.8)  # stagger startup so downstream deps are ready

    return procs


def wait_for_healthy(timeout: float = 30.0) -> bool:
    """Poll health endpoints until all services respond 200."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        all_ok = True
        for url in HEALTH_URLS:
            try:
                resp = httpx.get(url, timeout=2.0)
                if resp.status_code != 200:
                    all_ok = False
            except httpx.HTTPError:
                all_ok = False
        if all_ok:
            return True
        time.sleep(1.0)
    return False


def smoke_test_order() -> None:
    """Week 1 exit criterion: place an order through api-gateway."""
    payload = {
        "customer_id": "cust-smoke-test",
        "items": [{"sku": "widget-001", "quantity": 1}],
    }
    resp = httpx.post("http://localhost:8080/api/v1/orders", json=payload, timeout=10.0)
    resp.raise_for_status()
    body = resp.json()
    print(f"  order_id:  {body['order_id']}")
    print(f"  status:    {body['status']}")
    print(f"  total:     ${body['total_cents'] / 100:.2f}")
    assert body["status"] == "confirmed", f"Expected confirmed, got {body['status']}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run toy-system locally")
    parser.add_argument("--check", action="store_true", help="Health-check + smoke test only")
    args = parser.parse_args()

    procs: list[subprocess.Popen] = []

    def shutdown(*_args: object) -> None:
        print("\nShutting down services...")
        for p in procs:
            p.terminate()
        for p in procs:
            p.wait(timeout=5)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    if not args.check:
        print("Starting toy-system services...")
        procs = start_services()

    print("Waiting for health checks...")
    if not wait_for_healthy():
        print("ERROR: Services did not become healthy in time.")
        print("Make sure MongoDB is running: mongodb://localhost:27017")
        shutdown()
        return 1

    print("All services healthy.")
    print("Running smoke test (POST /api/v1/orders)...")
    try:
        smoke_test_order()
        print("Smoke test PASSED.")
    except Exception as exc:
        print(f"Smoke test FAILED: {exc}")
        shutdown()
        return 1

    if args.check:
        return 0

    print("\nServices running. Press Ctrl+C to stop.")
    print("  curl http://localhost:8080/api/v1/health")
    print('  curl -X POST http://localhost:8080/api/v1/orders -H "Content-Type: application/json" \\')
    print('    -d \'{"customer_id":"cust-1","items":[{"sku":"widget-001","quantity":2}]}\'')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
