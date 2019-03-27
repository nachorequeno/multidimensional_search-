import os
import tempfile as tf
import unittest
import copy

from ParetoLib.Oracle.OracleFunction import OracleFunction, Condition


##################
# OracleFunction #
##################


class OracleFunctionTestCase(unittest.TestCase):

    def setUp(self):
        # type: (OracleFunctionTestCase) -> None
        self.files_to_clean = set()

    def tearDown(self):
        # type: (OracleFunctionTestCase) -> None
        for filename in self.files_to_clean:
            if os.path.isfile(filename):
                os.remove(filename)

    def add_file_to_clean(self, filename):
        # type: (OracleFunctionTestCase, str) -> None
        self.files_to_clean.add(filename)

    # Test polynomial conditions
    def test_membership_condition(self):
        # type: (OracleFunctionTestCase) -> None
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

        self.assertFalse(p1 in ora)
        self.assertTrue(p2 in ora)
        self.assertFalse(p3 in ora)

    def test_hash(self):
        # type: (OracleFunctionTestCase) -> None
        c1 = Condition('x', '>', '2')
        c2 = Condition('y', '<', '0.75')
        hash(c1)
        hash(c2)

        # Oracle
        ora = OracleFunction()
        ora.add(c1)
        ora.add(c2)
        hash(ora)

        del ora

    def test_class_equalities(self):
        # type: (OracleFunctionTestCase) -> None
        # Condition
        c1 = Condition()
        c2 = Condition()

        self.assertEqual(c1, c2)

        c1 = Condition('x', '>', '0.5')
        c2 = Condition('y', '<', '0.75')

        self.assertNotEqual(c1, c2)

    def test_files_Condition(self):
        # type: (OracleFunctionTestCase) -> None
        self.read_write_condition_files(human_readable=False)
        self.read_write_condition_files(human_readable=True)

    def read_write_condition_files(self,
                                human_readable=False):
        # type: (OracleFunctionTestCase, bool) -> None

        tmpfile = tf.NamedTemporaryFile(delete=False)
        nfile = tmpfile.name

        c1 = Condition('x', '>', '0.5')
        c2 = Condition()

        # Read/Write Condition from file
        print('Reading from {0}'.format(nfile))
        print('Writing to {0}'.format(nfile))

        c1.to_file(nfile, append=False, human_readable=human_readable)
        c2.from_file(nfile, human_readable=human_readable)

        print('Condition 1: {0}'.format(c1))
        print('Condition 2: {0}'.format(c2))

        self.assertEqual(c1, c2, 'Different condition')
        self.assertEqual(hash(c1), hash(c2), 'Different condition')

        del c1
        del c2

        # Remove tempfile
        # os.unlink(nfile)
        self.add_file_to_clean(nfile)

    def test_files_OracleFunction(self):
        # type: (OracleFunctionTestCase) -> None
        self.read_write_oracle_files(False)
        self.read_write_oracle_files(True)

    def read_write_oracle_files(self,
                         human_readable=False):
        # type: (OracleFunctionTestCase, bool) -> None
        tmpfile = tf.NamedTemporaryFile(delete=False)
        nfile = tmpfile.name

        # Condition
        c1 = Condition('x', '>', '0.5')

        # Read/Write Condition from file
        print('Reading from {0}'.format(nfile))
        print('Writing to {0}'.format(nfile))

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
        print('Reading from {0}'.format(nfile))
        print('Writing to {0}'.format(nfile))

        ora1.to_file(nfile, append=False, human_readable=human_readable)
        ora2 = OracleFunction()
        ora2.from_file(nfile, human_readable=human_readable)

        print('Oracle 1: {0}'.format(ora1))
        print('Oracle 2: {0}'.format(ora2))

        param1 = ora1.get_var_names()
        param2 = ora2.get_var_names()

        self.assertNotEqual(param1, [])
        self.assertEqual(param1, param2)

        print('Oracle 1 Parameters: {0}'.format(param1))
        print('Oracle 2 Parameters: {0}'.format(param2))

        self.assertEqual(ora1, ora2, 'Different oracles')
        self.assertEqual(hash(ora1), hash(ora2), 'Different oracles')

        ora3 = copy.copy(ora1)
        self.assertEqual(ora1, ora3, 'Different oracles')
        self.assertEqual(hash(ora1), hash(ora3), 'Different oracles')

        ora3 = copy.deepcopy(ora1)
        self.assertEqual(ora1, ora3, 'Different oracles')
        self.assertEqual(hash(ora1), hash(ora3), 'Different oracles')

        del ora1
        del ora2
        del ora3

        # Remove tempfile
        # os.unlink(nfile)
        self.add_file_to_clean(nfile)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
