import uuid
from utils.config import PREDICTION_DELTA_THRESHOLD as DELTA

class PredictionVector:

    # Simple solution for useful queue objects
    # Composes the Hermes order queue
    def __init__(self, weight, predictions, timestamp):
        self.weight: float = weight
        self.percent: float =  round((weight*DELTA*100), 4)
        self.prediction_history: list = predictions
        self.timestamp: int = timestamp
        self.uuid: str = uuid.uuid4().hex