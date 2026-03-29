# File simulazione

import math
from datetime import datetime, timedelta, timezone

import requests


url = "http://localhost:8101/measurements"

start_time = datetime.now(timezone.utc)

sampling_rate_hz = 20.0
frequency_hz = 2.0
num_samples = 100

for i in range(num_samples):
    timestamp = start_time + timedelta(seconds=i / sampling_rate_hz)
    value = math.sin(2 * math.pi * frequency_hz * (i / sampling_rate_hz))

    payload = {
        "sensor_id": "sensor-01",
        "sensor_name": "Borealis Ridge",
        "sensor_region": "North Atlantic",
        "timestamp": timestamp.isoformat(),
        "value": value,
    }

    response = requests.post(url, json=payload, timeout=10)
    print(i + 1, response.json())