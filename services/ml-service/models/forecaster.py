import numpy as np
from typing import List, Dict, Any, Optional
from models.base import AbstractBaseModel

class TelemetryForecaster(AbstractBaseModel):
    """
    Time-Series Forecasting Model using Holt's Exponential Smoothing & Linear Trend Projection.
    Features:
    - N-step future value projection
    - Time-to-Threshold-Violation (TTV) estimation
    - Prediction Confidence Intervals (Upper & Lower Bounds, 95% CI)
    """
    def __init__(self, alpha: float = 0.3, beta: float = 0.1):
        self.alpha = alpha
        self.beta = beta

    def train(self, data: List[float]) -> None:
        pass  # Online adaptive model

    def predict(
        self, 
        history: List[float], 
        steps_ahead: int = 5, 
        critical_threshold: Optional[float] = None,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        if not history or len(history) < 3:
            return {
                "forecast_values": [],
                "confidence_intervals": [],
                "trend_direction": "unknown",
                "message": "Data historis tidak cukup untuk membuat prediksi (minimal 3 data point)"
            }

        # Urutkan dari data terlama ke terbaru (kronologis)
        data = list(reversed(history))
        n = len(data)

        # Inisialisasi Holt's Linear Trend & Error Tracking
        level = data[0]
        trend = data[1] - data[0]
        residuals = []

        for i in range(1, n):
            val = data[i]
            pred_in_sample = level + trend
            residuals.append(val - pred_in_sample)

            last_level = level
            level = self.alpha * val + (1 - self.alpha) * (level + trend)
            trend = self.beta * (level - last_level) + (1 - self.beta) * trend

        # Standar Deviasi Residual Errors (Root Mean Squared Error / Residual Std)
        residual_std = float(np.std(residuals)) if len(residuals) > 1 else 0.5
        if residual_std == 0:
            residual_std = 0.1

        # Z-factor untuk 95% Confidence Interval (1.96)
        z_factor = 1.96 if confidence_level == 0.95 else 1.645

        # Proyeksi ke depan N langkah beserta Confidence Intervals (Upper & Lower Bounds)
        forecasts = []
        confidence_intervals = []

        for h in range(1, steps_ahead + 1):
            pred_val = level + (h * trend)
            
            # Margin of Error meningkat seiring makin jauh langkah proyeksi h (fanning out effect)
            margin_of_error = z_factor * residual_std * np.sqrt(h)

            upper_bound = round(float(pred_val + margin_of_error), 2)
            lower_bound = round(float(pred_val - margin_of_error), 2)
            pred_rounded = round(float(pred_val), 2)

            forecasts.append(pred_rounded)
            confidence_intervals.append({
                "step": h,
                "predicted_value": pred_rounded,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "margin_of_error": round(float(margin_of_error), 2)
            })

        # Penentuan arah tren
        trend_direction = "stable"
        if trend > 0.05:
            trend_direction = "increasing"
        elif trend < -0.05:
            trend_direction = "decreasing"

        # --- SUB-FITUR 1: Time-to-Threshold-Violation (TTV) ---
        ttv_info = None
        if critical_threshold is not None:
            last_val = data[-1]
            
            # Kasus 1: Nilai saat ini SUDAH menembus batas kritis
            if (trend >= 0 and last_val >= critical_threshold) or (trend < 0 and last_val <= critical_threshold):
                ttv_info = {
                    "is_violating": True,
                    "will_violate": True,
                    "estimated_steps_to_violation": 0,
                    "critical_threshold": critical_threshold,
                    "warning_message": f"Kritis: Nilai saat ini ({last_val}) sudah melampaui batas kritis ({critical_threshold})!"
                }
            # Kasus 2: Tren naik menuju batas atas kritis
            elif trend > 0.001 and last_val < critical_threshold:
                steps_needed = (critical_threshold - last_val) / trend
                ttv_info = {
                    "is_violating": False,
                    "will_violate": True,
                    "estimated_steps_to_violation": round(float(steps_needed), 1),
                    "critical_threshold": critical_threshold,
                    "warning_message": f"Peringatan: Diprediksi menembus batas kritis ({critical_threshold}) dalam ~{round(float(steps_needed), 1)} interval ke depan."
                }
            # Kasus 3: Tren turun menuju batas bawah kritis
            elif trend < -0.001 and last_val > critical_threshold:
                steps_needed = (last_val - critical_threshold) / abs(trend)
                ttv_info = {
                    "is_violating": False,
                    "will_violate": True,
                    "estimated_steps_to_violation": round(float(steps_needed), 1),
                    "critical_threshold": critical_threshold,
                    "warning_message": f"Peringatan: Diprediksi menembus batas bawah kritis ({critical_threshold}) dalam ~{round(float(steps_needed), 1)} interval ke depan."
                }
            else:
                ttv_info = {
                    "is_violating": False,
                    "will_violate": False,
                    "estimated_steps_to_violation": None,
                    "critical_threshold": critical_threshold,
                    "warning_message": "Aman: Tren stabil atau bergerak menjauhi batas kritis."
                }

        return {
            "forecast_values": forecasts,
            "confidence_intervals": confidence_intervals,
            "confidence_level": f"{int(confidence_level * 100)}%",
            "steps_ahead": steps_ahead,
            "trend_direction": trend_direction,
            "trend_velocity": round(float(trend), 4),
            "last_known_value": round(float(data[-1]), 2),
            "threshold_violation_analysis": ttv_info
        }
