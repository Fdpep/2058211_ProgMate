# SYSTEM DESCRIPTION:

The system is a distributed and fault-tolerant seismic analysis platform designed to operate under unreliable conditions and partial failures, as defined in the mission scenario.

Seismic sensors deployed in geographically distributed locations continuously generate time-domain measurements. These measurements are collected from an external simulator and must be processed without hosting intelligence processing services in the neutral region.

A custom broker service, deployed in the neutral region, captures incoming measurements and redistributes them to multiple replicated processing services located in external data centers.

Each processing replica performs sliding-window analysis and applies FFT-based frequency-domain processing to extract dominant frequency components and classify seismic events.

Detected events are stored in a shared PostgreSQL database with duplicate-safe guarantees. A gateway service provides a single entry point for accessing stored data, while a frontend dashboard enables real-time monitoring and historical analysis.

The system is designed to remain operational even in the presence of processing replica failures. When replicas are terminated through the simulator control stream, the broker continues redistributing data to the remaining replicas, ensuring continuous system operation.

# USER STORIES:

1) As a command center operator, I want to monitor seismic events in real time, so that I can react immediately to potential threats.

2) As an analyst, I want to inspect historical seismic events, so that I can analyze past activity.

3) As an analyst, I want to filter events by sensor, so that I can focus on specific locations.

4) As an analyst, I want to filter events by event type, so that I can distinguish between earthquakes, explosions, and nuclear-like events.

5) As an analyst, I want to view the dominant frequency of an event, so that I can understand how it was classified.

6) As a system operator, I want processing services to be replicated, so that the system remains available in case of failure.

7) As a system operator, I want failed replicas to be automatically excluded from data redistribution, so that the system continues to function despite partial failures.

8) As a system operator, I want detected events to be stored in a shared database, so that all replicas contribute to a single source of truth.

9) As a system operator, I want duplicate events to be avoided, so that the stored data remains consistent and idempotent.

10) As an analyst, I want to know the region of each sensor, so that I can interpret the origin of events.

11) As an analyst, I want each event to include timestamps, so that I can correlate events over time.

12) As an operator, I want the entire platform to start with a single command, so that deployment is simple and reproducible.

13) As an examiner, I want the whole system to be reconstructable directly from the repository, so that I can verify its correctness during the discussion.

14) As an operator, I want the system to continue processing measurements even after a replica shutdown, so that monitoring is uninterrupted.

15) As a user, I want to access backend data through a single entry point, so that interaction with the system is consistent and simplified.

16) As a system operator, I want to monitor the health of processing replicas, so that I can detect failures and understand the current system state.
    
17) As a system operator, I want the system to automatically exclude unreachable processing replicas during data distribution, so that the platform continues operating despite partial failures.
    
18) As a system operator, I want to validate the system using controlled event injection, so that I can test detection, classification, and persistence end-to-end.
    
19) As an analyst, I want to view which replica detected each event, so that I can analyze how events are processed across the distributed system.
    
20) As an operator, I want the system to handle irregular or missing sensor data gracefully, so that frequency analysis remains reliable even in non-ideal streaming conditions.

# CONTAINERS:

The system is composed of multiple containers, each responsible for a specific functionality within the distributed architecture.

## CONTAINER_NAME: simulator

### DESCRIPTION:
Provides simulated seismic sensors and real-time measurement streams used by the system.

### USER STORIES:
Supports all system user stories by providing input data and failure simulation.

### PORTS:
8080:8080

### PERSISTENCE EVALUATION
No persistence required.

### EXTERNAL SERVICES CONNECTIONS
None.

### MICROSERVICES:

#### MICROSERVICE: simulator
- TYPE: external service
- DESCRIPTION: External container providing REST APIs for sensor discovery, WebSocket streams for real-time measurements, and SSE control stream for failure simulation of processing replicas.
- PORTS: 8080

---

## CONTAINER_NAME: broker-service

### DESCRIPTION:
Receives seismic measurements from the simulator and redistributes them to processing replicas without performing any form of data processing.

### USER STORIES:
6, 7, 14

### PORTS:
8001:8001

### PERSISTENCE EVALUATION
No persistence required.

### EXTERNAL SERVICES CONNECTIONS
Connects to simulator REST API and sensor WebSocket streams. Connects to processing replicas through HTTP.

### MICROSERVICES:

#### MICROSERVICE: broker
- TYPE: backend
- DESCRIPTION: Connects to sensor streams and forwards data to processing replicas.
- PORTS: 8001
- TECHNOLOGICAL SPECIFICATION:
Implemented in Python using FastAPI, requests, and async WebSocket clients.
- SERVICE ARCHITECTURE:
The broker discovers available sensors through the simulator API, establishes one WebSocket connection per sensor, and forwards each incoming measurement to all configured processing replicas (fan-out model). 
The broker strictly performs data distribution and does not perform any form of data processing, in compliance with system constraints.
It tolerates unreachable replicas by continuing distribution to the remaining available replicas without interrupting the data flow.

- ENDPOINTS:

| HTTP METHOD | URL | Description | User Stories |
| ----------- | --- | ----------- | ------------ |
| GET | /health | Returns broker health information | 6 |

---

## CONTAINER_NAME: processing-service

### DESCRIPTION:
Performs sliding-window analysis, FFT-based (DFT-equivalent) dominant frequency extraction, event classification, duplicate-safe persistence, and listens to the simulator control stream for shutdown commands.

### USER STORIES:
1, 2, 4, 5, 8, 9

### PORTS:
8101, 8102, 8103

### PERSISTENCE EVALUATION
Stores events in PostgreSQL.

### EXTERNAL SERVICES CONNECTIONS
Connects to simulator control stream (SSE) and to PostgreSQL.

### MICROSERVICES:

#### MICROSERVICE: processing
- TYPE: backend
- DESCRIPTION: Performs sliding window analysis and event classification.
- PORTS: 8100
- TECHNOLOGICAL SPECIFICATION:
Python with FastAPI and NumPy.
- SERVICE ARCHITECTURE:
Maintains in-memory sliding windows per sensor, applies FFT-based frequency-domain analysis (Discrete Fourier Transform equivalent), extracts dominant frequency components, classifies events according to predefined frequency bands, suppresses repeated equivalent detections in memory, persists events in PostgreSQL with duplicate-safe behavior, and terminates itself upon receiving a shutdown command from the simulator control stream.
The service guarantees idempotent persistence through deterministic event identifiers and database-level conflict handling.

- ENDPOINTS:

| HTTP METHOD | URL | Description | User Stories |
|------------|-----|------------|-------------|
| POST | /measurements | Receives sensor data from the broker and processes the current sliding window | 1 |
| GET | /health | Health check | 6 |

---

## CONTAINER_NAME: postgres

### DESCRIPTION:
Stores detected events.

### USER STORIES:
8, 9

### PORTS:
5432:5432

### PERSISTENCE EVALUATION
Persistent storage enabled.

### EXTERNAL SERVICES CONNECTIONS
None.

### MICROSERVICES:

#### MICROSERVICE: database
- TYPE: database
- DESCRIPTION: Stores seismic events.

- DB STRUCTURE:

**detected_events**

| Column                | Description                     |
|-----------------------|---------------------------------|
| event_id              | Unique deterministic identifier |
| sensor_id             | Sensor identifier               |
| sensor_name           | Human-readable sensor name      |
| sensor_region         | Sensor region                   |
| event_type            | Classified event type           |
| dominant_frequency_hz | Dominant frequency              |
| peak_amplitude        | Peak amplitude                  |
| window_start          | Start of analysis window        |
| window_end            | End of analysis window          |
| detected_at           | Detection timestamp             |
| replica_id            | Replica identifier              |
| created_at            | Insertion timestamp             |

---

## CONTAINER_NAME: gateway-service

### DESCRIPTION:
Provides a single entry point for the frontend and exposes read-only APIs for retrieving detected seismic events from PostgreSQL.

### USER STORIES:
1, 2, 3, 4, 15

### PORTS:
8000:8000

### PERSISTENCE EVALUATION
No persistence required. The service reads data from PostgreSQL and does not store internal state.

### EXTERNAL SERVICES CONNECTIONS
Connects to PostgreSQL.

### MICROSERVICES:

#### MICROSERVICE: gateway
- TYPE: backend
- DESCRIPTION: Exposes REST APIs for health checks, event list retrieval, filtered event queries, and event detail retrieval.
- PORTS: 8000
- TECHNOLOGICAL SPECIFICATION:
Python with FastAPI and psycopg2.
- SERVICE ARCHITECTURE:
Stateless read-only REST service connected to PostgreSQL. It acts as the single backend entry point required by the system specification and enables fault-tolerant access to detected events independently from processing replicas. It supports event filtering by sensor, type, region, and time interval.
The gateway performs periodic health checks on processing replicas and exposes system-level status, allowing the system to detect failures and operate in degraded mode when some replicas are unavailable.

- ENDPOINTS:

| HTTP METHOD | URL | Description | User Stories |
| ----------- | --- | ----------- | ------------ |
| GET | /health | Returns service and database health information | 6 |
| GET | /events | Returns detected events with optional filtering and pagination | 2, 3, 4 |
| GET | /events/{event_id} | Returns the details of a specific detected event | 3, 4 |

---

## CONTAINER_NAME: frontend-dashboard

### DESCRIPTION:
Provides real-time visualization and historical inspection of detected seismic events through a web dashboard connected to the gateway service.

### USER STORIES:
1, 2, 3, 4

### PORTS:
3000:3000

### PERSISTENCE EVALUATION
No persistence required.

### EXTERNAL SERVICES CONNECTIONS
Connects to the gateway service.

### MICROSERVICES:

#### MICROSERVICE: frontend
- TYPE: frontend
- DESCRIPTION: Displays the dashboard for seismic event monitoring, filtering, and periodic refresh of detected events.
- PORTS: 3000
- TECHNOLOGICAL SPECIFICATION:
React with Vite, served through Nginx in the container.
- SERVICE ARCHITECTURE:
Single-page frontend application that queries the gateway service through REST APIs. It supports event list visualization, filtering by sensor, event type, and region, and periodic polling for near real-time updates.
Real-time updates are implemented through periodic REST polling, which satisfies the real-time requirement defined in the system specification.

- PAGES:

| Name | Description | Related Microservice | User Stories |
|------|------------|----------------------|-------------|
| Dashboard | Displays detected events, filtering controls, refresh actions, and historical event inspection in tabular form | gateway | 1, 2, 3, 4 |



---

## CONTAINER_NAME: demo-injector

### DESCRIPTION:
Provides automated event injection for testing and validation purposes by interacting with the simulator administrative API.

### USER STORIES:
18

### PORTS:
None

### PERSISTENCE EVALUATION
No persistence required.

### EXTERNAL SERVICES CONNECTIONS
Connects to the simulator REST API to trigger synthetic seismic events.

### MICROSERVICES:

#### MICROSERVICE: demo-injector
- TYPE: support tool
- DESCRIPTION: Automatically injects predefined seismic events into selected sensors to validate end-to-end system behavior, including detection, classification, and persistence.
- TECHNOLOGICAL SPECIFICATION:
Python with requests library.
- SERVICE ARCHITECTURE:
The service waits for the simulator to become available, retrieves the list of sensors, and periodically injects predefined event types into a subset of sensors.  
This ensures deterministic system validation and avoids reliance on random low-frequency background signals generated by the simulator.