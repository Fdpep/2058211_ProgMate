from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

from app.classifier import classify_event
from app.config import (
    REPLICA_ID,
    SAMPLING_RATE_HZ,
    WINDOW_SIZE_SAMPLES,
    ANALYSIS_STRIDE_SAMPLES,
    EVENT_DEDUP_COOLDOWN_SECONDS,
    MIN_CLASSIFIABLE_FREQUENCY_HZ,
    MIN_CLASSIFIABLE_PEAK_MAGNITUDE,
    LOG_NON_EVENT_WINDOWS,
)
from app.control_listener import start_control_listener
from app.deduplication import EventDeduplicator
from app.fft_analysis import analyze_frequency_spectrum, extract_peak_amplitude
from app.persistence import generate_event_id, save_event
from app.schemas import HealthResponse, MeasurementIn
from app.sliding_window import SlidingWindowManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(
        f"[{REPLICA_ID}] Starting processing service "
        f"(sampling_rate_hz={SAMPLING_RATE_HZ}, "
        f"window_size_samples={WINDOW_SIZE_SAMPLES}, "
        f"analysis_stride_samples={ANALYSIS_STRIDE_SAMPLES})",
        flush=True
    )
    start_control_listener()
    yield


app = FastAPI(
    title="Processing Service",
    version="1.0.0",
    lifespan=lifespan
)

window_manager = SlidingWindowManager(
    window_size=WINDOW_SIZE_SAMPLES,
    analysis_stride=ANALYSIS_STRIDE_SAMPLES,
)
event_deduplicator = EventDeduplicator(
    cooldown_seconds=EVENT_DEDUP_COOLDOWN_SECONDS,
    frequency_tolerance_hz=0.8
)


@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok", replica_id=REPLICA_ID)


@app.get("/runtime-info")
def runtime_info():
    return {
        "status": "ok",
        "replica_id": REPLICA_ID,
        "sampling_rate_hz": SAMPLING_RATE_HZ,
        "window_size_samples": WINDOW_SIZE_SAMPLES,
        "analysis_stride_samples": ANALYSIS_STRIDE_SAMPLES,
        "tracked_sensors": len(window_manager.windows),
    }


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

    if not window_manager.should_analyze(measurement.sensor_id):
        return {
            "status": "accepted",
            "message": "Measurement stored, analysis deferred by stride policy."
        }

    window = window_manager.get_window(measurement.sensor_id)
    samples = [item["value"] for item in window]

    spectrum = analyze_frequency_spectrum(
        samples,
        SAMPLING_RATE_HZ,
        min_classifiable_frequency_hz=MIN_CLASSIFIABLE_FREQUENCY_HZ,
    )

    overall_dominant_frequency_hz = spectrum["overall_dominant_frequency_hz"]
    dominant_frequency_hz = spectrum["classifiable_dominant_frequency_hz"]
    signal_rms = spectrum["signal_rms"]
    classifiable_peak_magnitude = spectrum["classifiable_peak_magnitude"]

    event_type = None
    if (
        dominant_frequency_hz >= MIN_CLASSIFIABLE_FREQUENCY_HZ
        and classifiable_peak_magnitude >= MIN_CLASSIFIABLE_PEAK_MAGNITUDE
    ):
        event_type = classify_event(dominant_frequency_hz)

    window_manager.mark_analyzed(measurement.sensor_id)

    if event_type is None:
        if LOG_NON_EVENT_WINDOWS:
            print(
                f"[{REPLICA_ID}] No classified event for {measurement.sensor_id}: "
                f"overall_dominant_frequency_hz={overall_dominant_frequency_hz:.2f}, "
                f"classifiable_dominant_frequency_hz={dominant_frequency_hz:.2f}, "
                f"filtered_signal_rms={signal_rms:.4f}, "
                f"classifiable_peak_magnitude={classifiable_peak_magnitude:.4f}",
                flush=True
            )
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
        print(
            f"[{REPLICA_ID}] Database error for {measurement.sensor_id}: {str(exc)}",
            flush=True
        )
        raise HTTPException(status_code=500, detail=f"Database error: {str(exc)}") from exc

    print(
        f"[{REPLICA_ID}] Event processed for {measurement.sensor_id}: "
        f"event_type={event_type}, dominant_frequency_hz={dominant_frequency_hz:.2f}, "
        f"inserted={inserted}, event_id={event_id}",
        flush=True
    )

    return {
        "status": "processed",
        "event_detected": True,
        "event_inserted": inserted,
        "event_id": event_id,
        "event_type": event_type,
        "dominant_frequency_hz": dominant_frequency_hz,
        "replica_id": REPLICA_ID,
    }