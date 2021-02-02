import numpy as np
import pandas as pd
from pylab import rcParams
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Bidirectional, Activation, Dropout, Dense
from tensorflow.python.keras.layers import CuDNNLSTM
from utils import get_csv_url


class Model:

    def __init__(self):
        self.scaler = MinMaxScaler()

        self.X_train: np.ndarray = None
        self.y_train: np.ndarray = None
        self.X_test: np.ndarray = None
        self.y_test: np.ndarray = None

        # File paths
        self.csv_local_path = 'data/historical-data.csv'
        # Length of sequences to chunk data
        self.seq_len = 100
        self.window_size = self.seq_len - 1
        # Combat overfitting
        self.dropout = 0.2
        # How many epoch passes
        self.epoch_count = 50
        # GUI Config
        sns.set(style='whitegrid', palette='muted', font_scale=1.5)
        rcParams['figure.figsize'] = 14, 8
        # Other stuff
        self.batch_size = 64
        np.random.seed(42069)
        return

    def intake_and_shape(self) -> pd.DataFrame:
        # Import and parse data
        df = pd.read_csv(get_csv_url(), parse_dates=['timestamp'])
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

    def split_data(self, data, training_size):
        self.X_train = data[:training_size, :-1, :]
        self.y_train = data[:training_size, -1, :]
        self.X_test = data[training_size:, :-1, :]
        self.y_test = data[training_size:, -1, :]

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
            validation_split=0.1
        )

    def predict(self):
        y_hat = self.model.predict(self.X_test)
        self.y_hat_inverse = self.scaler.inverse_transform(y_hat)


class Predict(Model):

    def run(self, prediction_cycles: int = 1):
        pass

    def preprocess(self, data_raw):
        data = self.to_sequences(data_raw, self.seq_len)
        training_size = int(data.shape[0] - 1)
        self.split_data(data, training_size)