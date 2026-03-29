# SYSTEM DESCRIPTION:

The system is a distributed and fault-tolerant seismic analysis platform designed to process real-time seismic data collected from geographically distributed sensors.

The platform receives continuous streams of seismic measurements from an external simulator. These measurements are redistributed through a custom broker to multiple replicated processing services. Each processing replica performs frequency-domain analysis using FFT, extracts dominant frequencies, and classifies events into predefined categories.

Detected events are stored in a shared PostgreSQL database with duplicate-safe behavior. A gateway service provides a single entry point for accessing the system, while a frontend dashboard enables real-time monitoring and historical analysis.

The system is designed to remain operational even in the presence of partial failures, particularly when one or more processing replicas are shut down.

# USER STORIES:

1) As a command center operator, I want to monitor seismic events in real time, so that I can react immediately to potential threats.

2) As an analyst, I want to inspect historical seismic events, so that I can analyze past activity.

3) As an analyst, I want to filter events by sensor, so that I can focus on specific locations.

4) As an analyst, I want to filter events by event type, so that I can distinguish between earthquakes, explosions, and nuclear-like events.

5) As an analyst, I want to view the dominant frequency of an event, so that I can understand how it was classified.

6) As a system operator, I want processing services to be replicated, so that the system remains available in case of failure.

7) As a system operator, I want failed replicas to be automatically excluded, so that the system continues to function.

8) As a system operator, I want detected events to be stored in a shared database, so that all replicas contribute to a single source of truth.

9) As a system operator, I want duplicate events to be avoided, so that the stored data remains consistent.

10) As an analyst, I want to know the region of each sensor, so that I can interpret the origin of events.

11) As an analyst, I want each event to include timestamps, so that I can correlate events over time.

12) As an operator, I want the system to start with a single command, so that deployment is simple and reproducible.

13) As an examiner, I want the system to be fully reconstructable from the repository, so that I can verify its correctness.

14) As an operator, I want the system to continue processing data even after a replica shutdown, so that monitoring is uninterrupted.

15) As a user, I want to access the system through a single entry point, so that interaction is consistent and simplified.

# STANDARD EVENT SCHEMA:

Each detected event has the following structure:

- event_id: unique identifier of the event
- sensor_id: identifier of the sensor
- sensor_name: name of the sensor
- sensor_region: geographical region of the sensor
- event_type: earthquake | conventional_explosion | nuclear_like_event
- dominant_frequency_hz: dominant frequency extracted from the signal
- peak_amplitude: maximum amplitude detected in the window
- window_start: start timestamp of the analysis window
- window_end: end timestamp of the analysis window
- detected_at: timestamp of detection
- replica_id: identifier of the processing replica

# RULE MODEL:

The classification is based on the dominant frequency extracted from the signal using FFT:

- Earthquake: 0.5 <= f < 3.0 Hz
- Conventional explosion: 3.0 <= f < 8.0 Hz
- Nuclear-like event: f >= 8.0 Hz

If the dominant frequency is below 0.5 Hz, no event is generated.