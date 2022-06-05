import unittest

from testing.test_athena import TestAthena
from testing.test_delphi import TestDelphi
from testing.test_hermes import TestHermes
from testing.test_postgres import TestPostgres
from testing.test_services_manager import TestServicesManager


class __TestModule:

    def __init__(self, suite):
        self.suite = unittest.TestLoader().loadTestsFromTestCase(suite)

    @property
    def result(self):
        return unittest.TextTestRunner(verbosity=2).run(self.suite)


MODULES = {
    'athena': __TestModule(TestAthena),
    'delphi': __TestModule(TestDelphi),
    'hermes': __TestModule(TestHermes),
    'postgres': __TestModule(TestPostgres),
    'services': __TestModule(TestServicesManager)
}
