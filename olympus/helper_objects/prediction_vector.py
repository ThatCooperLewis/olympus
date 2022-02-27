import uuid


class PredictionVector:

    # Simple solution for useful queue objects
    # Composes the Hermes order queue
    def __init__(self, weight, predictions, timestamp):
        self.weight: float = weight
        self.prediction_history: list = predictions
        self.timestamp: int = timestamp
        self.uuid: str = uuid.uuid4().hex