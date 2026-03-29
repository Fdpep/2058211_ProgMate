import requests

from app.config import PROCESSING_REPLICAS


def distribute_measurement(measurement: dict) -> dict:
    results = {}

    for replica_base_url in PROCESSING_REPLICAS:
        target_url = f"{replica_base_url}/measurements"

        try:
            response = requests.post(target_url, json=measurement, timeout=5)
            results[replica_base_url] = {
                "reachable": True,
                "status_code": response.status_code
            }
        except requests.RequestException:
            results[replica_base_url] = {
                "reachable": False,
                "status_code": None
            }

    return results