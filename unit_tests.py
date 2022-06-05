import sys
import unittest

from testing import TEST_MODULES

if __name__ == '__main__':
    if len(sys.argv) > 1:
        module = sys.argv[1]
        module = TEST_MODULES.get(module, None)
        if module:
            sys.exit(not module.run().wasSuccessful())
        else:
            print('Unrecognized test suite. Please use one of the following:')
            for module in TEST_MODULES.keys():
                print(f'\t{module}')
            sys.exit(1)
    else:
        suite = unittest.TestSuite()
        for module in TEST_MODULES.values():
            suite.addTest(unittest.makeSuite(module.suite))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(not result.wasSuccessful())
