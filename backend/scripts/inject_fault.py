#!/usr/bin/env python3
"""Inject a catalogued fault and print the exact injection timestamp.

Usage:
    python backend/scripts/inject_fault.py --fault-id payments-null-deref
    python backend/scripts/inject_fault.py --fault-id payment-provider-timeout \\
        --params '{"latency_delay_ms": 5000}'
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FAULT_INJECTION_URL = "http://localhost:8090"


def main() -> int:
    parser = argparse.ArgumentParser(description="Inject a fault via the fault-injection API")
    parser.add_argument("--fault-id", required=True, help="fault_id from fault_catalogue")
    parser.add_argument("--params", default="{}", help="JSON object of injector overrides")
    parser.add_argument("--base-url", default=DEFAULT_FAULT_INJECTION_URL)
    args = parser.parse_args()

    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid --params JSON: {exc}", file=sys.stderr)
        return 1

    if not isinstance(params, dict):
        print("ERROR: --params must be a JSON object", file=sys.stderr)
        return 1

    payload = {"fault_id": args.fault_id, "params": params}
    url = f"{args.base_url.rstrip('/')}/api/v1/inject-fault"

    try:
        response = httpx.post(url, json=payload, timeout=30.0)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        print(f"ERROR: fault injection failed: {exc}", file=sys.stderr)
        if isinstance(exc, httpx.HTTPStatusError) and exc.response is not None:
            print(exc.response.text, file=sys.stderr)
        return 1

    body = response.json()
    print(f"fault_id:          {body['fault_id']}")
    print(f"injected_service:  {body['injected_service']}")
    print(f"injected_at:       {body['injected_at']}")
    print(f"status:            {body['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
