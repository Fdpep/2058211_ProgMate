import threading
import time

import requests

from app.config import (
    PROCESSING_REPLICAS,
    BROKER_REQUEST_TIMEOUT_SECONDS,
    BROKER_PARTIAL_FAILURE_LOG_INTERVAL_SECONDS,
    BROKER_REPLICA_RETRY_AFTER_SECONDS,
)

import random


_replica_status_memory = {}
_replica_retry_not_before = {}
_last_partial_failure_log_ts = 0.0
_lock = threading.Lock()

_session = requests.Session()


def _can_try_replica(replica_url: str) -> bool:
    now = time.time()
    retry_not_before = _replica_retry_not_before.get(replica_url, 0.0)
    return now >= retry_not_before


def _mark_replica_failure(replica_url: str) -> None:
    _replica_retry_not_before[replica_url] = (
        time.time() + BROKER_REPLICA_RETRY_AFTER_SECONDS
    )


def _mark_replica_success(replica_url: str) -> None:
    _replica_retry_not_before[replica_url] = 0.0


def _send_to_replica(replica_url: str, measurement: dict) -> dict:
    if not _can_try_replica(replica_url):
        return {
            "reachable": False,
            "status_code": None,
            "skipped_temporarily": True,
        }

    try:
        response = _session.post(
            f"{replica_url}/measurements",
            json=measurement,
            timeout=BROKER_REQUEST_TIMEOUT_SECONDS,
        )

        if response.status_code == 200:
            _mark_replica_success(replica_url)
            return {
                "reachable": True,
                "status_code": 200,
                "skipped_temporarily": False,
            }

        _mark_replica_failure(replica_url)
        return {
            "reachable": False,
            "status_code": response.status_code,
            "skipped_temporarily": False,
        }

    except requests.RequestException:
        _mark_replica_failure(replica_url)
        return {
            "reachable": False,
            "status_code": None,
            "skipped_temporarily": False,
        }


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

    replicas = PROCESSING_REPLICAS.copy()
    random.shuffle(replicas)

    for replica_url in replicas:
        distribution_result[replica_url] = _send_to_replica(replica_url, measurement)

    _log_replica_state_changes(distribution_result)
    _log_periodic_partial_failure_summary(distribution_result)

    return distribution_result