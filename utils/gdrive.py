from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from typing import List
from utils.environment import env
from utils import Logger, Postgres
from utils import config
from utils.postgres import PostgresOrder 

'''
Google Sheets interacts with Lists of Lists of Strings
Example:
[
    ["1234678", "BTCUSD", "buy", "0.01", ...],
    ["1234678", "BTCUSD", "sell", "0.01", ...],
]
'''

class GoogleSheets:
    
    def __init__(self) -> None:
        self.resource: Resource = self.__get_resource()
        self.sheet_id = env.google_sheet_id
        self.postgres = Postgres()
        self.log = Logger.setup("GoogleSheets")

    def __get_resource(self) -> Resource:
        creds = None
        if os.path.exists(config.GoogleDrive.TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(
                config.GoogleDrive.TOKEN_PATH, 
                config.GoogleDrive.API_SCOPES
            )
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.GoogleDrive.CREDENTIALS_PATH,
                    config.GoogleDrive.API_SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(config.GoogleDrive.TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
        service: Resource = build('sheets', 'v4', credentials=creds)
        return service.spreadsheets()

    def __get_values(self, range: str) -> List[List[str]]:
        result = self.resource.values().get(
            spreadsheetId=self.sheet_id, 
            range=range).execute()
        return result.get('values', [])

    def __update_values(self, range: str, values: List[List[str]]) -> None:
        self.resource.values().update(
            spreadsheetId=self.sheet_id,
            range=range,
            valueInputOption='USER_ENTERED',
            body={'values': values}).execute()

    def __append_values(self, range: str, values: List[List[str]]) -> None:
        self.resource.values().update(
            spreadsheetId=self.sheet_id,
            range=range,
            valueInputOption='USER_ENTERED',    
            body={'values': values, 'majorDimension': 'ROWS'}).execute()    

    def shorten_order_feed(self, orders_array, desired_length) -> List[List[str]]:
        length = len(orders_array)
        skip_interval = length/desired_length
        truncated = []
        div = None
        for i in range(length):
            new_div = i // skip_interval
            if new_div != div:
                order: PostgresOrder = orders_array[i]
                truncated.append([
                    str(order.timestamp),
                    str(order.usd_balance),
                    str(order.btc_balance),
                    str(order.current_price)
                ])
            div = new_div
        return truncated
    
    def rotate_24_hour_feed(self, latest_order: PostgresOrder) -> List[List[str]]:
        sheet_orders = self.__get_values(config.GoogleDrive.DAILY_FEED_RANGE)
        sheet_latest_timestamp = int(sheet_orders[0][0])
        if sheet_latest_timestamp == latest_order.timestamp:
            return None
        if len(sheet_orders) >= 288:
            sheet_orders = sheet_orders[:-1]
        sheet_orders.insert(0, [
            str(latest_order.timestamp), 
            str(latest_order.quantity),
            str(latest_order.side),
            str(latest_order.usd_balance), 
            str(latest_order.btc_balance), 
            str(latest_order.current_price)
        ])
        return sheet_orders

    def update_order_feed(self) -> None:
        self.log.debug("Updating all-time order feed...")
        try:
            all_orders = self.postgres.get_all_orders()
            truncated_orders = self.shorten_order_feed(all_orders, 5000)
            self.__update_values(config.GoogleDrive.ALLTIME_FEED_RANGE, truncated_orders)
        except Exception as e:
            self.log.error("Failed to update _full_data feed")
            self.log.error(e)

        self.log.debug("Rotating order feed")
        try:
            latest_order = self.postgres.get_latest_mock_orders(row_count=1)[0]
            order_feed = self.rotate_24_hour_feed(latest_order)
            if order_feed:
                self.__update_values(config.GoogleDrive.DAILY_FEED_RANGE, order_feed)
        except Exception as e:
            self.log.error("Failed to update _data feed")
            self.log.error(e)