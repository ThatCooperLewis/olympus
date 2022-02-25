from email.errors import NonPrintableDefect
import json
import traceback

import psycopg2 as psql
# from psycopg2 import connection as psql_connection
# from psycopg2 import cursor as psql_cursor

from crosstower.models import Ticker
from utils import Logger, DiscordWebhook


class Postgres:

    '''
    TODO:
    - Make sure the connection isn't lost over time
    - Handle multiple attempts, reconnecting between them
    - Alerts if SQL query fails
    - Add logging statements
    '''

    # SUPER TODO: Hollllld up... athena already intervals? do we need it anyways? two separate intervals?
    # TODO: Check latest timestamp of interval table, 
    # if gap between timestamps is larger than interval, 
    # then add this ticker to that tabl

    def __init__(self) -> None:
        self.log = Logger.setup(self.__class__.__name__)
        self.discord = DiscordWebhook(self.__class__.__name__)
        config = self.__get_postgres_config('credentials.json')
        self.conn = psql.connect(f"dbname='{config['database']}' user='{config['user']}' host='{config['host']}' password='{config['password']}'")
    # Public Methods

    def get_latest_rows(self, row_count: int) -> list:
        with PostgresCursor(self.conn) as cursor:
            # TODO: How many columns should be returned here? Just the ones that are used?
            if type(row_count) is not int:
                raise Exception("row_count must be an integer")
            query = f"""
                SELECT timestamp, ask FROM ticker_feed ORDER BY timestamp DESC LIMIT {row_count}
            """
            cursor.execute(query)
            result = cursor.fetchall()
        if type(result) is list:
            result.reverse()
            return result
        else:
            return []

    def insert_ticker(self, ticker: Ticker):
        try:
            with PostgresCursor(self.conn) as cursor:
                query = f"""
                    INSERT INTO ticker_feed (timestamp, ask, bid, last, low, high, open, volume, volume_quote) 
                    VALUES ({ticker.timestamp}, {ticker.ask}, {ticker.bid}, {ticker.last}, {ticker.low}, {ticker.high}, {ticker.open}, {ticker.volume}, {ticker.volume_quote})
                """
                cursor.execute(query)
        except Exception as e:
            trace = traceback.format_exc()
            self.log.error(trace)
            self.discord.send_alert(f"SQL Submission Error: {trace}")

    def __get_postgres_config(self, config_path: str):
        with open(config_path) as json_file:
            data: dict = json.load(json_file)
            return data.get("postgres")

    def __reconnect(self):
        config = self.__get_postgres_config('credentials.json')
        self.conn = psql.connect(f"dbname='{config['database']}' user='{config['user']}' host='{config['host']}' password='{config['password']}'")


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
