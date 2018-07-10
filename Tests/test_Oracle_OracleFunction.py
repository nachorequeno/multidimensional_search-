import os
import tempfile as tf
import unittest

from ParetoLib.Oracle.OracleFunction import *


##################
# OracleFunction #
##################


class OracleFunctionTestCase(unittest.TestCase):

    def setUp(self):
        self.files_to_clean = set()

    def tearDown(self):
        for filename in self.files_to_clean:
            if os.path.isfile(filename):
                os.remove(filename)

    def add_file_to_clean(self, filename):
        self.files_to_clean.add(filename)

    # Test polynomial conditions
    def test_membership_condition(self):

        c1 = Condition('x', '>', '2')
        c2 = Condition('y', '<', '0.75')

        # Oracle
        ora = OracleFunction()
        ora.add(c1)
        ora.add(c2)
        fora = ora.membership()

        # fora(p1)
        # fora(p2)
        # fora(p3)

        p1 = (0.0, 1.0)
        p2 = (3.0, 0.1)
        p3 = (2.0, 1.0)

        self.assertFalse(fora(p1))
        self.assertTrue(fora(p2))
        self.assertFalse(fora(p3))

    def test_class_equalities(self):

        # Condition
        c1 = Condition()
        c2 = Condition()

        self.assertEqual(c1, c2)

        c1 = Condition('x', '>', '0.5')
        c2 = Condition('y', '<', '0.75')

        self.assertNotEqual(c1, c2)

    def test_files(self):

        self.read_write_files(False)
        self.read_write_files(True)

    def read_write_files(self,
                         human_readable=False):

        tmpfile = tf.NamedTemporaryFile(delete=False)
        nfile = tmpfile.name

        # Condition
        c1 = Condition('x', '>', '0.5')

        # Read/Write Condition from file
        print 'Reading from %s' % nfile
        print 'Writing to %s' % nfile

        c1.to_file(nfile, append=False, human_readable=human_readable)
        c2 = Condition()
        c2.from_file(nfile, human_readable=human_readable)

        self.assertEqual(c1, c2)

        # Oracle
        ora1 = OracleFunction()
        ora2 = OracleFunction()

        self.assertEqual(ora1, ora2)

        c1 = Condition('x', '>', '0.5')
        ora1.add(c1)
        ora2.add(c1)

        self.assertEqual(ora1, ora2)

        c2 = Condition('y', '<', '0.75')
        ora2.add(c2)

        self.assertNotEqual(ora1, ora2)

        # Read/Write Oracle from file
        print 'Reading from %s' % nfile
        print 'Writing to %s' % nfile

        ora1.to_file(nfile, append=False, human_readable=human_readable)
        ora2 = OracleFunction()
        ora2.from_file(nfile, human_readable=human_readable)

        self.assertEqual(ora1, ora2)

        # Remove tempfile
        # os.unlink(nfile)
        self.add_file_to_clean(nfile)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
