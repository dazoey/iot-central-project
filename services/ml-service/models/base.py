from abc import ABC, abstractmethod
from typing import Any, Dict

class AbstractBaseModel(ABC):
    """
    Abstract Base Class for all ML Models in IoT Central.
    Ensures future models (LSTM, XGBoost, Autoencoders) follow a standard interface.
    """

    @abstractmethod
    def train(self, data: Any) -> None:
        """Train the model with historical data."""
        pass

    @abstractmethod
    def predict(self, input_data: Any) -> Dict[str, Any]:
        """Perform inference on input data."""
        pass
