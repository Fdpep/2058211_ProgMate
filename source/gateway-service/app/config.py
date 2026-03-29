import os


DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "seismicdb")
DB_USER = os.getenv("DB_USER", "seismic_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "seismic_password")