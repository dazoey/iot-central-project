import numpy as np
from typing import List, Dict, Any
from models.base import AbstractBaseModel

class TelemetryForecaster(AbstractBaseModel):
    """
    Time-Series Forecasting Model using Holt's Exponential Smoothing & Linear Trend Projection.
    Predicts future N values based on historical telemetry trend & momentum.
    """
    def __init__(self, alpha: float = 0.3, beta: float = 0.1):
        self.alpha = alpha
        self.beta = beta

    def train(self, data: List[float]) -> None:
        pass  # Online adaptive model

    def predict(self, history: List[float], steps_ahead: int = 5) -> Dict[str, Any]:
        if not history or len(history) < 3:
            return {
                "forecast_values": [],
                "trend": "unknown",
                "message": "Data historis tidak cukup untuk membuat prediksi (minimal 3 data point)"
            }

        # Urutkan dari data terlama ke terbaru (kronologis)
        data = list(reversed(history))
        n = len(data)

        # Inisialisasi Holt's Linear Trend
        level = data[0]
        trend = data[1] - data[0]

        for i in range(1, n):
            val = data[i]
            last_level = level
            level = self.alpha * val + (1 - self.alpha) * (level + trend)
            trend = self.beta * (level - last_level) + (1 - self.beta) * trend

        # Proyeksi ke depan N langkah
        forecasts = []
        for h in range(1, steps_ahead + 1):
            pred_val = level + (h * trend)
            forecasts.append(round(float(pred_val), 2))

        # Penentuan arah tren
        trend_direction = "stable"
        if trend > 0.05:
            trend_direction = "increasing"
        elif trend < -0.05:
            trend_direction = "decreasing"

        return {
            "forecast_values": forecasts,
            "steps_ahead": steps_ahead,
            "trend_direction": trend_direction,
            "trend_velocity": round(float(trend), 4),
            "last_known_value": round(float(data[-1]), 2)
        }
