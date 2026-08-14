import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SERVICE_NAME = "IoT-ML-Service"
    PORT = int(os.getenv("PORT", 8000))
    
    # Database Settings
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:rootpassword@localhost:5432/iot_central_db"
    )
    
    # MQTT Broker Settings
    MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
    MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
    MQTT_TELEMETRY_TOPIC = "devices/+/telemetry"
    MQTT_ANOMALY_TOPIC = "alerts/anomalies"
    
    # LLM Settings (Google Gemini API)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Thresholds
    ZSCORE_THRESHOLD = float(os.getenv("ZSCORE_THRESHOLD", 3.0))

config = Config()
