from queue import Queue
from utils import Logger
class PredictionVector:

    # Simple solution for useful queue objects
    # Composes the Hermes order queue
    def __init__(self, weight, predictions, timestamp):
        self.weight = weight
        self.prediction_history = predictions
        self.timestamp = timestamp


class PredictionQueue:

    # Hermes queue, populated by Delphi, kept separate so Hermes isn't a dependency
    def __init__(self, queue=None):
        '''
        Initialize the queue, either with a pre-existing queue or a new one
        '''
        self.log = Logger.setup(self.__class__.__name__)
        if queue:
            self.__queue: Queue = queue
        else:
            self.__queue: Queue = Queue()

    def put(self, prediction_vector: PredictionVector):
        if type(prediction_vector) is not PredictionVector:
            self.log.error('Tried to submit non-PredictionVector to queue')
            raise Exception("What's up guy? Bad type submitted to prediction queue!")
        self.__queue.put(prediction_vector)

    def get(self):
        return self.__queue.get()
    
    @property
    def size(self):
        return self.__queue.qsize()
