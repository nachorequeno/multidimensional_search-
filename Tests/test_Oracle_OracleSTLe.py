import os
import tempfile as tf
import unittest
import copy

from ParetoLib.Oracle.OracleSTLe import OracleSTLe, OracleSTLeLib


##############
# OracleSTLe #
##############

class OracleSTLeTestCase(unittest.TestCase):
    def setUp(self):
        # type: (OracleSTLeTestCase) -> None
        self.this_dir = 'Oracle/OracleSTLe'
        self.files_to_clean = set()
        self.files_to_load = self.add_file_to_load()

    def tearDown(self):
        # type: (OracleSTLeTestCase) -> None
        for filename in self.files_to_clean:
            if os.path.isfile(filename):
                os.remove(filename)

    def add_file_to_clean(self, filename):
        # type: (OracleSTLeTestCase) -> None
        self.files_to_clean.add(filename)

    def add_file_to_load(self):
        # type: (OracleSTLeTestCase) -> list
        # local_dirs = [x[0] for x in os.walk('Oracle/OracleSTL')]
        local_dirs = [x[0] for x in os.walk(self.this_dir)]
        oraclestl_filenames = []
        for local_dir in local_dirs:
            oraclestl_filenames += self.add_file_to_load_from_folder(local_dir)
        return oraclestl_filenames

    def add_file_to_load_from_folder(self, folder):
        # type: (OracleSTLeTestCase, str) -> list
        # test_dir = self.this_dir + folder
        test_dir = folder
        files_path = os.listdir(test_dir)
        test_txt = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]

        assert all(os.path.isfile(test) for test in test_txt)

        return test_txt

    # Test OracleSTLe
    def test_version(self):
        # type: (OracleSTLeTestCase) -> None
        for infile in self.files_to_load:
            print('Reading from {0}'.format(infile))
            ora = OracleSTLe()
            ora.from_file(infile, human_readable=True)
            print('Version {0}'.format(ora.version()))

    def test_files_OracleSTLe(self):
        # type: (OracleSTLeTestCase) -> None
        self.read_write_files(human_readable=False)
        self.read_write_files(human_readable=True)

    def read_write_files(self,
                         human_readable=False):
        # type: (OracleSTLeTestCase, bool) -> None
        tmpfile = tf.NamedTemporaryFile(delete=False)
        outfile = tmpfile.name

        # Oracle
        ora1 = OracleSTLe()
        ora2 = OracleSTLe()

        self.assertEqual(ora1, ora2)

        for infile in self.files_to_load:
            # Read/Write Oracle from file
            ora1 = OracleSTLe()
            ora2 = OracleSTLe()

            print('Reading from {0}'.format(infile))
            ora1.from_file(infile, human_readable=True)

            print('Writing to {0}'.format(outfile))
            ora1.to_file(outfile, append=False, human_readable=human_readable)

            print('Reading from {0}'.format(outfile))
            ora2.from_file(outfile, human_readable=human_readable)

            print('Oracle 1: {0}'.format(ora1))
            print('Oracle 2: {0}'.format(ora2))

            param1 = ora1.get_var_names()
            param2 = ora2.get_var_names()

            self.assertNotEqual(param1, [])
            self.assertEqual(param1, param2)

            print('Oracle 1 Parameters: {0}'.format(param1))
            print('Oracle 2 Parameters: {0}'.format(param2))

            self.assertEqual(ora1, ora2, 'Different files')
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
        self.add_file_to_clean(outfile)


#################
# OracleSTLeLib #
#################

class OracleSTLeLibTestCase(unittest.TestCase):
    def setUp(self):
        # type: (OracleSTLeLibTestCase) -> None
        self.this_dir = 'Oracle/OracleSTLe'
        self.files_to_clean = set()
        self.files_to_load = self.add_file_to_load()

    def tearDown(self):
        # type: (OracleSTLeLibTestCase) -> None
        for filename in self.files_to_clean:
            if os.path.isfile(filename):
                os.remove(filename)

    def add_file_to_clean(self, filename):
        # type: (OracleSTLeLibTestCase, str) -> None
        self.files_to_clean.add(filename)

    def add_file_to_load(self):
        # type: (OracleSTLeLibTestCase) -> list
        # local_dirs = [x[0] for x in os.walk('Oracle/OracleSTL')]
        local_dirs = [x[0] for x in os.walk(self.this_dir)]
        oraclestl_filenames = []
        for local_dir in local_dirs:
            oraclestl_filenames += self.add_file_to_load_from_folder(local_dir)
        return oraclestl_filenames

    def add_file_to_load_from_folder(self, folder):
        # type: (OracleSTLeLibTestCase, str) -> list
        # test_dir = self.this_dir + folder
        test_dir = folder
        files_path = os.listdir(test_dir)
        test_txt = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]

        assert all(os.path.isfile(test) for test in test_txt)

        return test_txt

    # Test OracleSTLeLib
    def test_version(self):
        # type: (OracleSTLeLibTestCase) -> None
        for infile in self.files_to_load:
            print('Reading from {0}'.format(infile))
            ora = OracleSTLeLib()
            ora.from_file(infile, human_readable=True)
            print('Version {0}'.format(ora.version()))

    def test_files_OracleSTLeLib(self):
        # type: (OracleSTLeLibTestCase) -> None
        self.read_write_files(human_readable=False)
        self.read_write_files(human_readable=True)

    def read_write_files(self,
                         human_readable=False):
        # type: (OracleSTLeLibTestCase, bool) -> None
        tmpfile = tf.NamedTemporaryFile(delete=False)
        outfile = tmpfile.name

        # Oracle
        ora1 = OracleSTLeLib()
        ora2 = OracleSTLeLib()

        self.assertEqual(ora1, ora2)

        for infile in self.files_to_load:
            # Read/Write Oracle from file
            ora1 = OracleSTLeLib()
            ora2 = OracleSTLeLib()

            print('Reading from {0}'.format(infile))
            ora1.from_file(infile, human_readable=True)

            print('Writing to {0}'.format(outfile))
            ora1.to_file(outfile, append=False, human_readable=human_readable)

            print('Reading from {0}'.format(outfile))
            ora2.from_file(outfile, human_readable=human_readable)

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
        self.add_file_to_clean(outfile)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
