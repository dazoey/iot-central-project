import numpy as np
from typing import List, Dict, Any, Optional
from models.base import AbstractBaseModel

class RULPredictor(AbstractBaseModel):
    """
    Remaining Useful Life (RUL) Prediction Engine.
    Estimates remaining operational life (in days & hours) for a device/sensor based on:
    1. Historical Degradation Velocity Slope (Linear Polyfit)
    2. Non-linear Exponential Acceleration Penalty (Accelerated Wear & Tear)
    3. Health Margin & Failure Thresholds
    """
    def __init__(self):
        pass

    def train(self, data: Any) -> None:
        pass  # Adaptive Linear/Exponential Degradation Model

    def predict(self, input_data: Any) -> Dict[str, Any]:
        if isinstance(input_data, dict):
            return self.estimate_rul(
                health_score_history=input_data.get("health_score_history", []),
                current_health_score=input_data.get("current_health_score", 100.0),
                expected_lifespan_days=input_data.get("expected_lifespan_days", 365.0),
                failure_threshold_score=input_data.get("failure_threshold_score", 20.0),
                interval_hours=input_data.get("interval_hours", 24.0)
            )
        return self.estimate_rul(health_score_history=input_data if isinstance(input_data, list) else [])

    def estimate_rul(
        self,
        health_score_history: List[float],
        current_health_score: float = 100.0,
        expected_lifespan_days: float = 365.0,
        failure_threshold_score: float = 20.0,
        interval_hours: float = 24.0
    ) -> Dict[str, Any]:
        """
        Estimasi Sisa Usia Pakai (RUL) dengan Penanganan Degradasi Akselerasi.
        """
        if current_health_score <= failure_threshold_score:
            return {
                "rul_days": 0.0,
                "rul_hours": 0.0,
                "health_degradation_rate_per_day": 0.0,
                "status": "EXPIRED_OR_FAILED",
                "maintenance_urgency": "IMMEDIATE_ACTION_REQUIRED",
                "recommendation": f"Perangkat telah menyentuh/melewati batas kegagalan ({failure_threshold_score}%). Segera lakukan pergantian/perbaikan komponen!",
                "estimated_failure_date_notice": "Telah Kedaluwarsa"
            }

        degradation_rate_per_hour = 0.0
        acceleration_factor = 1.0

        if len(health_score_history) >= 2:
            # Urutkan kronologis (terlama ke terbaru)
            scores = list(reversed(health_score_history))
            x = np.arange(len(scores)) * interval_hours
            y = np.array(scores)

            # Fit linear slope (dS / dt)
            if len(scores) > 1:
                slope, _ = np.polyfit(x, y, 1)  # slope dalam poin kesehatan per jam
                if slope < 0:
                    degradation_rate_per_hour = abs(slope)

            # Deteksi Akselerasi Degradasi (Jika degradasi makin cepat di data terbaru)
            if len(scores) >= 4:
                recent_drop = scores[-2] - scores[-1]
                earlier_drop = scores[0] - scores[1]
                if recent_drop > earlier_drop and earlier_drop > 0:
                    acceleration_factor = min(recent_drop / earlier_drop, 2.5)

        # Jika belum ada penurunan nyata, gunakan laju degradasi teoritis berbasis expected_lifespan_days
        if degradation_rate_per_hour == 0.0:
            total_hours = expected_lifespan_days * 24.0
            degradation_rate_per_hour = (100.0 - failure_threshold_score) / total_hours

        # Aplikasikan faktor akselerasi ke laju degradasi
        effective_degradation_rate_per_hour = degradation_rate_per_hour * acceleration_factor

        # Hitung sisa jam & hari
        health_margin = current_health_score - failure_threshold_score
        estimated_rul_hours = health_margin / effective_degradation_rate_per_hour
        estimated_rul_days = estimated_rul_hours / 24.0

        degradation_rate_per_day = effective_degradation_rate_per_hour * 24.0

        # Urgensi Pemeliharaan & Status
        if estimated_rul_days <= 7.0:
            urgency = "HIGH_CRITICAL"
            status = "NEARING_FAILURE"
            rec = "Jadwalkan pergantian/perbaikan komponen dalam minggu ini."
        elif estimated_rul_days <= 30.0:
            urgency = "MEDIUM_WARNING"
            status = "DEGRADING"
            rec = "Persiapkan suku cadang dan tentukan jadwal perawatan rutin bulan ini."
        else:
            urgency = "LOW_NORMAL"
            status = "HEALTHY_OPERATIONAL"
            rec = "Perangkat beroperasi dalam kondisi wajar tanpa perlu perawatan darurat."

        return {
            "rul_days": round(float(estimated_rul_days), 1),
            "rul_hours": round(float(estimated_rul_hours), 1),
            "health_degradation_rate_per_day": round(float(degradation_rate_per_day), 3),
            "acceleration_factor": round(float(acceleration_factor), 2),
            "current_health_score": round(float(current_health_score), 1),
            "failure_threshold_score": round(float(failure_threshold_score), 1),
            "status": status,
            "maintenance_urgency": urgency,
            "recommendation": rec
        }
