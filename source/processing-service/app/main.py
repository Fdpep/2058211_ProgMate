from datetime import datetime, timezone
from app.deduplication import EventDeduplicator

from fastapi import FastAPI, HTTPException

from app.classifier import classify_event
from app.config import REPLICA_ID, SAMPLING_RATE_HZ, WINDOW_SIZE_SAMPLES
from app.fft_analysis import extract_dominant_frequency, extract_peak_amplitude
from app.persistence import generate_event_id, save_event
from app.schemas import MeasurementIn, HealthResponse
from app.sliding_window import SlidingWindowManager


app = FastAPI(title="Processing Service", version="1.0.0")

window_manager = SlidingWindowManager(window_size=WINDOW_SIZE_SAMPLES)
event_deduplicator = EventDeduplicator(cooldown_seconds=5, frequency_tolerance_hz=0.5)

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok", replica_id=REPLICA_ID)


@app.post("/measurements")
def receive_measurement(measurement: MeasurementIn):
    measurement_dict = {
        "timestamp": measurement.timestamp,
        "value": measurement.value,
        "sensor_name": measurement.sensor_name,
        "sensor_region": measurement.sensor_region,
    }

    window_manager.add_measurement(measurement.sensor_id, measurement_dict)

    if not window_manager.is_window_ready(measurement.sensor_id):
        return {
            "status": "accepted",
            "message": "Measurement stored, window not ready yet."
        }

    window = window_manager.get_window(measurement.sensor_id)
    samples = [item["value"] for item in window]

    dominant_frequency_hz = extract_dominant_frequency(samples, SAMPLING_RATE_HZ)
    event_type = classify_event(dominant_frequency_hz)

    if event_type is None:
        return {
            "status": "accepted",
            "message": "Window analyzed, no classified event generated."
        }

    peak_amplitude = extract_peak_amplitude(samples)
    window_start = window[0]["timestamp"]
    window_end = window[-1]["timestamp"]
    detected_at = datetime.now(timezone.utc)

    should_persist_event = event_deduplicator.should_persist(
        sensor_id=measurement.sensor_id,
        event_type=event_type,
        dominant_frequency_hz=dominant_frequency_hz,
        detected_at=detected_at,
    )

    if not should_persist_event:
        return {
            "status": "processed",
            "event_detected": True,
            "event_inserted": False,
            "message": "Event suppressed by in-memory deduplication policy.",
            "event_type": event_type,
            "dominant_frequency_hz": dominant_frequency_hz,
            "replica_id": REPLICA_ID,
        }

    event_id = generate_event_id(
        sensor_id=measurement.sensor_id,
        event_type=event_type,
        window_start=window_start.isoformat(),
        window_end=window_end.isoformat(),
        dominant_frequency_hz=dominant_frequency_hz,
    )

    event_payload = {
        "event_id": event_id,
        "sensor_id": measurement.sensor_id,
        "sensor_name": measurement.sensor_name,
        "sensor_region": measurement.sensor_region,
        "event_type": event_type,
        "dominant_frequency_hz": dominant_frequency_hz,
        "peak_amplitude": peak_amplitude,
        "window_start": window_start,
        "window_end": window_end,
        "detected_at": detected_at,
        "replica_id": REPLICA_ID,
    }

    try:
        inserted = save_event(event_payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database error: {str(exc)}") from exc

    return {
        "status": "processed",
        "event_detected": True,
        "event_inserted": inserted,
        "event_id": event_id,
        "event_type": event_type,
        "dominant_frequency_hz": dominant_frequency_hz,
        "replica_id": REPLICA_ID,
    }