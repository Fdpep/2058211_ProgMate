from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    database: str


class EventOut(BaseModel):
    event_id: str
    sensor_id: str
    sensor_name: str
    sensor_region: str
    event_type: str
    dominant_frequency_hz: float
    peak_amplitude: float
    window_start: datetime
    window_end: datetime
    detected_at: datetime
    replica_id: str
    created_at: datetime


class EventFilters(BaseModel):
    sensor_id: Optional[str] = None
    event_type: Optional[str] = None
    sensor_region: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = 50
    offset: int = 0