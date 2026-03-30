import threading
import time

import requests

from app.config import (
    PROCESSING_REPLICAS,
    BROKER_REQUEST_TIMEOUT_SECONDS,
    BROKER_PARTIAL_FAILURE_LOG_INTERVAL_SECONDS,
)


_replica_status_memory = {}
_last_partial_failure_log_ts = 0.0
_lock = threading.Lock()


def _log_replica_state_changes(distribution_result: dict) -> None:
    global _replica_status_memory

    with _lock:
        for replica_url, result in distribution_result.items():
            current_reachable = result["reachable"]
            previous_reachable = _replica_status_memory.get(replica_url)

            if previous_reachable is None:
                _replica_status_memory[replica_url] = current_reachable
                if current_reachable:
                    print(f"[broker] Replica available: {replica_url}", flush=True)
                else:
                    print(f"[broker] Replica unavailable: {replica_url}", flush=True)
                continue

            if previous_reachable != current_reachable:
                _replica_status_memory[replica_url] = current_reachable
                if current_reachable:
                    print(f"[broker] Replica recovered: {replica_url}", flush=True)
                else:
                    print(f"[broker] Replica unavailable: {replica_url}", flush=True)


def _log_periodic_partial_failure_summary(distribution_result: dict) -> None:
    global _last_partial_failure_log_ts

    unreachable_replicas = [
        replica_url
        for replica_url, result in distribution_result.items()
        if not result["reachable"]
    ]

    if not unreachable_replicas:
        return

    now = time.time()

    with _lock:
        if (
            now - _last_partial_failure_log_ts
            < BROKER_PARTIAL_FAILURE_LOG_INTERVAL_SECONDS
        ):
            return

        _last_partial_failure_log_ts = now
        print(
            f"[broker] Partial distribution active. Currently unreachable replicas: "
            f"{unreachable_replicas}",
            flush=True
        )


def distribute_measurement(measurement: dict) -> dict:
    distribution_result = {}

    for replica_url in PROCESSING_REPLICAS:
        try:
            response = requests.post(
                f"{replica_url}/measurements",
                json=measurement,
                timeout=BROKER_REQUEST_TIMEOUT_SECONDS,
            )
            distribution_result[replica_url] = {
                "reachable": response.status_code == 200,
                "status_code": response.status_code,
            }
        except requests.RequestException:
            distribution_result[replica_url] = {
                "reachable": False,
                "status_code": None,
            }

    _log_replica_state_changes(distribution_result)
    _log_periodic_partial_failure_summary(distribution_result)

    return distribution_result