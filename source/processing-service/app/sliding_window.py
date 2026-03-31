from collections import deque
from typing import Deque, Dict


class SlidingWindowManager:
    def __init__(self, window_size: int, analysis_stride: int):
        self.window_size = window_size
        self.analysis_stride = max(1, analysis_stride)
        self.windows: Dict[str, Deque[dict]] = {}
        self.new_samples_since_last_analysis: Dict[str, int] = {}

    def add_measurement(self, sensor_id: str, measurement: dict) -> None:
        if sensor_id not in self.windows:
            self.windows[sensor_id] = deque(maxlen=self.window_size)
            self.new_samples_since_last_analysis[sensor_id] = 0

        window = self.windows[sensor_id]

        if window:
            last_timestamp = window[-1]["timestamp"]
            current_timestamp = measurement["timestamp"]

            delta = (current_timestamp - last_timestamp).total_seconds()

            # Reset solo se il gap è davvero anomalo
            if delta > 1.0:
                window.clear()
                self.new_samples_since_last_analysis[sensor_id] = 0

        window.append(measurement)

        if len(window) == self.window_size:
            self.new_samples_since_last_analysis[sensor_id] += 1

    def get_window(self, sensor_id: str):
        return list(self.windows.get(sensor_id, []))

    def is_window_ready(self, sensor_id: str) -> bool:
        return len(self.windows.get(sensor_id, [])) == self.window_size

    def should_analyze(self, sensor_id: str) -> bool:
        if not self.is_window_ready(sensor_id):
            return False

        pending = self.new_samples_since_last_analysis.get(sensor_id, 0)
        return pending >= self.analysis_stride

    def mark_analyzed(self, sensor_id: str) -> None:
        if sensor_id in self.new_samples_since_last_analysis:
            self.new_samples_since_last_analysis[sensor_id] = 0