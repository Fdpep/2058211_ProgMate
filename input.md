# SYSTEM OVERVIEW

The system is a distributed and fault-tolerant seismic analysis platform designed to process real-time seismic data collected from geographically distributed sensors.

The platform integrates with an external seismic simulator that provides:

- sensor discovery through REST APIs  
- real-time measurement streams via WebSocket  
- a control stream used to simulate processing node failures  

A custom broker service is responsible for:

- discovering available sensors  
- subscribing to their WebSocket streams  
- redistributing each incoming measurement to multiple processing replicas  

The broker acts purely as a fan-out component and does not perform any form of data processing.

Processing services are replicated and operate independently. Each replica:

- maintains an in-memory sliding window for each sensor  
- performs FFT-based frequency-domain analysis  
- extracts dominant frequency and signal characteristics  
- classifies seismic events according to predefined frequency ranges  

Detected events are stored in a shared PostgreSQL database. The persistence layer ensures idempotency through deterministic event identifiers and database-level conflict handling. Additionally, each replica applies an in-memory suppression policy to reduce redundant detections caused by overlapping windows.

A gateway service provides a single entry point for the frontend dashboard. The dashboard allows:

- near real-time monitoring of detected events  
- historical inspection through filtering and pagination  
- visualization of system status and replica availability  

The system is designed to remain operational under partial failures. Processing replicas may be terminated through the simulator control stream, but the broker continues distributing measurements to the remaining available replicas, ensuring uninterrupted operation.

# USER STORIES

1) As a command center operator, I want to monitor seismic events in real time so that I can react immediately to potential threats.

2) As an analyst, I want to inspect historical seismic events so that I can analyze past activity.

3) As an analyst, I want to filter events by sensor so that I can focus on specific locations.

4) As an analyst, I want to filter events by event type so that I can distinguish between earthquakes, explosions, and nuclear-like events.

5) As an analyst, I want to view the dominant frequency of an event so that I can understand how it was classified.

6) As an analyst, I want to view the peak amplitude of an event so that I can evaluate its intensity.

7) As an analyst, I want to see the region of each sensor so that I can interpret the origin of events.

8) As an analyst, I want each event to include timestamps so that I can correlate events over time.

9) As an analyst, I want to see which processing replica detected each event so that I can understand how events are distributed across the system.

10) As a system operator, I want processing services to be replicated so that the system remains available in case of failure.

11) As a system operator, I want failed replicas to be automatically excluded from data redistribution so that the system continues to function despite partial failures.

12) As a system operator, I want detected events to be stored in a shared database so that all replicas contribute to a single source of truth.

13) As a system operator, I want duplicate events to be avoided so that stored data remains consistent and idempotent.

14) As a system operator, I want the system to continue processing measurements even after a replica shutdown so that monitoring is uninterrupted.

15) As a system operator, I want to monitor the health of processing replicas so that I can detect failures and understand the system status.

16) As an operator, I want the entire platform to start with a single command so that deployment is simple and reproducible.

17) As an examiner, I want the system to be reconstructable directly from the repository so that I can verify its correctness during the discussion.

18) As an operator, I want to validate the system using controlled event injection so that I can test detection, classification, and persistence end-to-end.

19) As a user, I want to access backend data through a single entry point so that interaction with the system is consistent and simplified.

20) As a system operator, I want the system to handle irregular or missing sensor data gracefully so that analysis remains reliable under non-ideal conditions.

# STANDARD EVENT SCHEMA

Each detected event follows the structure below:

- event_id: unique deterministic identifier of the event  
- sensor_id: unique identifier of the sensor  
- sensor_name: human-readable sensor name  
- sensor_region: region associated with the sensor  
- event_type: classified event type (earthquake, conventional_explosion, nuclear_like)  
- dominant_frequency_hz: dominant frequency extracted from the analysis window  
- peak_amplitude: maximum absolute amplitude observed in the window  
- window_start: timestamp of the first sample in the analyzed window  
- window_end: timestamp of the last sample in the analyzed window  
- detected_at: timestamp of event detection  
- replica_id: identifier of the processing replica that generated the event  

# RULE MODEL

## Signal acquisition and distribution

- Sensors are discovered via the simulator REST API.  
- Measurements are received through WebSocket streams.  
- Each measurement is forwarded by the broker to processing replicas.  
- The broker performs no analysis and acts only as a distribution component.  
- If some replicas are unavailable, the broker continues forwarding data to the remaining reachable ones.  

## Sliding window analysis

- Each processing replica maintains a sliding window per sensor.  
- Window size: 5 seconds.  
- Sampling rate: 20 Hz.  
- Each window contains 100 samples.  
- Analysis is performed only when the window is full.  
- Windows overlap through a stride-based mechanism to ensure continuous analysis.  

## Event classification

Events are classified based on dominant frequency:

- Earthquake: 0.5 ≤ f < 3.0 Hz  
- Conventional explosion: 3.0 ≤ f < 8.0 Hz  
- Nuclear-like event: f ≥ 8.0 Hz  

No event is generated for frequencies below 0.5 Hz.

## Simulator behavior note

Under normal conditions, the simulator may produce low-frequency signals (e.g., 0.2–0.4 Hz), which do not trigger classification.

To demonstrate the system behavior, controlled event injection can be performed using simulator administrative endpoints.

## Duplicate-safe persistence

- Each event has a deterministic event_id.  
- Events are stored in PostgreSQL.  
- Database-level conflict handling prevents duplicates.  
- Each replica applies an in-memory suppression policy based on time and frequency similarity.  

## Fault tolerance

- Processing replicas listen to the simulator control stream.  
- Upon receiving a SHUTDOWN command, a replica terminates.  
- The system continues operating with remaining replicas.  

## Access and visualization

- The gateway acts as the single entry point for the frontend.  
- The dashboard retrieves events via the gateway.  
- Real-time updates are implemented through periodic polling.  
- Historical exploration is supported through filtering and pagination.  

## Validation and testing

The simulator provides administrative endpoints for event injection and shutdown simulation.

These features are used exclusively for testing and demonstration purposes and do not affect the core processing logic.