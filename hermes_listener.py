from utils import Logger, DiscordWebhook
from olympus.hermes import Hermes

class HermesOrderListener:

    def __init__(self) -> None:
        self.log = Logger.setup(self.__class__.__name__)
        self.discord = DiscordWebhook(self.__class__.__name__)
        self.hermes = Hermes()
        self.abort = False

    # TODO: Use the run method from Zeus

    def run(self):
        self.discord.send_alert("HermesOrderListener has started a new run.")
        self.hermes.start()
        try:
            while not self.abort:
                pass
        except KeyboardInterrupt:
            self.abort = True
            self.hermes.stop()
            self.discord.send_alert("HermesOrderListener has stopped (KeyboardInterrupt).")

if __name__ == '__main__':
    HermesOrderListener().run()