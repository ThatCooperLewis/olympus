from unittest import TestCase
import services_manager as ServicesManager
from services import TickerMonitor, TickerScraper

class TestServicesManager(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_service(self):
        scraper = ServicesManager.get_service('scraper')
        self.assertTrue(type(scraper) == TickerScraper)
        
        monitor = ServicesManager.get_service('monitor')
        self.assertTrue(type(monitor) == TickerMonitor)
        
        invalid = ServicesManager.get_service('invalid')
        self.assertTrue(invalid == None)