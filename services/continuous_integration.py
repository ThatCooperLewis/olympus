from time import sleep

from unit_tests_automated import ContinuousIntegration as CI
from utils import DiscordWebhook, Logger


class IntegrationService:

    def __init__(self):
        self.log = Logger.setup(self.__class__.__name__)
        self.discord = DiscordWebhook(self.__class__.__name__)
        self.ci = CI()

    def run(self):
        self.discord.send_status(f"ContinuousIntegration has started a new run. (Git hash: `{Logger.git_hash()}`)")
        try:
            while True:
                self.ci.run_cycle()
                sleep(30)
        except KeyboardInterrupt:
            pass
        print("Continuous integration service is running")
