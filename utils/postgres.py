import json
import traceback
from time import time as now
from typing import List, Tuple

import psycopg2 as psql
from crosstower.models import Order, Ticker
from olympus.helper_objects import PredictionVector

from utils import DiscordWebhook, Logger
import utils.config as constants
from utils.environment import env

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
        self.timestamp: int = int(data[0])
        self.quantity: float = float(data[1])
        self.side: str = str(data[2])
        self.status: str = str(data[3])
        self.uuid: str = str(data[4])
        self.usd_balance: float = float(data[5])
        self.btc_balance: float = float(data[6])
        self.current_price: float = float(data[7])


class MockPostgresOrder:
    
    def __init__(self, data: tuple) -> None:
        self.timestamp = int(data[0])
        self.quantity = float(data[1])
        self.side = str(data[2])
        self.ending_usd_balance = float(data[3])
        self.ending_btc_balance = float(data[4])   
        self.current_price = float(data[5]) 
        self.local_timestamp = int(data[6])
        self.uuid = str(data[7])
        self.total_value = float(data[8])
        self.status = str(data[9])

class PostgresTicker:

    def __init__(self, data: tuple) -> None:
        self.timestamp: int = int(data[0])
        self.ask: float = float(data[1])
        self.bid: float = float(data[2])
        self.last: float = float(data[3])
        self.low: float = float(data[4])
        self.high: float = float(data[5])
        self.open: float = float(data[6])
        self.volume: float = float(data[7])
        self.volume_quote: float = float(data[8])
        self.csv_line: str = f"{self.ask},{self.bid},{self.last},{self.low},{self.high},{self.open},{self.volume},{self.volume_quote},{self.timestamp}\n"

class PostgresPredictionVector:

    def __init__(self, data: tuple) -> None:
        self.timestamp: int = data[0]
        self.prediction_timestamp: int = data[1]
        self.weight: float = float(data[2])
        self.prediction_history: List[float] = []
        for prediction in data[3]:
            self.prediction_history.append(float(prediction))
        self.status: str = data[4]
        self.uuid: str = data[5]
        self.percent: float = data[6]

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
        self.log.debug(f"Inserting ticker with timestamp: {ticker.timestamp}")
        query = f"""INSERT INTO {self.ticker_table_name} {constants.POSTGRES_TICKER_COLUMNS}
        VALUES ({ticker.timestamp}, {ticker.ask}, {ticker.bid}, {ticker.last}, {ticker.low}, {ticker.high}, {ticker.open}, {ticker.volume}, {ticker.volume_quote})"""
        self._query(query, False)

    def insert_order(self, order: Order, current_price: float, crypto_balance: float, fiat_balance: float):
        self.log.debug(f"Inserting order with uuid: {order.uuid}")
        query = f"""INSERT INTO {self.order_table_name} {constants.POSTGRES_ORDER_COLUMNS}
        VALUES ({int(now())}, {order.quantity}, '{order.side}', '{constants.POSTGRES_STATUS_QUEUED}', '{order.uuid}')"""
        self._query(query, False)

    def insert_prediction_vector(self, prediction_vector: PredictionVector):
        self.log.debug(f"Inserting prediction vector with uuid: {prediction_vector.uuid}")
        history = self.__convert_prediction_history_to_string(prediction_vector.prediction_history)
        query = f"""INSERT INTO {self.prediction_table_name} {constants.POSTGRES_PREDICTION_COLUMNS}
        VALUES ({int(now())}, {prediction_vector.timestamp}, {prediction_vector.weight}, {history}, '{constants.POSTGRES_STATUS_QUEUED}', '{prediction_vector.uuid}', {prediction_vector.percent})"""
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

    def get_ticker_count(self):
        query = f"SELECT COUNT(*) FROM {self.ticker_table_name}"
        result = self._query(query, True)
        return result[0][0]

    # TODO: make this name like the prediction one
    def get_queued_orders(self) -> List[PostgresOrder]:
        """
        Get all the orders that have not been processed.
        :return: A list of Order objects
        """
        query = f"""SELECT * FROM {self.order_table_name} WHERE status = 'QUEUED' ORDER BY timestamp ASC"""
        result = self._query(query, True)
        return list(map(self.__convert_result_to_order, result))
    
    def get_latest_orders(self, row_count: int) -> List[PostgresOrder]:
        """
        It returns a specific number of the newest orders from the database
        
        :param row_count: The number of rows to return
        :return: A list of PostgresOrder objects
        """
        query = f"SELECT * FROM {self.order_table_name} ORDER BY timestamp DESC LIMIT {row_count}"
        result = self._query(query, True)
        if type(result) is list:
            result.reverse()
            return list(map(self.__convert_result_to_order, result))
        else:
            return []

    def get_all_orders(self) -> List[PostgresOrder]:
        """
        Get all the orders from the database
        
        :return: A list of Order objects
        """
        # TODO: Move column names to config
        query = f"""SELECT timestamp, quantity, side, status, uuid, usd_balance, btc_balance, current_price FROM {self.order_table_name} ORDER BY timestamp ASC"""
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
    
    def get_ticker_count_for_last_hour(self) -> int:
        """
        Get the number of tickers in the last hour
        :return: The number of tickers in the last hour
        """
        query = f"""SELECT COUNT(*) FROM ticker_feed WHERE local_timestamp > {int(now()) - 3600}"""
        result = self._query(query, True)
        return result[0][0]
    
    def get_latest_stack_of_same_orders(self) -> List[PostgresOrder]:
        query = f"""SELECT side FROM {self.order_table_name} ORDER BY timestamp DESC LIMIT 1"""
        last_side = self._query(query, True)[0][0]
        query = f"SELECT timestamp from {self.order_table_name} where side != '{last_side}' ORDER BY timestamp DESC LIMIT 1"
        earliest_timestamp = self._query(query, True)[0][0]
        query = f"SELECT * FROM {self.order_table_name} where timestamp > {earliest_timestamp} and side = '{last_side}' ORDER BY timestamp ASC"
        result = self._query(query, True)
        return list(map(self.__convert_result_to_order, result))

    # Public Methods - UPDATE

    def update_prediction_status(self, prediction_uuid: str, new_status: str):
        status = self.__parse_allowed_statuses(new_status)
        query = f"""UPDATE {self.prediction_table_name} SET status = '{status}' WHERE uuid = '{prediction_uuid}'"""
        self._query(query, False)
        
    def update_order_status(self, uuid: str, new_status: str):
        status = self.__parse_allowed_statuses(new_status)
        query = f"""UPDATE {self.order_table_name} SET status = '{status}' WHERE uuid = '{uuid}'"""
        self._query(query, False)

    # Public Methods - MOCK/TESTING
    # TODO: Move this? when we're done testing?

    def get_latest_mock_balances(self) -> Tuple[float, float]:
        query = "SELECT ending_usd_balance, ending_btc_balance FROM _mock_order_feed ORDER BY local_timestamp DESC LIMIT 1"
        result = self._query(query, True)
        usd = result[0][0]
        btc = result[0][1]
        return float(usd), float(btc)
    
    def insert_mock_order(self, quantity: float, side: str, ending_usd_balance: float, ending_btc_balance: float, current_btc_price: float, total_value: float, uuid: str):
        self.log.debug(f"Inserting mock order with uuid: {uuid}")
        query = f"""INSERT INTO _mock_order_feed (timestamp, quantity, side, ending_usd_balance, ending_btc_balance, current_btc_price, total_value, uuid)
        VALUES ({int(now())}, {quantity}, '{side}', {ending_usd_balance}, {ending_btc_balance}, {current_btc_price}, {total_value}, '{uuid}')"""
        self._query(query, False)
        
    def get_latest_mock_orders(self, row_count: int) -> List[MockPostgresOrder]:
        # TODO: Move column names to config
        query = f"SELECT timestamp, quantity, side, status, uuid, usd_balance, btc_balance, current_price FROM {self.order_table_name} ORDER BY timestamp DESC LIMIT {row_count}"
        result = self._query(query, True)
        return list(map(self.__convert_result_to_order, result))
    
    def __convert_result_to_mock_order(self, result) -> MockPostgresOrder:
        return MockPostgresOrder(result)


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
                    # Too noisy
                    # self.log.debug('Submitting query to Postgres: "%s"', query_str)
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
        self.conn = psql.connect(f"dbname='{env.postgres_database}' user='{env.postgres_user}' host='{env.postgres_host}' password='{env.postgres_password}'")
    
    def __reconnect(self):
        self.log.debug("Attempting to reconnect...")
        self.__setup_connection()


if __name__ == "__main__":
    pass
