import numpy as np
from typing import List, Dict, Any, Optional
from models.base import AbstractBaseModel

class DeviceHealthEvaluator(AbstractBaseModel):
    """
    Device Health Index (DHI) Evaluation Engine.
    Calculates a overall health score (0% - 100%) for a device/sensor based on:
    1. Stability / Noise Variance Penalty
    2. Anomaly Frequency Penalty
    3. Operational Threshold Deviation Penalty
    """
    def __init__(self):
        pass

    def train(self, data: Any) -> None:
        pass  # Heuristic & Statistical Scoring Engine

    def predict(self, input_data: Any) -> Dict[str, Any]:
        """Satisfaction of AbstractBaseModel interface"""
        if isinstance(input_data, dict):
            return self.evaluate_health(
                history_values=input_data.get("history_values", []),
                recent_anomalies_count=input_data.get("recent_anomalies_count", 0),
                normal_min=input_data.get("normal_min"),
                normal_max=input_data.get("normal_max")
            )
        return self.evaluate_health(history_values=input_data if isinstance(input_data, list) else [])

    def evaluate_health(
        self,
        history_values: List[float],
        recent_anomalies_count: int = 0,
        normal_min: Optional[float] = None,
        normal_max: Optional[float] = None
    ) -> Dict[str, Any]:
        if not history_values or len(history_values) < 3:
            return {
                "health_score": 100,
                "health_status": "Healthy",
                "status_color": "green",
                "penalties": {
                    "variance_penalty": 0,
                    "anomaly_penalty": 0,
                    "threshold_penalty": 0
                },
                "message": "Data histori belum cukup untuk analisis degradasi (default 100%)"
            }

        base_score = 100.0
        data = np.array(history_values)

        # 1. Variance / Noise Penalty (Makin acak/fluktuatif, kesehatan berkurang)
        std_dev = float(np.std(data))
        mean_val = float(np.mean(data))
        cv = (std_dev / abs(mean_val)) if mean_val != 0 else 0.0  # Coefficient of Variation
        variance_penalty = min(cv * 30.0, 25.0)  # Max penalty 25 points

        # 2. Anomaly Frequency Penalty (Makin sering anomali terjadi, kesehatan berkurang pesat)
        anomaly_penalty = min(recent_anomalies_count * 15.0, 40.0)  # Max penalty 40 points

        # 3. Threshold Out-of-Bound Penalty (Deviasi dari batas normal pabrikan)
        threshold_penalty = 0.0
        if normal_min is not None or normal_max is not None:
            out_of_bound_count = 0
            for val in data:
                if normal_min is not None and val < normal_min:
                    out_of_bound_count += 1
                elif normal_max is not None and val > normal_max:
                    out_of_bound_count += 1
            
            violation_ratio = out_of_bound_count / len(data)
            threshold_penalty = violation_ratio * 35.0  # Max penalty 35 points

        # Hitung skor kesehatan akhir
        total_penalty = variance_penalty + anomaly_penalty + threshold_penalty
        final_score = max(round(base_score - total_penalty, 1), 0.0)

        # Penentuan Status Kesehatan & Warna UI Dashboard
        if final_score >= 85.0:
            health_status = "Healthy"
            status_color = "green"
            recommendation = "Perangkat berjalan sangat stabil dalam kondisi optimal."
        elif final_score >= 65.0:
            health_status = "Warning / Degradation"
            status_color = "yellow"
            recommendation = "Terdeteksi fluktuasi/anomali minor. Disarankan pemantauan berkala."
        else:
            health_status = "Critical / High Failure Risk"
            status_color = "red"
            recommendation = "Kondisi perangkat kritis! Diperlukan pemeriksaan teknisi secara langsung."

        return {
            "health_score": final_score,
            "health_status": health_status,
            "status_color": status_color,
            "recommendation": recommendation,
            "metrics_breakdown": {
                "std_deviation": round(std_dev, 2),
                "anomaly_count_24h": recent_anomalies_count,
                "penalties": {
                    "variance_penalty": round(variance_penalty, 1),
                    "anomaly_penalty": round(anomaly_penalty, 1),
                    "threshold_penalty": round(threshold_penalty, 1)
                }
            }
        }
