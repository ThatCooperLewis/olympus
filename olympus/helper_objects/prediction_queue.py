from utils import Postgres, Logger
from utils.postgres import PostgresPredictionVector
import utils.config as constants
from olympus.helper_objects.prediction_vector import PredictionVector


class PredictionQueueDB:

    '''
    A queue-like object that interfaces with the pSQL database
    '''

    # Hermes queue, populated by Delphi, kept separate so Hermes isn't a dependency
    def __init__(self, override_postgres: Postgres = None):
        '''
        Initialize the queue, either with a pre-existing psql connection or a new one
        '''
        self.log = Logger.setup(self.__class__.__name__)
        self.postgres = override_postgres if override_postgres is not None else Postgres()

    def put(self, prediction_vector: PredictionVector):
        if type(prediction_vector) is not PredictionVector:
            self.log.error('Tried to submit non-PredictionVector to queue')
            raise Exception("What's up guy? Bad type submitted to prediction queue!")
        self.postgres.insert_prediction_vector(prediction_vector)

    def get(self) -> PostgresPredictionVector:
        """
        Pop the first prediction in the queue that is not being processed
        :return: A prediction object.
        """
        results = self.postgres.get_queued_predictions()
        if len(results) > 0:
            first_prediction = results[0]
            if first_prediction:
                self.postgres.update_prediction_status(first_prediction.uuid, constants.POSTGRES_STATUS_PROCESSING)
                return first_prediction
        return None
    
    def close(self, prediction_vector: PredictionVector):
        '''
        Set the DB status for a given prediction to 'COMPLETE'
        '''
        if type(prediction_vector) not in [PredictionVector, PostgresPredictionVector]:
            self.log.error('Tried to submit non-PredictionVector to queue')
            raise Exception("What's up guy? Bad type submitted to prediction queue!")
        self.postgres.update_prediction_status(prediction_vector.uuid, constants.POSTGRES_STATUS_COMPLETE)
        
    
    @property
    def size(self) -> int:
        result = self.postgres.get_queued_predictions()
        if type(result) is list:
            return len(result)
        return 0
