import requests

from app.config import PROCESSING_REPLICAS


def check_replicas_health(timeout: float = 1.0):
    results = {}

    for replica in PROCESSING_REPLICAS:
        try:
            response = requests.get(f"{replica}/health", timeout=timeout)
            if response.status_code == 200:
                results[replica] = "UP"
            else:
                results[replica] = "DOWN"
        except Exception:
            results[replica] = "DOWN"

    return results


def compute_system_status(health_map: dict):
    total = len(health_map)
    up = sum(1 for status in health_map.values() if status == "UP")

    if up == total:
        return "OK"
    elif up == 0:
        return "DOWN"
    else:
        return "DEGRADED"


def get_first_available_replica(timeout: float = 1.0):
    for replica in PROCESSING_REPLICAS:
        try:
            response = requests.get(f"{replica}/health", timeout=timeout)
            if response.status_code == 200:
                return replica
        except Exception:
            continue
    return None


def fetch_runtime_info_from_available_replica(timeout: float = 1.0):
    for replica in PROCESSING_REPLICAS:
        try:
            health_response = requests.get(f"{replica}/health", timeout=timeout)
            if health_response.status_code != 200:
                continue

            runtime_response = requests.get(f"{replica}/runtime-info", timeout=timeout)
            if runtime_response.status_code == 200:
                payload = runtime_response.json()
                payload["served_by"] = replica
                return payload
        except Exception:
            continue

    return None