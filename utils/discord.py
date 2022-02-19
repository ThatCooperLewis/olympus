import requests
import json
from utils import Logger 


# TODO: 

class DiscordWebhook:

    def __init__(self, credentials_file: str):
        webhook_url = self.get_webhook_from_json_file(credentials_file)
        self.url = webhook_url
        self.log = Logger.setup(self.__class__.__name__)

    def send_alert(self, username: str, message: str):
            payload = {"username": username, "content": message}
            self.log.debug(f'Sending discord alert: {message}')
            _ = requests.post(self.url, data=payload)

    def get_webhook_from_json_file(self, file_path: str):
        with open(file_path) as json_file:
            data: dict = json.load(json_file)
            return data.get("discord_webhook")