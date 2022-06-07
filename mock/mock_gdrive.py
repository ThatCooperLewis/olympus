from utils import Logger

class MockGoogleSheets:

    def __init__(self, app_name):
         self.log = Logger.setup(self.__class__.__name__)
         self.name = app_name

    def update_order_feed(self):
        self.log.debug("Pretending to rotate order feed")