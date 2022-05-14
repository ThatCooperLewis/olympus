from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from typing import List
from crosstower.models import Order
from utils.environment import env
from utils import Logger, Postgres
from utils.config import GDRIVE_API_SCOPES as SCOPES 

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
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'google_creds.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        service = build('sheets', 'v4', credentials=creds)
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

    def rotate_order_feed(self) -> None:
        # TODO: Un-mock this
        self.log.debug("Rotating order feed")
        try:
            order = self.postgres.get_latest_mock_orders(row_count=1)[0]
            # TODO: Configfile the range
            sheet_orders = self.__get_values('_data!A2:H289')
            if len(sheet_orders) >= 288:
                sheet_orders = sheet_orders[:-1]
            sheet_orders.insert(0, [
                str(order.timestamp), 
                str(order.quantity),
                str(order.side),
                str(order.total_value), 
                str(order.ending_usd_balance), 
                str(order.ending_btc_balance), 
                str(order.current_price),
                str(order.uuid)
            ])
            self.__update_values('_data!A2:H289', sheet_orders)
        except Exception as e:
            self.log.error("It didn't work")
            self.log.error(e)