import log_suppressor
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf
from pylab import rcParams
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras import Sequential
from tensorflow.keras import Model as tfModel
from tensorflow.keras.layers import Activation, Bidirectional, Dense, Dropout
from tensorflow.python.keras.layers import CuDNNLSTM


# Prevents memory crash
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)


class Model:

    def __init__(self, input_csv):
        self.csv_path = input_csv
        self.scaler = MinMaxScaler()

        self.X_train: np.ndarray = None
        self.y_train: np.ndarray = None
        self.X_test: np.ndarray = None
        self.y_test: np.ndarray = None

        # Tuning Knobs
        self.seq_len = 100
        self.window_size = self.seq_len - 1
        self.dropout = 0.2
        self.epoch_count = 300
        self.testing_split = 0.95
        self.validation_split = 0.2

        # GUI Config
        # todo: style='darkgrid'
        sns.set(style='whitegrid', palette='muted', font_scale=1.5)
        rcParams['figure.figsize'] = 14, 8
        # Other stuff
        self.batch_size = 64
        np.random.seed(42069)
        return

    def intake_data(self) -> pd.DataFrame:
        # Import and parse data
        df = pd.read_csv(self.csv_path, parse_dates=['timestamp'])
        return df.sort_values('timestamp')

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

    def create_model(self):
        self.model = Sequential()
        self.model.add(Bidirectional(
            CuDNNLSTM(self.window_size, return_sequences=True),
            # TODO !!! See if shape[-1] changes when new data is added
            # If not, no need to rebuild model! Just model.fit() each time!!
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

    def train_model(self):
        self.model.compile(loss='mean_squared_error', optimizer='adam')
        self.history = self.model.fit(
            self.X_train,
            self.y_train,
            epochs=self.epoch_count,
            batch_size=self.batch_size,
            shuffle=False,
            validation_split=self.validation_split,
        )

    def predict(self):
        y_hat = self.model.predict(self.X_test)
        result = self.scaler.inverse_transform(y_hat)
        return result[0][0]

    def save_model(self, model: tfModel):
        # TODO
        return


class Predict(Model):

    def run(self, prediction_cycles: int = 1):
        data = self.intake_data()
        self.preprocess(data)
        initial_feed = []
        for subarray in self.scaler.inverse_transform(self.X_test[0]):
            initial_feed.append(subarray[0])
        self.create_model()
        self.train_model()
        result_feed = []
        for _ in range(prediction_cycles):
            result = self.predict()
            result_feed.append(result)
            self.X_test = self.update_data(self.X_test, result)
            # self.preprocess(data)
        self.render_prediction_chart(initial_feed, result_feed)

    def preprocess(self, data_raw):
        data_raw = self.shape_data(data_raw)
        data = self.to_sequences(data_raw, self.seq_len)
        self.split_data(data)

    def split_data(self, data):
        self.X_train = data[:, :-1, :]
        self.y_train = data[:, -1, :]
        self.X_test = data[-1:, 1:, :]

    def update_data(self, data: np.ndarray, new_row: int):
        data = np.append(data, new_row)
        data = np.array([data.reshape(-1, 1)])
        data = data[:, 1:, :]
        return data

    def render_prediction_chart(self, initial_feed: list, prediction_feed: list):
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


class Test(Model):

    def run(self):
        data = self.intake_data()
        self.preprocess(data)
        self.create_model()
        self.train_model()
        self.predict()
        self.render_prediction_chart()

    def preprocess(self, data_raw):
        data_raw = self.shape_data(data_raw)
        data = self.to_sequences(data_raw, self.seq_len)
        training_size = int(self.testing_split * data.shape[0])
        self.split_data(data, training_size)

    def split_data(self, data, training_size):
        self.X_train = data[:training_size, :-1, :]
        self.y_train = data[:training_size, -1, :]
        self.X_test = data[training_size:, :-1, :]
        self.y_test = data[training_size:, -1, :]

    def render_prediction_chart(self):
        self.y_test_inverse = self.scaler.inverse_transform(self.y_test)
        plt.plot(self.y_test_inverse, label="Actual Price", color='green')
        plt.plot(self.y_hat_inverse, label="Predicted Price", color='red')

        plt.title('Bitcoin price prediction')
        plt.xlabel('Time [days]')
        plt.ylabel('Price')
        plt.legend(loc='best')

        plt.show()


if __name__ == "__main__":
    # model = Test(input_csv='btc-history-60min-small.csv')
    model = Predict(input_csv='btc-history-60min-smaller.csv')
    model.run()
