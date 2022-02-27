from email.errors import NonPrintableDefect
import json
import traceback

import psycopg2 as psql

from crosstower.models import Ticker
from utils import Logger, DiscordWebhook
from utils.config import POSTGRES_TICKER_TABLE_NAME, POSTGRES_ORDER_TABLE_NAME, CREDENTIALS_FILE

class Postgres:

    def __init__(self, ticker_table_override: str = None) -> None:
        # TODO: What the fuck is going on here? Use this elsewhere!
        self.ticker_table_name = ticker_table_override if ticker_table_override is not None else POSTGRES_TICKER_TABLE_NAME
        self.log = Logger.setup(self.__class__.__name__)
        self.discord = DiscordWebhook("Postgres")
        self.__setup_connection()

    # Public Methods

    def get_latest_rows(self, row_count: int) -> list:
        # TODO: How many columns should be returned here? Just the ones that are used?
        query = f"SELECT timestamp, ask FROM {self.ticker_table_name} ORDER BY timestamp DESC LIMIT {row_count}"
        result = self._query(query, True)
        if type(result) is list:
            result.reverse()
            return result
        else:
            return []

    def insert_ticker(self, ticker: Ticker):
        query = f"""INSERT INTO {self.ticker_table_name} (timestamp, ask, bid, last, low, high, open, volume, volume_quote) 
        VALUES ({ticker.timestamp}, {ticker.ask}, {ticker.bid}, {ticker.last}, {ticker.low}, {ticker.high}, {ticker.open}, {ticker.volume}, {ticker.volume_quote})"""
        self._query(query, False)

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


if __name__ == "__main__":
    pass
