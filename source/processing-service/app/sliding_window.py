from collections import deque
from typing import Dict, Deque


class SlidingWindowManager:
    def __init__(self, window_size: int):
        self.window_size = window_size
        self.windows: Dict[str, Deque[dict]] = {}

    def add_measurement(self, sensor_id: str, measurement: dict) -> None:
        if sensor_id not in self.windows:
            self.windows[sensor_id] = deque(maxlen=self.window_size)

        window = self.windows[sensor_id]

        if window:
            last_timestamp = window[-1]["timestamp"]
            current_timestamp = measurement["timestamp"]

            delta = (current_timestamp - last_timestamp).total_seconds()

            # Reset solo se il gap è davvero anomalo
            if delta > 0.5:
                window.clear()

        window.append(measurement)

    def get_window(self, sensor_id: str):
        return list(self.windows.get(sensor_id, []))

    def is_window_ready(self, sensor_id: str) -> bool:
        return len(self.windows.get(sensor_id, [])) == self.window_size