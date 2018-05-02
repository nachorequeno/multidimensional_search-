import os
import tempfile as tf
import unittest

from ParetoLib.Oracle.OracleFunction import *

##################
# OracleFunction #
##################


class OracleFunctionTestCase (unittest.TestCase):

    def setUp ( self ) :
        self.files_to_clean = set()


    def tearDown ( self ) :
        for filename in self.files_to_clean :
            if ( os.path.isfile(filename) ) :
                os.remove(filename)

    def add_file_to_clean ( self, filename ) :
        """
        Adds a file for deferred removal by the tearDown() routine.

        Arguments :
            filename  ( string )
                File name to remove by the tearDown() routine.
        """
        self.files_to_clean.add(filename)

    # Test polynomial conditions
    def test_membership_condition(self):

        c1 = Condition('x', '>', '2')
        c2 = Condition('y', '<', '0.75')

        cl1 = ConditionList()
        cl1.add(c1)

        f1 = cl1.membership()
        # f1(0)
        # f1(3)

        p1 = (0.0, )
        p2 = (3.0, )

        self.assertFalse(f1(p1))
        self.assertTrue(f1(p2))

        cl2 = ConditionList()
        cl2.add(c2)
        f2 = cl2.membership()
        # f2(1.0)
        # f2(0.1)

        p1 = (1.0,)
        p2 = (0.1,)

        self.assertFalse(f2(p1))
        self.assertTrue(f2(p2))

        # Oracle
        ora = OracleFunction()
        ora.add(cl1, 0)
        ora.add(cl2, 1)
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

        # ConditionList
        cl1 = ConditionList()
        cl2 = ConditionList()

        self.assertEqual(cl1, cl2)

        cl1.add(c1)
        cl1.add(c2)

        cl2.add(c2)

        self.assertNotEqual(cl1, cl2)

    def test_files ( self) :

        self.read_write_files_test(False)
        self.read_write_files_test(True)

    def read_write_files_test(self,
                            human_readable=False):
        # type: (_, bool) -> _

        # Condition
        c1 = Condition('x', '>', '0.5')
        c2 = Condition('y', '<', '0.75')

        # ConditionList
        cl1 = ConditionList()
        cl2 = ConditionList()

        cl1.add(c1)
        cl1.add(c2)

        cl2.add(c2)

        tmpfile = tf.NamedTemporaryFile(delete=False)
        nfile = tmpfile.name

        # Read/Write Condition from file
        c1.toFile(nfile, append=False, human_readable=human_readable)
        c2 = Condition()
        c2.fromFile(nfile, human_readable=human_readable)

        self.assertEqual(c1, c2)

        # Read/Write ConditionList from file
        cl1.toFile(nfile, append=False, human_readable=human_readable)
        cl2 = ConditionList()
        cl2.fromFile(nfile, human_readable=human_readable)

        self.assertEqual(cl1, cl2)

        # Oracle
        ora1 = OracleFunction()
        ora2 = OracleFunction()

        self.assertEqual(ora1, ora2)

        ora1.add(cl1, 1)
        ora1.add(cl2, 2)

        ora2.add(cl2, 2)

        self.assertNotEqual(ora1, ora2)

        # Read/Write Oracle from file
        ora1.toFile(nfile, append=False, human_readable=human_readable)
        ora2 = OracleFunction()
        ora2.fromFile(nfile, human_readable=human_readable)

        self.assertEqual(ora1, ora2)

        # Remove tempfile
        # os.unlink(nfile)
        self.add_file_to_clean(nfile)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
