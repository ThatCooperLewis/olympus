import json
from threading import Thread
from time import sleep
from typing import Tuple
from uuid import uuid4
from os import remove
import asyncio

import utils.config as constants
from utils import DiscordWebhook, Logger, Postgres

from olympus.helper_objects import PredictionVector
from olympus.helper_objects.prediction_queue import \
    PredictionQueueDB as PredictionQueue
from olympus.primordial_chaos import PrimordialChaos
from olympus.prometheus import Predict
from utils.environment import env

class Delphi(PrimordialChaos):

    '''
    Make predictions based on current trends
    '''

    def __init__(
        self,
        override_model_path: str = None,
        override_params_path: str = None,
        override_sql_mode_with_csv_path: str = None,
        override_prediction_queue: PredictionQueue = None,
        override_iteration_length: int = None,
    ) -> None:
        super().__init__()
        self.log = Logger.setup(__name__)
        self.discord = DiscordWebhook('Delphi')
        if override_sql_mode_with_csv_path:
            # CSV MODE
            # Instead of generating a CSV from the SQL database, use a local CSV
            self.sql_mode = False
            self.postgres = None
            self.csv_path = override_sql_mode_with_csv_path
            self.tmp_csv_path = self.__generate_tmp_filename(include_original_name=self.csv_path)
        else:
            # SQL MODE
            # Generate data for the tmp CSV using the SQL database
            self.postgres = Postgres()
            self.sql_mode = True
            self.tmp_csv_path = self.__generate_tmp_filename()

        model_path = override_model_path if override_model_path else env.keras_model_path
        params_path = override_params_path if override_params_path else env.keras_params_path

        with open(params_path) as file:
            params: dict = json.load(file)
            self.seq_len = params.get('seq_len')
            if not self.seq_len:
                self.log.error('No seq_len in params file')
                raise Exception("No seq_len in params")

        self.predictor = Predict(
            model_name='',
            input_csv=self.tmp_csv_path,
            input_model=model_path,
            params=params
        )

        self.iterations = override_iteration_length if override_iteration_length else constants.PREDICTION_ITERATION_COUNT
        self.delta_threshold = constants.PREDICTION_DELTA_THRESHOLD
        self.interval_size = constants.TICKER_INTERVAL

        self.prediction_queue: PredictionQueue = override_prediction_queue if override_prediction_queue else PredictionQueue(override_postgres=self.postgres)
        self.abort = False
        self.is_active = False
        self.latest_timestamp = None
        self.primary_thread: Thread = Thread(target=self.__primary_loop)
        self.all_threads = [self.primary_thread]

    def __fetch_new_data_from_csv(self) -> Tuple[float, int]:
        with open(self.csv_path, 'r') as file:
            rows = file.readlines()
            file.close()

        tmp_rows = [constants.DEFAULT_CSV_HEADERS]
        for index in range(-100, 0):
            # Remove newlines
            row = rows[index].strip() if index == -1 else rows[index]
            tmp_rows.append(row)

        self.__create_tmp_csv_with_lines(tmp_rows)

        latest_ticker = tmp_rows[-1]
        latest_price = float(latest_ticker.split(',')[0])
        latest_timestamp = int(latest_ticker.split(',')[-1])

        return latest_price, latest_timestamp
    
    def __fetch_new_data_from_psql(self) -> Tuple[float, int]:
        rows = self.postgres.get_latest_tickers(row_count=self.seq_len)
        tmp_rows = [constants.DEFAULT_CSV_HEADERS]
        
        for index, ticker in enumerate(rows):
            row = ticker.csv_line.strip() if index == len(rows) - 1 else ticker.csv_line
            tmp_rows.append(row)
        
        self.__create_tmp_csv_with_lines(tmp_rows)
        latest_ticker = rows[-1]
        return latest_ticker.ask, latest_ticker.timestamp

    def __latest_data_handler(self) -> Tuple[float, int]:
        if self.sql_mode:
            return self.__fetch_new_data_from_psql()
        else:
            return self.__fetch_new_data_from_csv()

    def __generate_tmp_filename(self, include_original_name: str = None) -> str:
        short_uuid = uuid4().hex[:8] 
        if include_original_name:
            return include_original_name.replace('.csv', f'_tmp_{short_uuid}.csv')
        else:
            return 'delphi_tmp_' + short_uuid + '.csv'

    def __create_tmp_csv_with_lines(self, lines: list):
        with open(self.tmp_csv_path, 'w+') as file:
            file.writelines(lines)
            file.close()

    def __add_prediction_to_tmp_csv(self, prediction: float, timestamp: int):
        with open(self.tmp_csv_path, 'a') as file:
            # Training model only cares about first column
            file.write(f'\n{prediction},10.0,10.0,10.0,10.0,10.0,10.0,10.0,{timestamp}')
            self.log.debug('Added prediction to csv')

    def __weigh_price_delta_against_threshold(self, prediction, current):
        '''
        Takes in a prediction and a current value, and returns a value between -1 and 1 that represents
        the intensity of change, relative to the threshold
        
        :param prediction: The predicted future price
        :param current: The current price of the stock
        :return: A value between -1 and 1 that represents the intensity of change, relative to the threshold
        '''
        delta = (prediction - current)/current
        self.log.debug(f"Predicted percent change: {round((delta*100), 4)}%")
        eval = delta/self.delta_threshold
        if eval > 1:
            return 1
        if eval < -1:
            return -1
        return eval

    async def sleep(self, seconds: int):
        for i in range(seconds):
            if self.abort:
                return
            await asyncio.sleep(1)

    def __primary_loop(self):
        self.log.debug('Starting loop')
        self.is_active = True
        while not self.abort:
            self.log.debug('Starting iteration')
            predictions = []
            current_price, timestamp = self.__latest_data_handler()
            if timestamp == self.latest_timestamp:
                if self.is_active:
                    self.alert_with_error('Ticket data is stale, skipping prediction. Will alert when new data is available')
                    self.is_active = False
                asyncio.run(self.sleep(65))
                continue
            else:
                if not self.is_active:
                    self.is_active = True
                    self.alert_with_error(f'Ticket data is fresh again. Waiting {self.seq_len} predictions, then resuming...')
                    asyncio.run(self.sleep(self.seq_len*self.interval_size))
                self.latest_timestamp = timestamp
            self.log.debug('Got latest data')
            
            for i in range(self.iterations):
                self.log.debug(f'Starting iteration {i}')
                timestamp += self.interval_size
                predictions.append(self.predictor.make_prediction())
                self.__add_prediction_to_tmp_csv(
                    prediction=round(predictions[i], 2),
                    timestamp=timestamp
                )
                
            self.log.debug('Finished iterations, adding to PredictionQueue')
            self.prediction_queue.put(
                PredictionVector(
                    weight=self.__weigh_price_delta_against_threshold(
                        prediction=predictions[-1],
                        current=current_price
                    ),
                    predictions=predictions,
                    timestamp=timestamp
                )
            )
            self.log.debug('Submitted prediction to queue')
            
            # Delete self.temp_csv_path
            remove(self.tmp_csv_path)
            self.log.debug('Deleted temp csv')
            
            # Sleep my sweet angel
            asyncio.run(self.sleep(self.interval_size * self.iterations))
        self.log.debug('Exiting loop')
