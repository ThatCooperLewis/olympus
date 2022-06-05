from cmath import log
import sys
import unittest
from testing import TEST_MODULES
from testing.utils import delete_all_test_files as delete_all


if __name__ == '__main__':
    # TODO: Make this argparse with help text
    module = sys.argv[1]
    log_file = sys.argv[2] if len(sys.argv) > 2 else None

    if module == 'all':
        suite = unittest.TestSuite()
        for module in TEST_MODULES.values():
            suite.addTest(unittest.makeSuite(module.suite))
        result = unittest.TextTestRunner(open(log_file, "a+") if log_file else None, verbosity=2).run(suite)
        success = result.wasSuccessful()
    else:
        module = TEST_MODULES.get(module, None)
        if module:
            success = module.run(open(log_file, "a+") if log_file else None).wasSuccessful()
        else:
            print('Unrecognized test suite. Please use one of the following:')
            for module in TEST_MODULES.keys():
                print(f'\t{module}')
            success = False
    delete_all()
    sys.exit(0 if success else 1)
