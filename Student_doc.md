# SYSTEM DESCRIPTION:

The system is a distributed seismic analysis platform designed to process real-time sensor data and detect significant events through frequency analysis.

It consists of multiple containers responsible for data ingestion, processing, storage, and visualization. The system is fault-tolerant and continues operating even when processing replicas fail.

# USER STORIES:

(see input.md)

# CONTAINERS:

## CONTAINER_NAME: simulator

### DESCRIPTION:
Provides simulated seismic sensors and real-time measurement streams used by the system.

### USER STORIES:
1, 6

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
Receives seismic measurements from the simulator and redistributes them to processing replicas.

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
Single service that discovers sensors through the simulator API, subscribes to sensor WebSocket streams, and redistributes incoming measurements to all configured processing replicas. It tolerates unreachable replicas without stopping overall operation.

- ENDPOINTS:

| HTTP METHOD | URL | Description | User Stories |
| ----------- | --- | ----------- | ------------ |
| GET | /health | Returns broker health information | 6 |

---

## CONTAINER_NAME: processing-service

### DESCRIPTION:
Performs sliding-window analysis, FFT-based dominant frequency extraction, event classification, duplicate-safe persistence, and listens to the simulator control stream for shutdown commands.

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
Maintains in-memory windows per sensor, applies FFT on incoming data, classifies events according to dominant frequency, suppresses repeated equivalent detections in memory, persists events in PostgreSQL, and terminates itself when a shutdown command is received from the simulator control stream. The service ensures idempotent event persistence through deterministic event identifiers and database-level conflict handling.

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

**detected_events** :
| event_id | sensor_id | sensor_name | sensor_region | event_type | dominant_frequency_hz | peak_amplitude | window_start | window_end | detected_at | replica_id | created_at |

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

- PAGES:

| Name | Description | Related Microservice | User Stories |
|------|------------|----------------------|-------------|
| Dashboard | Displays detected events, filtering controls, refresh actions, and historical event inspection in tabular form | gateway | 1, 2, 3, 4 |