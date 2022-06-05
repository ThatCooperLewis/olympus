import sys
import unittest
from testing import TEST_MODULES
from testing.utils import delete_all_test_files as delete_all


if __name__ == '__main__':
    if len(sys.argv) > 1:
        module = sys.argv[1]
        module = TEST_MODULES.get(module, None)
        if module:
            success = module.run().wasSuccessful()
        else:
            print('Unrecognized test suite. Please use one of the following:')
            for module in TEST_MODULES.keys():
                print(f'\t{module}')
            success = False
    else:
        suite = unittest.TestSuite()
        for module in TEST_MODULES.values():
            suite.addTest(unittest.makeSuite(module.suite))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        success = result.wasSuccessful()
    delete_all()
    sys.exit(0 if success else 1)
