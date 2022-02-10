import sys
import unittest

from testing import TestAthena, TestDelphi, TestHermes

if __name__ == '__main__':
    # Run all tests
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAthena))
    suite.addTest(unittest.makeSuite(TestHermes))
    suite.addTest(unittest.makeSuite(TestDelphi))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
