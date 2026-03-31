from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.replicas import (
    check_replicas_health,
    compute_system_status,
    fetch_runtime_info_from_available_replica,
)

from app.db import check_database_connection, fetch_event_by_id, fetch_events
from app.schemas import EventOut, HealthResponse


app = FastAPI(
    title="Gateway Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health_check():
    try:
        database_ok = check_database_connection()
    except Exception:
        database_ok = False

    if not database_ok:
        raise HTTPException(status_code=500, detail="Database connection unavailable.")

    return HealthResponse(status="ok", database="reachable")


@app.get("/events", response_model=List[EventOut])
def get_events(
    sensor_id: Optional[str] = Query(default=None),
    event_type: Optional[str] = Query(default=None),
    sensor_region: Optional[str] = Query(default=None),
    start_time: Optional[datetime] = Query(default=None),
    end_time: Optional[datetime] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    try:
        events = fetch_events(
            sensor_id=sensor_id,
            event_type=event_type,
            sensor_region=sensor_region,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset,
        )
        return events
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(exc)}"
        ) from exc


@app.get("/events/{event_id}", response_model=EventOut)
def get_event_by_id(event_id: str):
    try:
        event = fetch_event_by_id(event_id)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(exc)}"
        ) from exc

    if not event:
        raise HTTPException(status_code=404, detail="Event not found.")

    return event

@app.get("/replicas/health")
def get_replicas_health():
    return check_replicas_health()


@app.get("/system/status")
def get_system_status():
    replicas_health = check_replicas_health()
    system_status = compute_system_status(replicas_health)

    return {
        "status": system_status,
        "replicas": replicas_health,
        "active_replicas": sum(1 for s in replicas_health.values() if s == "UP"),
        "total_replicas": len(replicas_health),
    }

@app.get("/processing/runtime")
def get_processing_runtime():
    runtime_info = fetch_runtime_info_from_available_replica()

    if runtime_info is None:
        raise HTTPException(
            status_code=503,
            detail="No processing replicas are currently available."
        )

    return runtime_info