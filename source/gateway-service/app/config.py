import os


DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "seismicdb")
DB_USER = os.getenv("DB_USER", "seismic_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "seismic_password")

PROCESSING_REPLICAS = [
    os.getenv("PROCESSING_REPLICA_1", "http://processing-1:8100"),
    os.getenv("PROCESSING_REPLICA_2", "http://processing-2:8100"),
    os.getenv("PROCESSING_REPLICA_3", "http://processing-3:8100"),
]