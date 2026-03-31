import asyncio
import json
from contextlib import asynccontextmanager

import websockets
from fastapi import FastAPI

from app.config import (
    PROCESSING_REPLICAS,
    BROKER_QUEUE_MAXSIZE,
    BROKER_WORKER_COUNT,
)
from app.distributor import distribute_measurement
from app.schemas import HealthResponse
from app.simulator_client import fetch_devices


connected_sensors = []
dropped_measurements = 0

# Una queue per worker, così preserviamo l'ordine per sensore
worker_queues = []
worker_drop_counts = []


def get_worker_index(sensor_id: str) -> int:
    # hash stabile, non usare hash() di Python
    return sum(ord(char) for char in sensor_id) % BROKER_WORKER_COUNT


async def consume_sensor_stream(sensor: dict) -> None:
    global dropped_measurements

    sensor_id = sensor["id"]
    sensor_name = sensor["name"]
    sensor_region = sensor["region"]

    websocket_url = f"ws://simulator:8080/api/device/{sensor_id}/ws"

    while True:
        try:
            print(
                f"[broker] Connecting to sensor stream: {sensor_id} -> {websocket_url}",
                flush=True
            )

            async with websockets.connect(
                websocket_url,
                ping_interval=20,
                ping_timeout=60,
                close_timeout=10,
            ) as websocket:
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

                    worker_index = get_worker_index(sensor_id)

                    try:
                        worker_queues[worker_index].put_nowait(measurement)
                    except asyncio.QueueFull:
                        dropped_measurements += 1
                        worker_drop_counts[worker_index] += 1

                        if dropped_measurements % 100 == 0:
                            print(
                                f"[broker] Queue full on worker-{worker_index + 1}. "
                                f"Dropped measurements so far: {dropped_measurements}",
                                flush=True
                            )

        except Exception as exc:
            print(
                f"[broker] Sensor stream error for {sensor_id}: {exc}. "
                f"Reconnecting in 3 seconds.",
                flush=True
            )
            await asyncio.sleep(3)


async def distribution_worker(worker_id: int) -> None:
    queue_index = worker_id - 1
    print(f"[broker] Distribution worker started: worker-{worker_id}", flush=True)

    while True:
        measurement = await worker_queues[queue_index].get()

        try:
            await asyncio.to_thread(distribute_measurement, measurement)
        except Exception as exc:
            print(
                f"[broker] Distribution error in worker-{worker_id}: {exc}",
                flush=True
            )
        finally:
            worker_queues[queue_index].task_done()


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

        sensor_tasks = [
            asyncio.create_task(consume_sensor_stream(sensor))
            for sensor in devices
        ]

        worker_tasks = [
            asyncio.create_task(distribution_worker(worker_id))
            for worker_id in range(1, BROKER_WORKER_COUNT + 1)
        ]

        await asyncio.gather(*(sensor_tasks + worker_tasks))

    except Exception as exc:
        print(f"[broker] Failed to start sensor consumers: {exc}", flush=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global worker_queues, worker_drop_counts

    per_worker_queue_size = max(1, BROKER_QUEUE_MAXSIZE // BROKER_WORKER_COUNT)

    worker_queues = [
        asyncio.Queue(maxsize=per_worker_queue_size)
        for _ in range(BROKER_WORKER_COUNT)
    ]
    worker_drop_counts = [0 for _ in range(BROKER_WORKER_COUNT)]

    print(
        f"[broker] Starting broker service with "
        f"{len(PROCESSING_REPLICAS)} configured processing replicas, "
        f"queue_maxsize={BROKER_QUEUE_MAXSIZE}, "
        f"worker_count={BROKER_WORKER_COUNT}, "
        f"per_worker_queue_size={per_worker_queue_size}.",
        flush=True
    )
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


@app.get("/runtime-info")
def runtime_info():
    queue_sizes = [queue.qsize() for queue in worker_queues]

    return {
        "status": "ok",
        "connected_sensors": len(connected_sensors),
        "configured_replicas": len(PROCESSING_REPLICAS),
        "worker_count": BROKER_WORKER_COUNT,
        "total_queue_size": sum(queue_sizes),
        "queue_sizes_by_worker": {
            f"worker-{index + 1}": size
            for index, size in enumerate(queue_sizes)
        },
        "queue_maxsize_total": BROKER_QUEUE_MAXSIZE,
        "queue_maxsize_per_worker": (
            max(1, BROKER_QUEUE_MAXSIZE // BROKER_WORKER_COUNT)
        ),
        "dropped_measurements": dropped_measurements,
        "dropped_by_worker": {
            f"worker-{index + 1}": count
            for index, count in enumerate(worker_drop_counts)
        },
    }