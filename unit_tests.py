import sys
import unittest

from testing import TestAthena, TestDelphi, TestHermes

if __name__ == '__main__':
    # Run all tests
    test_suites = [
        TestAthena,
        TestDelphi,
        TestHermes,
    ]
    suite = unittest.TestSuite()
    for test_suite in test_suites:
        suite.addTest(unittest.makeSuite(test_suite))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
