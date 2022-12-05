from unittest import TestCase
import services_manager_no_cuda as ServicesManager
from services import PostgresMonitor, TickerScraper, OrderListener

class TestServicesManager(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_service(self):
        scraper = ServicesManager.get_service('scraper')
        self.assertTrue(type(scraper) == TickerScraper)
        
        monitor = ServicesManager.get_service('monitor')
        self.assertTrue(type(monitor) == PostgresMonitor)
        
        orders = ServicesManager.get_service('orders')
        self.assertTrue(type(orders) == OrderListener)
        
        invalid = ServicesManager.get_service('invalid')
        self.assertTrue(invalid == None)