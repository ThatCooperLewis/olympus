from threading import Thread
from time import time as now
from time import sleep
from typing import List

from crosstower.socket_api import OrderListener, Trading
from olympus import Athena, Delphi, Hermes, PrimordialChaos
from olympus.utils import PredictionQueue
from utils import Logger, DiscordWebhook

# Constants

ATHENA_OUTPUT = 'run/athena.csv'
ATHENA_SCRAPE_INTERVAL_SECONDS = 5

TRADE_SYMBOL = 'BTCUSD'
H5_MODEL = 'run/model.h5'
PARAMS_JSON = 'run/params.json'
PREDICTION_ITERATIONS = 3
PREDICTION_QUEUE_MAX_SIZE = 5


class Zeus(PrimordialChaos):

    '''
    Initialize and watch everything
    '''

    def __init__(self) -> None:
        super().__init__()
        self.abort = False
        self.name = self.__class__.__name__
        self.log = Logger.setup(self.name)
        self.discord = DiscordWebhook(self.name)
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
        self.all_gods: List[PrimordialChaos] = [
            self.athena, 
            self.hermes, 
            self.delphi
        ]

        self.athena_thread = Thread(target=self.run_athena, daemon=True)
        self.hermes_thread = Thread(target=self.run_hermes, daemon=True)
        self.delphi_thread = Thread(target=self.run_delphi, daemon=True)
        self.all_threads = [
            self.athena_thread, 
            self.hermes_thread, 
            self.delphi_thread
        ]

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
                sleep(5)
        except KeyboardInterrupt:
            self.log.info('Keyboard interrupt detected in run_athena, aborting')
            self.join_threads()

    def run_hermes(self):
        '''
        Run Hermes in the background
        '''
        self.log.info('Starting Hermes...')
        self.hermes.start()
        last_submission_count = self.hermes.status[1]
        try:
            while not self.abort:
                queue_size, submission_count = self.hermes.status
                if queue_size > PREDICTION_QUEUE_MAX_SIZE and last_submission_count == submission_count:
                    self.handle_timeout(self.hermes)
                    break
                else:
                    last_submission_count = submission_count
                sleep(5)
        except KeyboardInterrupt:
            self.log.info('Keyboard interrupt detected in run_hermes, aborting')
            self.join_threads()

    def run_delphi(self):
        self.log.info('Starting Delphi...')
        self.delphi.run()
        try:
            while not self.abort:
                if not self.delphi.primary_thread.is_alive():
                    self.handle_timeout(self.delphi)
                    break
                sleep(5)
        except KeyboardInterrupt:
            self.log.info('Keyboard interrupt detected in run_delphi, aborting')
            self.join_threads()

    # Runtime error handling

    def handle_timeout(self, olympian: PrimordialChaos):
        if olympian.abort:
            self.log.debug(f'{olympian.__class__.__name__} has been aborted, ending loop')
        else:
            self.log.error(f'{olympian.__class__.__name__} has timed out, aborting Zeus...')
        return 

    '''
    UPDATE 2/21

    Delphi is formatting CSV properly!
    ...but something is stopping the predictor from running
    when some other thread is aborted, Delphi quickly populates the predictions.
    Need to see what's holding it up. Maybe multiproccess it, since no other threads are touching that file?


    '''



    '''
    Hello, future self.
    This is looking good
    2) Figure out hermes buy percentage issue
    3) Override hermes with mock trading account here (or in a mock_zeus.py file)
    4) Get a 24/7 scraper running
    

    Outstanding questions:
    Is Delphi handling the CSVs properly? 
    Does zeus need to let Athena run to fill enough data?
    Test cases for Prometheus?
    How to format 24/7 scraper CSVs? ...SQL database?? CSV on network drive?    
    '''

    # Management

    def stop(self):
        super().stop()
        for god in self.all_gods:
            god.stop()
        self.log.debug('Abort booleans flipped, waiting for threads to end...')

    def run(self):
        super().run()
        try:
            while not self.abort:
                continue
        except KeyboardInterrupt:
            self.log.info('Exiting...')
            self.join_threads()
            exit(0)

if __name__ == "__main__":
    zeus = Zeus()
    zeus.run()