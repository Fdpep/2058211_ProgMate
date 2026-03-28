# Seismic Surveillance Platform

## Project overview

This project implements a distributed and fault-tolerant seismic analysis platform based on the simulator provided for the April 2026 hackathon.

The system ingests real-time seismic measurements, redistributes them across replicated processing services, performs frequency-domain analysis, classifies events, persists them with duplicate-safe behavior, and exposes a real-time dashboard.

## Repository structure

- `input.md`: system overview, user stories, event schema, and rule model
- `Student_doc.md`: technical and deployment documentation
- `source/`: application source code, Dockerfiles, Docker Compose configuration, and infrastructure files
- `booklets/`: slides, mockups, and additional project material

## Planned architecture

The platform is composed of the following services:

- simulator
- broker-service
- processing-service
- gateway-service
- frontend-dashboard
- postgres database

## Execution

The full system will be executable with:

```bash
docker compose up
from the source/ directory after implementation is completed.