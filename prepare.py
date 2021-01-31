import numpy as np
import pandas as pd
import pickle as pk
from sklearn.preprocessing import MinMaxScaler as MinMax

# Not yet sure what this is for?/s
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
# Length of sequences to chunk data
SEQ_LEN = 100
# Proportion of data to reserve for training
TRAIN_SPLIT = 0.95
'''
DATA PREP
'''


def intake_and_shape(csv_path: str):
    # Import and parse data
    df = pd.read_csv(csv_path, parse_dates=['Date'])
    df = df.sort_values('Date')

    # Reshape data into range [0,1]
    scaler = MinMax()
    close_price = df.Close.values.reshape(-1, 1)
    scaled_close = scaler.fit_transform(close_price)

    # Remove NaN values from data
    scaled_close = scaled_close[~np.isnan(scaled_close)]
    return scaled_close.reshape(-1, 1)


'''
PREPROCESSING
'''


def to_sequences(data, seq_len):
    d = []
    for index in range(len(data) - seq_len):
        d.append(data[index: index + seq_len])
    return np.array(d)


def preprocess(data_raw, seq_len, train_split):
    data = to_sequences(data_raw, seq_len)
    num_train = int(train_split * data.shape[0])

    X_train = data[:num_train, :-1, :]
    y_train = data[:num_train, -1, :]
    X_test = data[num_train:, :-1, :]
    y_test = data[num_train:, -1, :]

    return X_train, y_train, X_test, y_test


if __name__ == "__main__":
    print("Shaping...")
    scaled_data = intake_and_shape("historical-data.csv")
    print("Preprocessing...")
    X_train, y_train, X_test, y_test = preprocess(
        scaled_data, SEQ_LEN, TRAIN_SPLIT)
    print("Exporting pickles...")
    pk.dump(X_train, open('data/x-train.pickle', 'wb'))
    pk.dump(y_train, open('data/y-train.pickle', 'wb'))
    pk.dump(X_test, open('data/x-test.pickle', 'wb'))
    pk.dump(y_test, open('data/y-test.pickle', 'wb'))
