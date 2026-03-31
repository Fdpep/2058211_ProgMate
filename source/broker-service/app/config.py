import os


SIMULATOR_BASE_URL = os.getenv("SIMULATOR_BASE_URL", "http://simulator:8080")
DEVICES_ENDPOINT = f"{SIMULATOR_BASE_URL}/api/devices/"

PROCESSING_REPLICAS = [
    os.getenv("PROCESSING_REPLICA_1", "http://processing-1:8100"),
    os.getenv("PROCESSING_REPLICA_2", "http://processing-2:8100"),
    os.getenv("PROCESSING_REPLICA_3", "http://processing-3:8100"),
]

BROKER_REQUEST_TIMEOUT_SECONDS = float(
    os.getenv("BROKER_REQUEST_TIMEOUT_SECONDS", "0.3")
)

BROKER_PARTIAL_FAILURE_LOG_INTERVAL_SECONDS = int(
    os.getenv("BROKER_PARTIAL_FAILURE_LOG_INTERVAL_SECONDS", "15")
)