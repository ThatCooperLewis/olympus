from queue import Queue
from threading import Thread
from time import time as now

from crosstower.socket_api import OrderListener, Trading
from olympus import Athena, Delphi, Hermes, PredictionQueue
from olympus.primordial_chaos import PrimordialChaos
from utils import Logger

# Constants

ATHENA_OUTPUT = 'run/athena.csv'
ATHENA_SCRAPE_INTERVAL_SECONDS = 5

TRADE_SYMBOL = 'BTCUSD'
H5_MODEL = 'run/model.h5'
PARAMS_JSON = 'run/params.json'
PREDICTION_ITERATIONS = 3
PREDICTION_QUEUE_MAX_SIZE = 5


class Zeus:

    '''
    Initialize and watch everything
    '''

    def __init__(self) -> None:
        self.abort = False
        self.log = Logger.setup(__name__)
        self.order_listener = OrderListener()
        self.trading_account = Trading()
        self.prediction_queue = PredictionQueue()
        self.athena = Athena(
            csv_path=ATHENA_OUTPUT,
            custom_symbol=TRADE_SYMBOL,
            custom_interval=ATHENA_SCRAPE_INTERVAL_SECONDS,
        )
        self.hermes = Hermes(
            override_orderListener=self.order_listener,
            override_tradingAccount=self.trading_account,
            override_predictionQueue=self.prediction_queue
        )
        self.delphi = Delphi(
            csv_path=ATHENA_OUTPUT, 
            model_path=H5_MODEL,
            params_path=PARAMS_JSON,
            iteration_length=PREDICTION_ITERATIONS,
            prediction_queue=self.prediction_queue
        )

        self.athena_thread = Thread(target=self.run_athena, daemon=True)
        self.hermes_thread = Thread(target=self.run_hermes, daemon=True)

    # Thread Loops

    def run_athena(self):
        '''
        Run the Athena scraper in the background.
        Monitor its output and raise an error if it hangs
        '''
        self.log.info('Starting Athena...')
        self.athena.run(headless=True)
        try:
            while not self.abort:
                # Monitor thread, ensure data continues to populate
                time_since_update = now() - self.athena.last_time
                if time_since_update > ATHENA_SCRAPE_INTERVAL_SECONDS*3:
                    self.handle_timeout(self.athena)
                    break
        except KeyboardInterrupt:
            self.log.info('Keyboard interrupt detected in run_athena, aborting')
            self.abort_all()

    def run_hermes(self):
        '''
        Run Hermes in the background
        '''
        self.log.info('Starting Hermes...')
        self.hermes.start()
        last_submission_count = self.hermes.status[1]
        try:
            while not self.abort:
                submission_count = queue_size = self.hermes.status[1]
                if queue_size > PREDICTION_QUEUE_MAX_SIZE and last_submission_count == submission_count:
                    self.handle_timeout(self.hermes)
                    break
                else:
                    last_submission_count = submission_count
        except KeyboardInterrupt:
            self.log.info('Keyboard interrupt detected in run_hermes, aborting')
            self.abort_all()

    # Runtime error handling

    def handle_timeout(self, olympian: PrimordialChaos):
        if olympian.abort:
            self.log.debug(f'{olympian.__class__.__name__} has been aborted, ending loop')
        else:
            self.log.error(f'{olympian.__class__.__name__} has timed out, aborting Zeus...')
        return 


    '''
    Hello, future self.
    This is looking good
    1) Setup Delphi thread here
    2) Figure out hermes buy percentage issue
    3) Override hermes with mock trading account here (or in a mock_zeus.py file)
    4) Get a 24/7 scraper running
    

    Outstanding questions:
    Is Delphi handling the CSVs properly? 
    Does zeus need to let Athena run to fill enough data?
    Test cases for Prometheus?
    How to format 24/7 scraper CSVs? ...SQL database??    
    '''

    # Management

    def abort_all(self):
        self.log.debug('Aborting all threads...')
        self.athena.abort = True
        self.hermes.abort = True
        self.abort = True
        self.log.debug('Abort booleans flipped, waiting for threads to end...')
        self.athena_thread.join()
        self.hermes_thread.join()

    def start(self):
        self.athena_thread.start()
        self.hermes_thread.start()
        try:
            while not self.abort:
                continue
        except KeyboardInterrupt:
            self.log.info('Exiting...')
            self.abort_all()
            exit(0)

if __name__ == "__main__":
    zeus = Zeus()
    zeus.start()
