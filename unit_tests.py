import sys
import unittest

from testing import TestAthena, TestDelphi, TestHermes

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'athena':
            suite = unittest.TestLoader().loadTestsFromTestCase(TestAthena)
            result = unittest.TextTestRunner(verbosity=2).run(suite)
        elif sys.argv[1] == 'delphi':
            suite = unittest.TestLoader().loadTestsFromTestCase(TestDelphi)
            result = unittest.TextTestRunner(verbosity=2).run(suite)
        elif sys.argv[1] == 'hermes':
            suite = unittest.TestLoader().loadTestsFromTestCase(TestHermes)
            result = unittest.TextTestRunner(verbosity=2).run(suite)
        else:
            print('Unrecognized test suite. Please use one of the following:')
            print('\tathena')
            print('\tdelphi')
            print('\thermes')
            sys.exit(1)
    else:
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
