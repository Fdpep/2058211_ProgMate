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

ANALYSIS_STRIDE_SAMPLES = int(os.getenv("ANALYSIS_STRIDE_SAMPLES", "10"))

EVENT_DEDUP_COOLDOWN_SECONDS = int(
    os.getenv("EVENT_DEDUP_COOLDOWN_SECONDS", "12")
)

MIN_CLASSIFIABLE_PEAK_MAGNITUDE = float(
    os.getenv("MIN_CLASSIFIABLE_PEAK_MAGNITUDE", "1.2")
)

MIN_CLASSIFIABLE_FREQUENCY_HZ = float(os.getenv("MIN_CLASSIFIABLE_FREQUENCY_HZ", "0.5"))
LOG_NON_EVENT_WINDOWS = os.getenv("LOG_NON_EVENT_WINDOWS", "false").lower() == "true"