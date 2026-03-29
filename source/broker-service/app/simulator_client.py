import requests

from app.config import DEVICES_ENDPOINT


def fetch_devices() -> list[dict]:
    response = requests.get(DEVICES_ENDPOINT, timeout=15)
    response.raise_for_status()
    return response.json()