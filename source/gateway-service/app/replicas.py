import requests

PROCESSING_REPLICAS = [
    "http://processing-1:8100",
    "http://processing-2:8100",
    "http://processing-3:8100",
]


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