import json
import traceback
from time import time as now
from typing import List

import psycopg2 as psql
from crosstower.models import Order, Ticker

from utils import DiscordWebhook, Logger
from utils.config import (CREDENTIALS_FILE, POSTGRES_ORDER_TABLE_NAME,
                          POSTGRES_TICKER_TABLE_NAME, POSTGRES_ORDER_STATUS_QUEUED)


class PostgresCursor:

    def __init__(self, connection) -> None:
        self.conn = connection

    def __enter__(self):
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, tb):
        self.conn.commit()
        self.cursor.close()
        self.cursor = None


class PostgresOrder:

    def __init__(self, data: tuple) -> None:
        self.id = data[0]
        self.timestamp = data[1]
        self.quantity = data[2]
        self.side = data[3]
        self.status = data[4]


class PostgresTicker:

    def __init__(self, data: tuple) -> None:
        self.timestamp = data[0]
        self.ask = data[1]
        self.bid = data[2]
        self.last = data[3]
        self.low = data[4]
        self.high = data[5]
        self.open = data[6]
        self.volume = data[7]
        self.volume_quote = data[8]

class Postgres:

    def __init__(self, ticker_table_override: str = None, order_table_override: str = None) -> None:
        # TODO: What the fuck is going on here? Use this elsewhere!
        self.ticker_table_name = ticker_table_override if ticker_table_override is not None else POSTGRES_TICKER_TABLE_NAME
        self.order_table_name = order_table_override if order_table_override is not None else POSTGRES_ORDER_TABLE_NAME
        self.log = Logger.setup(self.__class__.__name__)
        self.discord = DiscordWebhook("Postgres")
        self.__setup_connection()

    # Public Methods

    def insert_ticker(self, ticker: Ticker):
        query = f"""INSERT INTO {self.ticker_table_name} (timestamp, ask, bid, last, low, high, open, volume, volume_quote) 
        VALUES ({ticker.timestamp}, {ticker.ask}, {ticker.bid}, {ticker.last}, {ticker.low}, {ticker.high}, {ticker.open}, {ticker.volume}, {ticker.volume_quote})"""
        self._query(query, False)

    def insert_order(self, order: Order):
        query = f"""INSERT INTO {self.order_table_name} (timestamp, quantity, side, status) 
        VALUES ({now()}, {order.quantity}, '{order.side}', '{POSTGRES_ORDER_STATUS_QUEUED}')"""
        self._query(query, False)

    def get_latest_tickers(self, row_count: int) -> List[PostgresTicker]:
        query = f"SELECT * FROM {self.ticker_table_name} ORDER BY timestamp DESC LIMIT {row_count}"
        result = self._query(query, True)
        if type(result) is list:
            result.reverse()
            return list(map(self.__convert_result_to_ticker, result))
        else:
            return []

    def get_outstanding_orders(self) -> List[PostgresOrder]:
        """
        Get all the orders that have not been processed.
        :return: A list of Order objects
        """
        query = f"""SELECT * FROM {self.order_table_name} WHERE status = 'QUEUED' ORDER BY timestamp ASC"""
        result = self._query(query, True)
        return list(map(self.__convert_result_to_order, result))

    def __convert_result_to_order(self, result) -> PostgresOrder:
        return PostgresOrder(result)

    def __convert_result_to_ticker(self, result) -> PostgresTicker:
        return PostgresTicker(result)

    def _query(self, query_str: str, fetch_result: bool):
        result = None
        attempt = 0
        completed = False
        while attempt < 3:
            try:
                with PostgresCursor(self.conn) as cursor:
                    self.log.debug('Submitting query to Postgres: "%s"', query_str)
                    cursor.execute(query_str)
                    if fetch_result:
                        result = cursor.fetchall()
                completed = True
                break
            except:
                message = f"**SQL Query Failed**: {query_str}\n{traceback.format_exc()}"
                self.log.error(message)
                self.__reconnect()
                attempt += 1
                continue
        if not completed:
            if message:
                self.discord.send_alert(message)
            raise Exception("Failed to submit query to Postgres after 3 attempts. Giving up.")
        return result        

    def __setup_connection(self):
        with open(CREDENTIALS_FILE) as json_file:
            data: dict = json.load(json_file)
            config = data.get("postgres")
        self.conn = psql.connect(f"dbname='{config['database']}' user='{config['user']}' host='{config['host']}' password='{config['password']}'")
    
    def __reconnect(self):
        self.log.debug("Attempting to reconnect...")
        self.__setup_connection()


class PostgresTesting(Postgres):

    # Expose query method for testing
    def query(self, query_str: str, fetch_result: bool):
        return self._query(query_str, fetch_result)


if __name__ == "__main__":
    pass
