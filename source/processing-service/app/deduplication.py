from datetime import datetime
from typing import Dict, Optional


class EventDeduplicator:
    def __init__(self, cooldown_seconds: int = 5, frequency_tolerance_hz: float = 0.5):
        self.cooldown_seconds = cooldown_seconds
        self.frequency_tolerance_hz = frequency_tolerance_hz
        self.last_events: Dict[str, dict] = {}

    def should_persist(
        self,
        sensor_id: str,
        event_type: str,
        dominant_frequency_hz: float,
        detected_at: datetime
    ) -> bool:
        last_event: Optional[dict] = self.last_events.get(sensor_id)

        if last_event is None:
            self.last_events[sensor_id] = {
                "event_type": event_type,
                "dominant_frequency_hz": dominant_frequency_hz,
                "detected_at": detected_at,
            }
            return True

        same_type = last_event["event_type"] == event_type
        frequency_close = abs(
            last_event["dominant_frequency_hz"] - dominant_frequency_hz
        ) <= self.frequency_tolerance_hz
        seconds_since_last = (detected_at - last_event["detected_at"]).total_seconds()
        within_cooldown = seconds_since_last <= self.cooldown_seconds

        if same_type and frequency_close and within_cooldown:
            return False

        self.last_events[sensor_id] = {
            "event_type": event_type,
            "dominant_frequency_hz": dominant_frequency_hz,
            "detected_at": detected_at,
        }
        return True