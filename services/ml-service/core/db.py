import psycopg2
from psycopg2.extras import RealDictCursor
from config import config

def get_db_connection():
    try:
        conn = psycopg2.connect(config.DATABASE_URL)
        return conn
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return None

def fetch_sensor_telemetry_history(sensor_id: int, limit: int = 100):
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT time, value 
                FROM telemetry_data 
                WHERE sensor_id = %s 
                ORDER BY time DESC 
                LIMIT %s;
            """
            cursor.execute(query, (sensor_id, limit))
            records = cursor.fetchall()
            return records
    except Exception as e:
        print(f"[ERROR] Fetch telemetry error: {e}")
        return []
    finally:
        conn.close()
