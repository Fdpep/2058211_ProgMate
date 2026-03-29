import asyncio
import json
from contextlib import asynccontextmanager

import websockets
from fastapi import FastAPI

from app.config import PROCESSING_REPLICAS
from app.distributor import distribute_measurement
from app.schemas import HealthResponse
from app.simulator_client import fetch_devices


connected_sensors = []


async def consume_sensor_stream(sensor: dict) -> None:
    sensor_id = sensor["id"]
    sensor_name = sensor["name"]
    sensor_region = sensor["region"]

    websocket_url = f"ws://simulator:8080/api/device/{sensor_id}/ws"

    message_counter = 0  # 👈 per ridurre spam log

    while True:
        try:
            print(f"[broker] Connecting to sensor stream: {sensor_id} -> {websocket_url}", flush=True)

            async with websockets.connect(websocket_url) as websocket:
                print(f"[broker] Connected to sensor stream: {sensor_id}", flush=True)

                while True:
                    raw_message = await websocket.recv()
                    payload = json.loads(raw_message)

                    measurement = {
                        "sensor_id": sensor_id,
                        "sensor_name": sensor_name,
                        "sensor_region": sensor_region,
                        "timestamp": payload["timestamp"],
                        "value": payload["value"],
                    }

                    message_counter += 1

                    # 👇 stampa solo ogni 50 messaggi (evita spam)
                    if message_counter % 50 == 0:
                        print(
                            f"[broker] Received {message_counter} messages from {sensor_id}",
                            flush=True
                        )

                    distribution_result = await asyncio.to_thread(
                        distribute_measurement, measurement
                    )

                    # 👇 stampa solo se c'è un problema
                    if any(not r["reachable"] for r in distribution_result.values()):
                        print(
                            f"[broker] Partial distribution failure for {sensor_id}: {distribution_result}",
                            flush=True
                        )

        except Exception as exc:
            print(
                f"[broker] Sensor stream error for {sensor_id}: {exc}. Reconnecting in 3 seconds.",
                flush=True
            )
            await asyncio.sleep(3)


async def start_sensor_consumers() -> None:
    global connected_sensors

    try:
        print("[broker] Fetching devices from simulator...", flush=True)
        devices = fetch_devices()
        connected_sensors = devices

        print(f"[broker] Retrieved {len(devices)} devices from simulator.", flush=True)

        if not devices:
            print("[broker] No devices found. No sensor consumer started.", flush=True)
            return

        tasks = [
            asyncio.create_task(consume_sensor_stream(sensor))
            for sensor in devices
        ]

        await asyncio.gather(*tasks)

    except Exception as exc:
        print(f"[broker] Failed to start sensor consumers: {exc}", flush=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(start_sensor_consumers())
    yield


app = FastAPI(
    title="Broker Service",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok",
        connected_sensors=len(connected_sensors),
        configured_replicas=len(PROCESSING_REPLICAS)
    )