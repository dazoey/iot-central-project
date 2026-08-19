import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from models.base import AbstractBaseModel

class MaintenanceScheduler(AbstractBaseModel):
    """
    Auto Maintenance Recommender & Scheduler Engine.
    Combines Device Health Index, RUL Prediction, Anomaly Frequency, and Telemetry Trends
    to generate structured Work Orders and recommended maintenance dates.
    """
    def __init__(self):
        pass

    def train(self, data: Any) -> None:
        pass  # Decision Matrix Engine

    def predict(self, input_data: Any) -> Dict[str, Any]:
        if isinstance(input_data, dict):
            return self.generate_recommendation(
                health_score=input_data.get("health_score", 100.0),
                rul_days=input_data.get("rul_days", 365.0),
                recent_anomalies_count=input_data.get("recent_anomalies_count", 0),
                trend_direction=input_data.get("trend_direction", "stable"),
                device_name=input_data.get("device_name", "Device"),
                sensor_name=input_data.get("sensor_name", "Sensor")
            )
        return self.generate_recommendation(100.0, 365.0, 0, "stable", "Device", "Sensor")

    def generate_recommendation(
        self,
        health_score: float,
        rul_days: float,
        recent_anomalies_count: int = 0,
        trend_direction: str = "stable",
        device_name: str = "Device",
        sensor_name: str = "Sensor"
    ) -> Dict[str, Any]:
        now = datetime.now()

        # Decision Matrix untuk Menentukan Tanggal & Jenis Maintenance
        if health_score < 50.0 or rul_days <= 3.0 or recent_anomalies_count >= 5:
            priority = "URGENT"
            days_until_maintenance = 1
            maintenance_type = "COMPONENT_REPLACEMENT"
            action_title = "Pergantian Komponen Darurat"
            description = f"Skor kesehatan sangat rendah ({health_score}%) atau RUL tinggal {rul_days} hari dengan frekuensi anomali tinggi. Komponen sensor disarankan segera diganti."

        elif health_score < 70.0 or rul_days <= 14.0 or recent_anomalies_count >= 2:
            priority = "HIGH"
            days_until_maintenance = min(max(int(rul_days / 2), 2), 7)
            maintenance_type = "CORRECTIVE_CALIBRATION"
            action_title = "Kalibrasi & Perbaikan Korektif"
            description = f"Terdeteksi pemudaran kinerja ({health_score}%) dan deviasi tren ({trend_direction}). Jadwalkan inspeksi teknisi dan kalibrasi ulang sensor."

        elif health_score < 85.0 or rul_days <= 45.0:
            priority = "MEDIUM"
            days_until_maintenance = min(max(int(rul_days / 3), 7), 21)
            maintenance_type = "PREVENTIVE_INSPECTION"
            action_title = "Pemeriksaan Rutin Pencegahan"
            description = "Perangkat beroperasi lumayan stabil tetapi memerlukan pembersihan berkala dan cek fisik koneksi perkabelan."

        else:
            priority = "LOW"
            days_until_maintenance = min(int(rul_days / 2), 60)
            maintenance_type = "ROUTINE_AUDIT"
            action_title = "Audit Periodik Standar"
            description = "Sistem dalam kondisi prima. Tidak ada tindakan mendesak yang diperlukan."

        recommended_date = now + timedelta(days=days_until_maintenance)
        formatted_date = recommended_date.strftime("%Y-%m-%d")

        return {
            "device_name": device_name,
            "sensor_name": sensor_name,
            "priority_level": priority,
            "maintenance_type": maintenance_type,
            "recommended_maintenance_date": formatted_date,
            "days_until_maintenance": days_until_maintenance,
            "action_title": action_title,
            "suggested_work_order": {
                "work_order_id": f"WO-{now.strftime('%Y%m%d')}-{np.random.randint(100, 999)}",
                "title": f"Work Order [{priority}]: {action_title} ({device_name})",
                "summary": description,
                "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
                "scheduled_date": formatted_date
            }
        }
