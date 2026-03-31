# USER STORIES

## Command Center Operator

1) As a command center operator, I want to monitor seismic events in real time so that I can react immediately to potential threats.


## Analyst

2) As an analyst, I want to inspect historical seismic events so that I can analyze past activity.

3) As an analyst, I want to filter events by sensor so that I can focus on specific locations.

4) As an analyst, I want to filter events by event type so that I can distinguish between earthquakes, explosions, and nuclear-like events.

5) As an analyst, I want to view the dominant frequency of an event so that I can understand how it was classified.

6) As an analyst, I want to view the peak amplitude of an event so that I can evaluate the intensity of the detected disturbance.

7) As an analyst, I want to know the region of each sensor so that I can interpret the origin of events.

8) As an analyst, I want each event to include timestamps so that I can correlate events over time.

9) As an analyst, I want to view which replica detected each event so that I can understand how detections are distributed across the system.


## System Operator

10) As a system operator, I want processing services to be replicated so that the system remains available in case of failure.

11) As a system operator, I want unreachable replicas to be automatically excluded from data redistribution so that the platform continues operating despite partial failures.

12) As a system operator, I want detected events to be stored in a shared database so that all replicas contribute to a single source of truth.

13) As a system operator, I want duplicate events to be avoided so that stored data remains consistent and idempotent.

14) As a system operator, I want the system to continue processing measurements even after a replica shutdown so that monitoring is uninterrupted.

16) As a system operator, I want to monitor the health of processing replicas so that I can detect failures and understand the current system status.

19) As a system operator, I want to validate the platform using controlled event injection so that I can test detection, classification, persistence, and visualization end-to-end.


## User

15) As a user, I want to access backend data through a single entry point so that interaction with the system is consistent and simplified.


## Operator (Deployment / Exam)

17) As an operator, I want the entire platform to start with a single command so that deployment is simple and reproducible.

18) As an examiner, I want the whole system to be reconstructable directly from the repository so that I can verify its correctness during the discussion.

20) As an operator, I want the system to handle irregular or missing sensor data gracefully so that frequency analysis remains reliable even in non-ideal streaming conditions.