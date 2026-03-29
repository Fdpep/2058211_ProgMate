from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    connected_sensors: int
    configured_replicas: int