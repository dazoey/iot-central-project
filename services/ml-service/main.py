from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from config import config
from models.anomaly import ZScoreAnomalyDetector, IsolationForestAnomalyDetector
from models.llm_advisor import LLMAdvisor
from core.db import fetch_sensor_telemetry_history
from core.scheduler import AutoRetrainingPipeline

app = FastAPI(
    title=config.SERVICE_NAME,
    version="1.0.0",
    description="Microservice Machine Learning & AI Diagnostics untuk IoT Central System"
)

# Inisialisasi Model ML, LLM Advisor, & Auto-Retraining Pipeline
z_detector = ZScoreAnomalyDetector(threshold=config.ZSCORE_THRESHOLD)
iso_detector = IsolationForestAnomalyDetector()
llm_advisor = LLMAdvisor()
retrain_pipeline = AutoRetrainingPipeline(iso_detector)

@app.on_event("startup")
def startup_event():
    # Jalankan scheduler otomatis setiap 24 jam di latar belakang
    retrain_pipeline.start_scheduler(interval_hours=24)

@app.on_event("shutdown")
def shutdown_event():
    retrain_pipeline.stop_scheduler()

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

@app.post("/api/v1/ml/trigger-auto-retrain")
def trigger_auto_retrain():
    """
    Pemicu manual untuk menjalankan siklus Auto-Retraining ML Pipeline secara instan.
    """
    retrain_pipeline.retrain_all_models()
    return {"message": "Siklus Auto-Retraining ML Pipeline telah berhasil dipicu di latar belakang."}

class ForecastRequest(BaseModel):
    sensor_id: int
    steps_ahead: Optional[int] = 5
    critical_threshold: Optional[float] = None
    lower_critical_threshold: Optional[float] = None
    history_values: Optional[List[float]] = []

@app.post("/api/v1/ml/predict-telemetry")
def predict_telemetry(req: ForecastRequest):
    """
    Memprediksi tren & nilai telemetri sensor N langkah ke depan (Forecasting)
    serta menghitung Estimasi Waktu Mencapai Batas Kritis (TTV) & 95% Confidence Intervals.
    """
    from models.forecaster import TelemetryForecaster
    forecaster = TelemetryForecaster()

    history = req.history_values
    if not history:
        db_records = fetch_sensor_telemetry_history(req.sensor_id, limit=50)
        history = [r["value"] for r in db_records]

    forecast_res = forecaster.predict(
        history=history, 
        steps_ahead=req.steps_ahead,
        critical_threshold=req.critical_threshold,
        lower_critical_threshold=req.lower_critical_threshold
    )
    return forecast_res

class HealthEvaluationRequest(BaseModel):
    sensor_id: int
    recent_anomalies_count: Optional[int] = 0
    normal_min: Optional[float] = None
    normal_max: Optional[float] = None
    history_values: Optional[List[float]] = []

@app.post("/api/v1/ml/device-health")
def evaluate_device_health(req: HealthEvaluationRequest):
    """
    Menghitung skor kesehatan perangkat / Device Health Index (0% - 100%).
    """
    from models.health_evaluator import DeviceHealthEvaluator
    evaluator = DeviceHealthEvaluator()

    history = req.history_values
    if not history:
        db_records = fetch_sensor_telemetry_history(req.sensor_id, limit=100)
        history = [r["value"] for r in db_records]

    health_res = evaluator.evaluate_health(
        history_values=history,
        recent_anomalies_count=req.recent_anomalies_count,
        normal_min=req.normal_min,
        normal_max=req.normal_max
    )
    return health_res

class RULEvaluationRequest(BaseModel):
    sensor_id: int
    health_score_history: Optional[List[float]] = []
    current_health_score: Optional[float] = 100.0
    expected_lifespan_days: Optional[float] = 365.0
    failure_threshold_score: Optional[float] = 20.0
    interval_hours: Optional[float] = 24.0

@app.post("/api/v1/ml/predict-rul")
def predict_rul(req: RULEvaluationRequest):
    """
    Memprediksi Sisa Usia Pakai / Remaining Useful Life (RUL) perangkat dalam hari/jam.
    """
    from models.rul_predictor import RULPredictor
    predictor = RULPredictor()

    rul_res = predictor.estimate_rul(
        health_score_history=req.health_score_history,
        current_health_score=req.current_health_score,
        expected_lifespan_days=req.expected_lifespan_days,
        failure_threshold_score=req.failure_threshold_score,
        interval_hours=req.interval_hours
    )
    return rul_res

class MaintenanceScheduleRequest(BaseModel):
    sensor_id: int
    device_name: Optional[str] = "Device"
    sensor_name: Optional[str] = "Sensor"
    health_score: Optional[float] = 100.0
    rul_days: Optional[float] = 365.0
    recent_anomalies_count: Optional[int] = 0
    trend_direction: Optional[str] = "stable"

@app.post("/api/v1/ml/schedule-maintenance")
def schedule_maintenance(req: MaintenanceScheduleRequest):
    """
    Menghasilkan rekomendasi jadwal pemeliharaan & Work Order teknis otomatis.
    """
    from models.maintenance_scheduler import MaintenanceScheduler
    scheduler = MaintenanceScheduler()

    schedule_res = scheduler.generate_recommendation(
        health_score=req.health_score,
        rul_days=req.rul_days,
        recent_anomalies_count=req.recent_anomalies_count,
        trend_direction=req.trend_direction,
        device_name=req.device_name,
        sensor_name=req.sensor_name
    )
    return schedule_res

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=config.PORT, reload=True)
