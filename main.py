import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas.core.frame import DataFrame
from pylab import rcParams
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.python.keras.layers import CuDNNLSTM, LSTM
from tensorflow.keras import Sequential, Model
from tensorflow.keras.layers import Bidirectional, Activation, Dropout, Dense
from utils import save_pickle, get_csv_url


# This prevents a crash from memory overloading
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(e)


class Predictor:

    def __init__(self):
        self.scaler = MinMaxScaler()
        self.model = Sequential()

        self.X_train: np.ndarray = None
        self.y_train: np.ndarray = None
        self.X_test: np.ndarray = None
        self.y_test: np.ndarray = None

        # File paths
        self.csv_local_path = 'data/historical-data.csv'
        self.history_path = 'model/history.pkl'
        # Length of sequences to chunk data
        self.seq_len = 100
        self.window_size = self.seq_len - 1
        # Proportion of data to reserve for training
        self.train_split = 0.95
        # Combat overfitting
        self.dropout = 0.2
        # GUI Config
        sns.set(style='whitegrid', palette='muted', font_scale=1.5)
        rcParams['figure.figsize'] = 14, 8
        # Other stuff
        self.batch_size = 64
        np.random.seed(42069)

        return

    def run(self):
        self.prepare_data()
        self.build_model()
        self.train_model()
        self.predict()
        # self.save_model()
        self.render_prediction_chart()

    '''
    DATA PREPROCESSING
    '''

    def prepare_data(self):
        scaled_data = self.intake_and_shape()
        self.preprocess(scaled_data)

    def intake_and_shape(self) -> pd.DataFrame:
        # Import and parse data
        df = pd.read_csv(get_csv_url(), parse_dates=['Date'])
        df.to_csv(self.csv_local_path, index=False)
        df = df.sort_values('Date')

        # Reshape data into range [0,1]
        close_price = df.Close.values.reshape(-1, 1)
        scaled_close = self.scaler.fit_transform(close_price)

        # Remove NaN values from data
        scaled_close = scaled_close[~np.isnan(scaled_close)]
        return scaled_close.reshape(-1, 1)

    def to_sequences(self, data, seq_len):
        d = []
        for index in range(len(data) - seq_len):
            d.append(data[index: index + seq_len])
        return np.array(d)

    def preprocess(self, data_raw):
        data = self.to_sequences(data_raw, self.seq_len)
        num_train = int(self.train_split * data.shape[0])

        self.X_train = data[:num_train, :-1, :]
        self.y_train = data[:num_train, -1, :]
        self.X_test = data[num_train:, :-1, :]
        self.y_test = data[num_train:, -1, :]

    '''
    MODELING
    '''

    def build_model(self):
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

    def train_model(self):
        self.model.compile(loss='mean_squared_error', optimizer='adam')
        self.history = self.model.fit(
            self.X_train,
            self.y_train,
            epochs=50,
            batch_size=self.batch_size,
            shuffle=False,
            validation_split=0.1
        )

    def save_model(self):
        # !!! THIS DOES NOT WORK !!!
        # Solutions online do not fix it
        self.model.save('model', save_format='tf')
        save_pickle(self.history, self.history_path)

    def predict(self):
        # predict() takes an array of X values (dates)
        # and outputs an array of Y values (prices)
        y_hat = self.model.predict(self.X_test)
        self.y_test_inverse = self.scaler.inverse_transform(self.y_test)
        self.y_hat_inverse = self.scaler.inverse_transform(y_hat)

    '''
    ANALYTICS
    '''

    def render_prediction_chart(self):
        plt.plot(self.y_test_inverse, label="Actual Price", color='green')
        plt.plot(self.y_hat_inverse, label="Predicted Price", color='red')

        plt.title('Bitcoin price prediction')
        plt.xlabel('Time [days]')
        plt.ylabel('Price')
        plt.legend(loc='best')

        plt.show()


if __name__ == "__main__":
    predictor = Predictor()
    predictor.run()
