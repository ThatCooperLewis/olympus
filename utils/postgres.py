import json
import traceback
from time import time as now
from typing import List

import psycopg2 as psql
from crosstower.models import Order, Ticker
from olympus.utils import PredictionVector

from utils import DiscordWebhook, Logger
import utils.config as constants


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
        self.timestamp: int = data[0]
        self.quantity: float = data[1]
        self.side: str = data[2]
        self.status: str = data[3]
        self.uuid: str = data[4]


class PostgresTicker:

    def __init__(self, data: tuple) -> None:
        self.timestamp: int = data[0]
        self.ask: float = data[1]
        self.bid: float = data[2]
        self.last: float = data[3]
        self.low: float = data[4]
        self.high: float = data[5]
        self.open: float = data[6]
        self.volume: float = data[7]
        self.volume_quote: float = data[8]

class PostgresPredictionVector:

    def __init__(self, data: tuple) -> None:
        self.timestamp: int = data[0]
        self.prediction_timestamp: int = data[1]
        self.prediction_weight: float = data[2]
        self.prediction_history: List[float] = data[3]
        self.status: str = data[4]
        self.uuid: str = data[5]

class Postgres:

    def __init__(self, ticker_table_override: str = None, order_table_override: str = None, prediction_table_override: str = None) -> None:
        # TODO: What the fuck is going on here? Use this elsewhere!
        self.ticker_table_name = ticker_table_override if ticker_table_override is not None else constants.POSTGRES_TICKER_TABLE_NAME
        self.order_table_name = order_table_override if order_table_override is not None else constants.POSTGRES_ORDER_TABLE_NAME
        self.prediction_table_name = prediction_table_override if prediction_table_override is not None else constants.POSTGRES_PREDICTION_TABLE_NAME
        self.log = Logger.setup(self.__class__.__name__)
        self.discord = DiscordWebhook("Postgres")
        self.__setup_connection()

    # Public Methods - INSERT

    def insert_ticker(self, ticker: Ticker):
        query = f"""INSERT INTO {self.ticker_table_name} {constants.POSTGRES_TICKER_COLUMNS}
        VALUES ({ticker.timestamp}, {ticker.ask}, {ticker.bid}, {ticker.last}, {ticker.low}, {ticker.high}, {ticker.open}, {ticker.volume}, {ticker.volume_quote})"""
        self._query(query, False)

    def insert_order(self, order: Order):
        query = f"""INSERT INTO {self.order_table_name} {constants.POSTGRES_ORDER_COLUMNS}
        VALUES ({now()}, {order.quantity}, '{order.side}', '{constants.POSTGRES_STATUS_QUEUED}', '{order.uuid}')"""
        self._query(query, False)

    def insert_prediction_vector(self, prediction_vector: PredictionVector):
        history = self.__convert_prediction_history_to_string(prediction_vector.prediction_history)
        query = f"""INSERT INTO {self.prediction_table_name} {constants.POSTGRES_PREDICTION_COLUMNS}
        VALUES ({now()}, {prediction_vector.timestamp}, {prediction_vector.weight}, {history}, '{constants.POSTGRES_STATUS_QUEUED}', '{prediction_vector.uuid}')"""
        self._query(query, False)

    # Public Methods - SELECT

    def get_latest_tickers(self, row_count: int) -> List[PostgresTicker]:
        """
        It returns a specific number of the newest tickers from the database
        
        :param row_count: The number of rows to return
        :return: A list of PostgresTicker objects
        """
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

    def get_queued_predictions(self) -> List[PostgresPredictionVector]:
        """
        Get all the enqueued predictions from the database
        :return: A list of PredictionVector objects.
        """
        query = f"""SELECT * FROM {self.prediction_table_name} WHERE status = 'QUEUED' ORDER BY timestamp ASC"""
        result = self._query(query, True)
        return list(map(self.__convert_result_to_prediction, result))

    # Public Methods - UPDATE

    def update_prediction_status(self, prediction_uuid: str, new_status: str):
        status = self.__parse_allowed_statuses(new_status)
        query = f"""UPDATE {self.prediction_table_name} SET status = '{status}' WHERE uuid = '{prediction_uuid}'"""
        self._query(query, False)
        
    def update_order_status(self, uuid: str, new_status: str):
        status = self.__parse_allowed_statuses(new_status)
        query = f"""UPDATE {self.order_table_name} SET status = '{status}' WHERE uuid = '{uuid}'"""
        self._query(query, False)

    # Private Methods

    def __convert_result_to_order(self, result) -> PostgresOrder:
        return PostgresOrder(result)

    def __convert_result_to_ticker(self, result) -> PostgresTicker:
        return PostgresTicker(result)

    def __convert_result_to_prediction(self, result) -> PostgresPredictionVector:
        return PostgresPredictionVector(result)

    def __convert_prediction_history_to_string(self, prediction_history: List[float]) -> str:
        return "ARRAY " + str(prediction_history)

    def __parse_allowed_statuses(self, status: str):
        for allowed_status in constants.POSTGRES_ALLOWED_STATUSES:
            if status.lower() == allowed_status.lower():
                return allowed_status
        raise Exception(f"Invalid status: {status}")

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
        with open(constants.CREDENTIALS_FILE) as json_file:
            data: dict = json.load(json_file)
            config = data.get("postgres")
        self.conn = psql.connect(f"dbname='{config['database']}' user='{config['user']}' host='{config['host']}' password='{config['password']}'")
    
    def __reconnect(self):
        self.log.debug("Attempting to reconnect...")
        self.__setup_connection()


if __name__ == "__main__":
    pass
