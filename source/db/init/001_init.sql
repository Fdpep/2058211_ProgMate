CREATE TABLE IF NOT EXISTS detected_events (
    event_id VARCHAR(128) PRIMARY KEY,
    sensor_id VARCHAR(64) NOT NULL,
    sensor_name VARCHAR(128) NOT NULL,
    sensor_region VARCHAR(128) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    dominant_frequency_hz DOUBLE PRECISION NOT NULL,
    peak_amplitude DOUBLE PRECISION NOT NULL,
    window_start TIMESTAMPTZ NOT NULL,
    window_end TIMESTAMPTZ NOT NULL,
    detected_at TIMESTAMPTZ NOT NULL,
    replica_id VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);