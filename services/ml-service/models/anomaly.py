import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Any
from models.base import AbstractBaseModel

class ZScoreAnomalyDetector(AbstractBaseModel):
    """
    Statistical Z-Score Anomaly Detector.
    Fast & low-latency for detecting sudden extreme telemetry spikes.
    """
    def __init__(self, threshold: float = 3.0):
        self.threshold = threshold

    def train(self, data: List[float]) -> None:
        pass  # Statis / Rule-based

    def predict(self, value: float, history: List[float]) -> Dict[str, Any]:
        if not history or len(history) < 3:
            return {"is_anomaly": False, "score": 0.0, "reason": "Insufficient history data"}
        
        mean = float(np.mean(history))
        std = float(np.std(history))

        if std == 0:
            is_anomaly = value != mean
            return {"is_anomaly": is_anomaly, "score": 0.0 if not is_anomaly else 5.0, "reason": "Zero variance history"}

        z_score = abs((value - mean) / std)
        is_anomaly = z_score > self.threshold

        return {
            "is_anomaly": is_anomaly,
            "z_score": round(z_score, 2),
            "mean": round(mean, 2),
            "std": round(std, 2),
            "reason": f"Z-Score ({round(z_score, 2)}) exceeded threshold ({self.threshold})" if is_anomaly else "Normal"
        }

class IsolationForestAnomalyDetector(AbstractBaseModel):
    """
    Machine Learning Isolation Forest Anomaly Detector.
    Unsupervised ML model for non-linear multivariate anomaly detection.
    """
    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.is_trained = False

    def train(self, data: List[float]) -> None:
        if len(data) < 10:
            print("[WARN] Need at least 10 data points to train Isolation Forest")
            return
        
        X = np.array(data).reshape(-1, 1)
        self.model.fit(X)
        self.is_trained = True

    def predict(self, value: float) -> Dict[str, Any]:
        if not self.is_trained:
            return {"is_anomaly": False, "reason": "Model not trained yet"}
        
        X = np.array([[value]])
        pred = self.model.predict(X)[0] # -1 for anomaly, 1 for normal
        score = self.model.decision_function(X)[0]

        is_anomaly = (pred == -1)
        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": round(float(score), 4),
            "reason": "Isolation Forest flagged pattern anomaly" if is_anomaly else "Normal"
        }
