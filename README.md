# Seismic Surveillance Platform

## Project Overview

This project implements a distributed and fault-tolerant seismic analysis platform developed for the 2026/04 Laboratory of Advanced programming's hackaton.

The system ingests real-time seismic measurements from a provided simulator, redistributes them across replicated processing services, performs frequency-domain analysis using FFT, classifies seismic events, and stores them with duplicate-safe guarantees.

A gateway service provides a single entry point for data access, while a frontend dashboard enables real-time monitoring and historical inspection of detected events.

The system is designed to operate under partial failures, ensuring continuous functionality even when processing replicas are shut down.

---

## Architecture Overview

The platform is composed of the following services:

* **Simulator (given)**
  Provides seismic sensors, WebSocket streams, and failure simulation via SSE control stream.

* **Broker Service**
  Discovers sensors, subscribes to their streams, and redistributes measurements to processing replicas (fan-out model).

* **Processing Services (replicated)**
  Perform sliding-window analysis, FFT processing, event classification, and persistence.

* **PostgreSQL Database**
  Stores detected events with duplicate-safe behavior.

* **Gateway Service**
  Provides a single entry point for querying stored events and system status.

* **Frontend Dashboard**
  Displays real-time and historical seismic events with filtering capabilities.

---

## Key Features

* Distributed microservice architecture
* Replicated processing services
* Fault tolerance with simulated replica shutdowns
* Sliding-window signal processing
* FFT-based frequency analysis
* Event classification based on frequency bands
* Duplicate-safe event persistence
* Real-time dashboard (REST polling)
* Fully containerized system (Docker Compose)

---

## Repository Structure

```
.
├── input.md
├── Student_doc.md
├── WORKLOG.md
├── README.md
├── booklets/
└── source/
    ├── docker-compose.yml
    ├── db/
    ├── broker-service/
    ├── processing-service/
    ├── gateway-service/
    └── frontend-dashboard/
```

---

## How to Run the System

### 1. Requirements

* Docker
* Docker Compose

---

### 2. Start the system

From the `source/` directory:

```bash
docker compose up --build
```

This will start all services:

* simulator
* postgres
* broker-service
* processing replicas (3)
* gateway-service
* frontend-dashboard

---

### 3. Access the services

* **Frontend Dashboard**
  http://localhost:3000

* **Gateway API**
  http://localhost:8000

* **Simulator API & Docs**
  http://localhost:8080
  http://localhost:8080/docs

---

## System Workflow

1. The broker retrieves the list of sensors from the simulator.
2. The broker opens one WebSocket stream per sensor.
3. Each incoming measurement is redistributed to all processing replicas.
4. Each processing replica:

   * maintains a sliding window per sensor
   * applies FFT analysis
   * extracts dominant frequency and peak amplitude
   * classifies events based on frequency ranges
5. Detected events are stored in PostgreSQL with duplicate-safe logic.
6. The gateway exposes read APIs for event retrieval.
7. The frontend dashboard periodically fetches data and displays events.

---

## Fault Tolerance

* Processing replicas listen to the simulator control stream (SSE).
* When a replica receives a `SHUTDOWN` command, it terminates.
* The broker continues sending data to remaining replicas.
* The system continues operating in degraded mode.

---

## Event Classification Rules

Events are classified based on dominant frequency:

* **Earthquake:** 0.5 ≤ f < 3.0 Hz
* **Conventional explosion:** 3.0 ≤ f < 8.0 Hz
* **Nuclear-like event:** f ≥ 8.0 Hz

Frequencies below 0.5 Hz are ignored.

---

## Duplicate-Safe Persistence

* Each event is assigned a deterministic `event_id`
* Events are stored using `ON CONFLICT DO NOTHING`
* Additional in-memory deduplication avoids repeated detections

---

## Real-Time Dashboard

The dashboard provides:

* Event visualization
* Filtering (sensor, type, region)
* Periodic updates (REST polling)
* System status monitoring (replica health)

---

## Notes for Evaluation

* The system is fully reproducible via Docker Compose
* No manual setup is required after startup
* All services start automatically
* Controlled event injection can be performed via simulator APIs

