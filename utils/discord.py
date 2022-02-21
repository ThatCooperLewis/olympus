import requests
import json
from utils import Logger
import random


# TODO: Move config to a config file
CREDENTIALS_FILE = 'credentials.json'

class DiscordWebhook:

    def __init__(self, app_name: str):
        self.log = Logger.setup(self.__class__.__name__)
        self.name = app_name
        self.url = self.__get_webhook_url_from_json_file(CREDENTIALS_FILE)
        if not self.url:
            self.log.error(f'No discord webhook url found in {CREDENTIALS_FILE}')
            raise Exception(f'No discord webhook url found in {CREDENTIALS_FILE}')

    def send_alert(self, message: str):
            payload = {"username": self.name, "content": message}
            self.log.debug(f'Sending discord alert: {message}')
            _ = requests.post(self.url, data=payload)

    def __get_webhook_url_from_json_file(self, file_path: str):
        with open(file_path) as json_file:
            data: dict = json.load(json_file)
            return data.get("discord_webhook")