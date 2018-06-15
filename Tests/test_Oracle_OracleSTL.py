import os
import tempfile as tf
import copy
import unittest

from ParetoLib.Oracle.OracleSTL import *


###############
# OracleSTL #
###############

class OracleSTLTestCase(unittest.TestCase):
    def setUp(self):
        self.files_to_clean = set()

    def tearDown(self):
        for filename in self.files_to_clean:
            if (os.path.isfile(filename)):
                os.remove(filename)

    def add_file_to_clean(self, filename):
        self.files_to_clean.add(filename)

    # Test OracleSTL
    def test_OracleSTL(self):
        self.read_write_files(human_readable=False)
        self.read_write_files(human_readable=True)

    def read_write_files(self,
                         min_corner=0.0,
                         max_corner=1.0,
                         human_readable=False):
        # type: (_, float, float, bool) -> _
        tmpfile = tf.NamedTemporaryFile(delete=False)
        nfile = tmpfile.name

        # Oracle
        ora1 = OracleSTL()
        ora2 = OracleSTL()


        self.assertEqual(ora1, ora2)

        # Membership test
        fora1 = ora1.membership()

        for p in p1:
            self.assertTrue(fora1(p))

        for p in p2:
            self.assertTrue(fora1(p))

        for p in p3:
            self.assertFalse(fora1(p))

        # Read/Write Oracle from file
        ora1.toFile(nfile, append=False, human_readable=human_readable)
        ora2 = OracleSTL()
        ora2.fromFile(nfile, human_readable=human_readable)

        self.assertEqual(ora1, ora2)

        # Remove tempfile
        # os.unlink(nfile)
        self.add_file_to_clean(nfile)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
