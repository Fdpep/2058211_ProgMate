#configurazione da dockercompose

import os


DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "seismicdb")
DB_USER = os.getenv("DB_USER", "seismic_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "seismic_password")

REPLICA_ID = os.getenv("REPLICA_ID", "processing-unknown")

SAMPLING_RATE_HZ = float(os.getenv("SAMPLING_RATE_HZ", "20.0"))
WINDOW_SIZE_SECONDS = int(os.getenv("WINDOW_SIZE_SECONDS", "5"))
WINDOW_SIZE_SAMPLES = int(SAMPLING_RATE_HZ * WINDOW_SIZE_SECONDS)