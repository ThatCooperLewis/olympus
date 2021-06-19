import json
from queue import Queue
from time import time
from typing import Tuple
import shutil

from cryptographer.model import Predict


class Delphi:

    def __init__(
        self,
        csv_path: str,
        model_path: str,
        params_path: str,
        iteration_length: int
    ) -> None:
        
        self.csv_path = csv_path
        self.tmp_csv_path = csv_path.replace('.csv', '_tmp.csv')
        with open(params_path) as file:
            params = json.load(file)
            self.seq_len = params.get('seq_len')
            if not self.seq_len:
                raise Exception("No seq_len in params")

        self.predictor = Predict('', self.tmp_csv_path, model_path, params)
        self.abort = False  # can be used to shut down loop
        self.iterations = iteration_length  # how many prediction cycles
        self.delta_threshold = 0.03  # When price changes this much, take 100% action
        self.interval_size = 300  # Seconds between price tickers & prediction cycles

    def __get_current_data(self) -> Tuple[float, int]:
        shutil.copyfile(self.csv_path, self.tmp_csv_path)
        # TODO
        # filter backwards from last line, keep only sequence of params.seq_len + header
        # return current price & timestamp
        pass

    def __append_prediction(self, prediction: float):
        with open(self.tmp_csv_path, 'a') as file:
            # Training model only cares about first column
            file.write(f'{prediction},0.0,0.0,0.0,0.0,0.0,0.0,0.0,0\n')

    def weigh_delta(self, prediction, current):
        # Returns a value between -1 and 1 that represents the intensity of change, relative to the threshold
        delta = (prediction - current)/current
        eval = delta/self.delta_threshold
        if eval > 1:
            return 1
        if eval < -1:
            return -1
        return eval

    def run_loop(self, order_queue: Queue):
        while not self.abort:
            current_price, timestamp = self.__get_current_data()
            prediction_time = timestamp + \
                (self.interval_size * self.iterations)
            for _ in range(self.iterations):
                prediction = self.predictor.run()
                self.__append_prediction(prediction)
            weight = self.weigh_delta(prediction, current_price)
            ticker = ConfidenceTicker(weight, prediction_time)
            order_queue.put(ticker)

            # run once for now
            self.abort = True


class ConfidenceTicker:

    # Simple solution for useful queue objects
    def __init__(self, weight, timestamp):
        self.weight = weight
        self.timestamp = timestamp


if __name__ == "__main__":
    Delphi(
        csv_path='crosstower-btc.csv',
        model_path='results/1617764061 - 0.0002/model.h5',
        params_path='results/1617764061 - 0.0002/params.json'
    ).run_loop()
