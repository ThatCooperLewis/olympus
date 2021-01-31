# import csv
from datetime import datetime
import pickle as pk
# import requests
import time
import pandas as pd

CSV_URL = "https://query1.finance.yahoo.com/v7/finance/download/BTC-USD?period1=1410912000&period2={}&interval=1d&events=history&includeAdjustedClose=true"

def save_pickle(object, path):
    file = open(path, 'wb')
    pk.dump(object, file)
    file.close()


def load_pickle(path):
    try:
        file = open(path, 'rb')
    except FileNotFoundError:
        print("ERROR: Could not find the file '{}'".format(path))
        exit()
    data = pk.load(file)
    file.close()
    return data

def get_csv_url():
    epoch = time.mktime(datetime.today().timetuple())
    return CSV_URL.format(int(epoch))