import requests
from utils import Logger 

class DiscordWebhook:

    def __init__(self, webhook_url):
        self.url = webhook_url
        self.log = Logger.setup(self.__class__.__name__)

    def send_alert(self, username: str, message: str):
            payload = {"username": username, "content": message}
            self.log.debug(f'Sending discord alert: {message}')
            _ = requests.post(self.url, data=payload)
