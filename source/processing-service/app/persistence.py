import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor

from app.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )


def generate_event_id(
    sensor_id: str,
    event_type: str,
    window_start: str,
    window_end: str,
    dominant_frequency_hz: float
) -> str:
    base_string = (
        f"{sensor_id}|{event_type}|{window_start}|{window_end}|"
        f"{dominant_frequency_hz:.2f}"
    )
    return hashlib.sha256(base_string.encode("utf-8")).hexdigest()


def save_event(event: dict) -> bool:
    query = """
    INSERT INTO detected_events (
        event_id,
        sensor_id,
        sensor_name,
        sensor_region,
        event_type,
        dominant_frequency_hz,
        peak_amplitude,
        window_start,
        window_end,
        detected_at,
        replica_id
    )
    VALUES (
        %(event_id)s,
        %(sensor_id)s,
        %(sensor_name)s,
        %(sensor_region)s,
        %(event_type)s,
        %(dominant_frequency_hz)s,
        %(peak_amplitude)s,
        %(window_start)s,
        %(window_end)s,
        %(detected_at)s,
        %(replica_id)s
    )
    ON CONFLICT (event_id) DO NOTHING;
    """

    connection = get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query, event)
                return cursor.rowcount == 1
    finally:
        connection.close()