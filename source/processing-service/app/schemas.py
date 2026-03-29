# Modelli 

from pydantic import BaseModel
from datetime import datetime


class MeasurementIn(BaseModel):
    sensor_id: str
    sensor_name: str
    sensor_region: str
    timestamp: datetime
    value: float


class HealthResponse(BaseModel):
    status: str
    replica_id: str