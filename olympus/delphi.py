import json
from queue import Queue
from threading import Thread
from time import sleep
from typing import Tuple

from olympus.primordial_chaos import PrimordialChaos
from olympus.prometheus import Predict
from olympus.utils import PredictionQueue, PredictionVector
from utils import DiscordWebhook, Logger


class Delphi(PrimordialChaos):

    '''
    Make predictions based on current trends
    '''

    def __init__(
        self,
        csv_path: str,
        model_path: str,
        params_path: str,
        iteration_length: int,
        prediction_queue: PredictionQueue,
    ) -> None:
        super().__init__()
        self.log = Logger.setup(__name__)
        self.discord = DiscordWebhook('Delphi')
        self.csv_path = csv_path
        self.tmp_csv_path = csv_path.replace('.csv', '_tmp.csv')

        with open(params_path) as file:
            params = json.load(file)
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

        self.iterations = iteration_length  # how many prediction cycles
        self.delta_threshold = 0.0003  # When price changes this much, take 100% action
        self.interval_size = 1  # TODO CHANGE Seconds between price tickers & prediction cycles
        self.prediction_queue = prediction_queue

        self.primary_thread: Thread = Thread(target=self.__threaded_loop)
        self.all_threads = [self.primary_thread]

    def __get_current_data_from_csv(self) -> Tuple[float, int]:
        with open(self.csv_path, 'r') as file:
            rows = file.readlines()
            file.close()

        tmp_rows = [rows[0]]
        for index in range(-100, 0):
            # Remove newlines
            row = rows[index]
            if index == -1:
                row = row.strip()
            tmp_rows.append(row)

        with open(self.tmp_csv_path, 'w+') as file:
            file.writelines(tmp_rows)
            file.close()

        last_row = tmp_rows[-1]
        price = float(last_row.split(',')[0])
        timestamp = int(last_row.split(',')[-1])

        return price, timestamp

    def __add_prediction_to_csv(self, prediction: float, timestamp: int):
        with open(self.tmp_csv_path, 'a') as file:
            # Training model only cares about first column
            file.write(
                f'\n{prediction},10.0,10.0,10.0,10.0,10.0,10.0,10.0,{timestamp}')
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

    def __threaded_loop(self):
        self.log.debug('Starting loop')
        while not self.abort:
            self.log.debug('Starting iteration')
            current_price, timestamp = self.__get_current_data_from_csv()
            prediction_ts = timestamp
            predictions = []
            self.log.debug('Got CSV data')
            
            for i in range(self.iterations):
                self.log.debug(f'Starting iteration {i}')
                prediction_ts += self.interval_size
                predictions.append(self.predictor.run())
                self.__add_prediction_to_csv(
                    prediction=round(predictions[i], 2),
                    timestamp=prediction_ts
                )

            self.prediction_queue.put(
                PredictionVector(
                    weight=self.__weigh_price_delta_against_threshold(
                        prediction=predictions[-1],
                        current=current_price
                    ),
                    predictions=predictions,
                    timestamp=prediction_ts
                )
            )
            self.log.debug('Submitted prediction to queue')

            sleep(self.interval_size + self.iterations)
        self.log.debug('Exiting loop')


if __name__ == "__main__":
    Delphi(
        csv_path='crosstower-btc.csv',
        model_path='results/1617764061 - 0.0002/model.h5',
        params_path='results/1617764061 - 0.0002/params.json',
        iteration_length=3
    ).run()