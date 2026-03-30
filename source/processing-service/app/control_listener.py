import json
import os
import signal
import threading
import time

import requests
from sseclient import SSEClient

from app.config import REPLICA_ID


SIMULATOR_CONTROL_URL = os.getenv(
    "SIMULATOR_CONTROL_URL",
    "http://simulator:8080/api/control"
)


def terminate_process() -> None:
    pid = os.getpid()
    os.kill(pid, signal.SIGTERM)


def listen_for_shutdown_commands() -> None:
    while True:
        try:
            print(
                f"[{REPLICA_ID}] Connecting to control stream: {SIMULATOR_CONTROL_URL}",
                flush=True
            )
            response = requests.get(SIMULATOR_CONTROL_URL, stream=True, timeout=60)
            response.raise_for_status()

            client = SSEClient(response)

            for event in client.events():
                event_type = getattr(event, "event", None)
                data = getattr(event, "data", "")

                if not data or event_type != "command":
                    continue

                try:
                    payload = json.loads(data)
                except json.JSONDecodeError:
                    print(f"[{REPLICA_ID}] Invalid command payload received.", flush=True)
                    continue

                if payload.get("command") == "SHUTDOWN":
                    print(
                        f"[{REPLICA_ID}] Shutdown command received. Terminating replica.",
                        flush=True
                    )
                    terminate_process()
                    return

        except Exception as exc:
            print(
                f"[{REPLICA_ID}] Control stream error: {exc}. Reconnecting in 3 seconds.",
                flush=True
            )
            time.sleep(3)


def start_control_listener() -> None:
    listener_thread = threading.Thread(
        target=listen_for_shutdown_commands,
        daemon=True
    )
    listener_thread.start()