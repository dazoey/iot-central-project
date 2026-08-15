from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from config import config
from models.anomaly import ZScoreAnomalyDetector, IsolationForestAnomalyDetector
from models.llm_advisor import LLMAdvisor
from core.db import fetch_sensor_telemetry_history

app = FastAPI(
    title=config.SERVICE_NAME,
    version="1.0.0",
    description="Microservice Machine Learning & AI Diagnostics untuk IoT Central System"
)

# Inisialisasi Model ML & LLM Advisor
z_detector = ZScoreAnomalyDetector(threshold=config.ZSCORE_THRESHOLD)
iso_detector = IsolationForestAnomalyDetector()
llm_advisor = LLMAdvisor()

# Pydantic Schemas
class TelemetryCheckRequest(BaseModel):
    sensor_id: int
    device_name: str
    sensor_name: str
    value: float
    unit: str
    history_values: Optional[List[float]] = []

class AnomalyCheckResponse(BaseModel):
    is_anomaly: bool
    method_used: str
    details: dict
    ai_recommendation: Optional[dict] = None

@app.get("/")
def read_root():
    return {"service": config.SERVICE_NAME, "status": "running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/v1/ml/detect-anomaly", response_model=AnomalyCheckResponse)
def detect_anomaly(req: TelemetryCheckRequest):
    """
    Menjalankan deteksi anomali telemetri sensor menggunakan Z-Score / Isolation Forest
    dan memberikan analisis AI LLM jika terdeteksi anomali.
    """
    history = req.history_values

    # Jika history tidak dikirim di body, ambil otomatis dari TimescaleDB
    if not history:
        db_records = fetch_sensor_telemetry_history(req.sensor_id, limit=50)
        history = [r["value"] for r in db_records]

    # Run Z-Score Detection
    res = z_detector.predict(req.value, history)

    ai_advice = None
    if res["is_anomaly"]:
        # Panggil LLM Advisor jika ada anomali
        ai_advice = llm_advisor.explain_anomaly(
            device_name=req.device_name,
            sensor_name=req.sensor_name,
            value=req.value,
            unit=req.unit,
            reason=res["reason"]
        )

    return {
        "is_anomaly": res["is_anomaly"],
        "method_used": "Z-Score Statistical Model",
        "details": res,
        "ai_recommendation": ai_advice
    }

@app.post("/api/v1/ml/train-isolation-forest")
def train_isolation_forest(sensor_id: int = Query(...)):
    """
    Melatih model Isolation Forest berdasarkan histori telemetri sensor dari TimescaleDB.
    """
    db_records = fetch_sensor_telemetry_history(sensor_id, limit=200)
    if not db_records:
        raise HTTPException(status_code=400, detail="Data telemetri di DB tidak cukup untuk latihan model.")
    
    values = [r["value"] for r in db_records]
    iso_detector.train(values)

    return {
        "message": f"Isolation Forest berhasil dilatih untuk Sensor ID {sensor_id}",
        "data_points_used": len(values)
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)
