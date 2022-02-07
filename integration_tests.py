import sys
import unittest

from testing import TestAthena

if __name__ == '__main__':
    # Run TestAthena
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAthena)
    result =unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())