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


def check_database_connection() -> bool:
    connection = get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
        return True
    finally:
        connection.close()


def fetch_events(
    sensor_id=None,
    event_type=None,
    sensor_region=None,
    start_time=None,
    end_time=None,
    limit=50,
    offset=0,
):
    query = """
    SELECT
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
        replica_id,
        created_at
    FROM detected_events
    WHERE 1=1
    """
    params = []

    if sensor_id:
        query += " AND sensor_id = %s"
        params.append(sensor_id)

    if event_type:
        query += " AND event_type = %s"
        params.append(event_type)

    if sensor_region:
        query += " AND sensor_region = %s"
        params.append(sensor_region)

    if start_time:
        query += " AND detected_at >= %s"
        params.append(start_time)

    if end_time:
        query += " AND detected_at <= %s"
        params.append(end_time)

    query += " ORDER BY detected_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    connection = get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
    finally:
        connection.close()


def fetch_event_by_id(event_id: str):
    query = """
    SELECT
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
        replica_id,
        created_at
    FROM detected_events
    WHERE event_id = %s
    """

    connection = get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (event_id,))
                return cursor.fetchone()
    finally:
        connection.close()