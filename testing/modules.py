import unittest

from testing.test_athena import TestAthena
from testing.test_delphi import TestDelphi
from testing.test_hermes import TestHermes
from testing.test_postgres import TestPostgres
from testing.test_services_manager import TestServicesManager


class __TestModule:

    def __init__(self, suite):
        self.suite = suite

    def run(self):
        loaded_test = unittest.TestLoader().loadTestsFromTestCase(self.suite)
        return unittest.TextTestRunner(verbosity=2).run(loaded_test)


TEST_MODULES = {
    'athena': __TestModule(TestAthena),
    'delphi': __TestModule(TestDelphi),
    'hermes': __TestModule(TestHermes),
    'postgres': __TestModule(TestPostgres),
    'services': __TestModule(TestServicesManager)
}
