import time
startTime = time.time()

import log_suppressor
import argparse as argp
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf
from pylab import rcParams
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras import Model as tfModel
from tensorflow.keras import Sequential
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.layers import Activation, Bidirectional, Dense, Dropout
from tensorflow.python.keras.layers import CuDNNLSTM


print("Loading memory patch")
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)

class Model:

    def __init__(self, model_name: str, input_csv: str = None, input_model: str = None, **params):
        print(params.get('params'))
        self.name = model_name
        if not input_csv and not input_model:
            print("ERROR: Neither of input_csv nor a input_model provided!")
            exit()
        self.load_model(input_model)
        self.csv_path = input_csv

        self.scaler = MinMaxScaler()
        self.X_train: np.ndarray = None
        self.y_train: np.ndarray = None
        self.X_test: np.ndarray = None
        self.y_test: np.ndarray = None

        # Tuning Knobs
        params = params.get('params', {})
        self.seq_len = params.get('seq_len', 20)
        self.window_size = self.seq_len - 1
        self.dropout = params.get('dropout', 0.2)
        self.epoch_count = params.get('epoch_count', 50)
        self.testing_split = params.get('testing_split', 0.95)
        self.validation_split = params.get('validation_split', 0.2)
        self.exclude_rows = params.get('exclude_rows', 0)
        self.patience = int(self.epoch_count * .15)

        # GUI Config
        # todo: style='darkgrid'
        sns.set(style='whitegrid', palette='muted', font_scale=1.5)
        rcParams['figure.figsize'] = 14, 8
        # Other stuff
        self.batch_size = 64
        np.random.seed(42069)
        return

    # DATA PARSING & MANIPULATION

    def shape_data(self, df: pd.DataFrame):
        close_price = df.price.values.reshape(-1, 1)
        scaled_close = self.scaler.fit_transform(close_price)
        # Remove NaN values from data
        scaled_close = scaled_close[~np.isnan(scaled_close)]
        return scaled_close.reshape(-1, 1)

    def to_sequences(self, data, seq_len):
        d = []
        for index in range(len(data) - seq_len + 1):
            d.append(data[index: index + seq_len])
        return np.array(d)

    def intake_preprocess(self):
        # Import and parse data
        df = pd.read_csv(self.csv_path, parse_dates=['timestamp'])
        data_raw = df.sort_values('timestamp')
        # Preprocess data
        data_raw = self.shape_data(data_raw)
        data = self.to_sequences(data_raw, self.seq_len)
        self.split_data(data)

    def split_data(self, data):
        training_size = int(self.testing_split * data.shape[0])
        self.X_train = data[:training_size, :-1, :]
        self.y_train = data[:training_size, -1, :]
        self.X_test = data[training_size:, :-1, :]
        self.y_test = data[training_size:, -1, :]

    def append_xTest(self, new_row: int):
        data = self.X_test
        data = np.append(data, new_row)
        data = np.array([data.reshape(-1, 1)])
        data = data[:, 1:, :]
        self.X_test = data

    # MODELING

    def __create_model(self):
        self.model = Sequential()
        self.model.add(Bidirectional(
            CuDNNLSTM(self.window_size, return_sequences=True),
            input_shape=(self.window_size, self.X_train.shape[-1])
        ))
        self.model.add(Dropout(rate=self.dropout))
        self.model.add(Bidirectional(
            CuDNNLSTM((self.window_size * 2), return_sequences=True)
        ))
        self.model.add(Dropout(rate=self.dropout))
        self.model.add(Bidirectional(
            CuDNNLSTM(self.window_size, return_sequences=False)
        ))
        self.model.add(Dense(units=1))
        self.model.add(Activation('linear'))

    def __train_model(self):
        model_dir = f"results/{self.name}"
        model_path = f"{model_dir}/model.h5"
        if not os.path.exists('results'): os.mkdir('results')
        if not os.path.exists(model_dir): os.mkdir(model_dir)
        self.model.compile(loss='mean_squared_error', optimizer='adam')
        self.history = self.model.fit(
            self.X_train,
            self.y_train,
            epochs=self.epoch_count,
            batch_size=self.batch_size,
            shuffle=False,
            validation_split=self.validation_split,
            callbacks=[
                EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=self.patience),
                ModelCheckpoint(filepath=model_path, monitor='val_loss', save_best_only=True)
            ]
        )
        self.model = tf.keras.models.load_model(model_path)

    def evaluate(self):
        train_loss = self.model.evaluate(self.X_train, self.y_train, verbose=1)
        test_loss = self.model.evaluate(self.X_test, self.y_test, verbose=1)
        return train_loss, test_loss

    def predict(self):
        y_hat = self.model.predict(self.X_test)
        result = self.scaler.inverse_transform(y_hat)
        return result

    def train(self):
        self.intake_preprocess()
        self.__create_model()
        self.__train_model()

    def build_predictions(self, cycles: int = 3):
        predictions = []
        for _ in range(cycles):
            result = self.predict()[0][0]
            predictions.append(result)
            self.append_xTest(result)
        return predictions

    # DONT DELETE
    # This is how you get the last item in X test (i think)
    # last_known = self.scaler.inverse_transform(self.X_test[0])



    # UTILITIES

    def save_params(self):
        with open(f"results/{self.name}/params.json", "w+") as file:
            json.dump({
                "seq_len" : self.seq_len,
                "dropout" : self.dropout,
                "epoch_count" : self.epoch_count,
                "testing_split" : self.testing_split,
                "validation_split" : self.validation_split,
            }, file, indent=4)

    def load_model(self, file_path: str):
        if not file_path:
            self.model = None
        else:
            self.model = tf.keras.models.load_model(file_path)

    def plot_model_loss(self, save=False) -> plt:
        f = plt.figure()
        f.clear()
        plt.close(f)
        plt.plot(self.history.history['loss'])
        plt.plot(self.history.history['val_loss'])
        plt.title('model loss')
        plt.ylabel('loss')
        plt.xlabel('epoch')
        plt.ylim([0.0, 0.015])
        plt.legend(['train', 'test'], loc='upper left')
        if save:
            plt.savefig(f"results/{self.name}/model_loss.png")
        return plt


class Predict(Model):

    def run(self):
        self.intake_preprocess()
        result = self.predict()[0][0]
        return result

    # Override methods to shape "test" data properly 
    def to_sequences(self, data, seq_len):
        print("correct function call")
        data = np.array([data[-(seq_len-1):]])
        print(self.scaler.inverse_transform(data[0]))
        return data

    def split_data(self, data):
        self.X_test = data

class TrainPredict(Model):

    def run(self, prediction_cycles: int = 1):
        if not self.model:
            self.train()
            self.save_params()
        initial_feed = []
        for subarray in self.scaler.inverse_transform(self.X_test[0]):
            # Create most recent history for graph
            initial_feed.append(subarray[0])
        self.plot_model_loss().show()

        result_feed = []
        for _ in range(prediction_cycles):
            result = self.predict()[0][0]
            result_feed.append(result)
            self.X_test = self.update_data(self.X_test, result)
        self.render_prediction_chart(initial_feed, result_feed).show()

    def update_data(self, data: np.ndarray, new_row: int):
        data = np.append(data, new_row)
        data = np.array([data.reshape(-1, 1)])
        data = data[:, 1:, :]
        return data

    def split_data(self, data):
        # Remove last element from each sequence
        self.X_train = data[:, :-1, :]
        # Create a sequence of only the last element
        self.y_train = data[:, -1, :]
        # Use sequence ending in most recent row
        self.X_test = data[-1:, 1:, :]

    def render_prediction_chart(self, initial_feed: list, prediction_feed: list) -> plt:
        initial_feed = initial_feed[int(len(initial_feed)/1.25):]
        full_feed = initial_feed + prediction_feed
        plt.plot(full_feed, label="Predicted Price", color='red')
        full_feed.sort()
        plt.vlines(
            x=(len(initial_feed) - 1),
            ymin=full_feed[0],
            ymax=full_feed[-1],
            colors='purple'
        )

        plt.title('BTC')
        plt.xlabel('Time [days]')
        plt.ylabel('Price')

        plt.show()


class TestHistory(Model):

    def run(self):
        self.train()
        self.save_params()
        self.plot_model_loss().show()
        y_hat_inverse = self.predict()
        self.render_prediction_chart(y_hat_inverse).show()

    def preprocess(self, data_raw):
        data_raw = self.shape_data(data_raw)
        data = self.to_sequences(data_raw, self.seq_len)
        self.split_data(data)

    def split_data(self, data):
        training_size = int(self.testing_split * data.shape[0])
        self.X_train = data[:training_size, :-1, :]
        self.y_train = data[:training_size, -1, :]
        self.X_test = data[training_size:, :-1, :]
        self.y_test = data[training_size:, -1, :]

    def render_prediction_chart(self, y_hat) -> plt:
        self.y_test_inverse = self.scaler.inverse_transform(self.y_test)
        plt.plot(self.y_test_inverse, label="Actual Price", color='green')
        plt.plot(y_hat, label="Predicted Price", color='red')

        plt.title('Bitcoin price prediction')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.legend(loc='best')


if __name__ == "__main__":
    with open(f'results/1617764061 - 0.0002/params.json') as file:
            params = json.load(file)
    result = Predict('TODOFIX', 'newBTC.csv', 'results/1617764061 - 0.0002/model.h5', params=params).run()
    print(result)
    # parser = argp.ArgumentParser()
    # parser.add_argument('csv_path')
    # parser.add_argument('mode', help="Test historical data (test, t) Predict upcoming intervals (predict, p) Guess next direction (next, n)")
    # parser.add_argument('--model_path', help="Filepath of existing .h5 model")
    # parser.add_argument('--intervals', help="How many intervals forward to guess (Predict Mode requirement)")
    # args = parser.parse_args()
    # csv_path = args.csv_path
    # model_name = f"{csv_path.split('/')[-1].split('.')[0]}"
    # if args.mode.lower() in ['test', 't']:
    #     TestHistory(model_name, input_csv=args.csv_path).run()
    # elif args.mode.lower() in ['predict', 'p']:
    #     try:
    #         interval = int(args.intervals)
    #     except:
    #         interval = 0
    #     TrainPredict(model_name, input_csv=args.csv_path).run(interval)