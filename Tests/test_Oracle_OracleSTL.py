import tempfile as tf
import unittest

from ParetoLib.Oracle.OracleSTL import *


###############
# OracleSTL #
###############

class OracleSTLTestCase(unittest.TestCase):
    def setUp(self):
        self.this_dir = 'Oracle/OracleSTL'
        self.files_to_clean = set()
        self.files_to_load = self.add_file_to_load()

    def tearDown(self):
        for filename in self.files_to_clean:
            if os.path.isfile(filename):
                os.remove(filename)

    def add_file_to_clean(self, filename):
        self.files_to_clean.add(filename)

    def add_file_to_load(self):
        # local_dirs = [x[0] for x in os.walk('Oracle/OracleSTL')]
        local_dirs = [x[0] for x in os.walk(self.this_dir)]
        oraclestl_filenames = []
        for local_dir in local_dirs:
            oraclestl_filenames += self.add_file_to_load_from_folder(local_dir)
        return oraclestl_filenames

    def add_file_to_load_from_folder(self, folder):
        # test_dir = self.this_dir + folder
        test_dir = folder
        files_path = os.listdir(test_dir)
        test_txt = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]

        assert all(os.path.isfile(test) for test in test_txt)

        return test_txt

    # Test OracleSTL
    def test_OracleSTL(self):
        self.read_write_files(human_readable=False)
        self.read_write_files(human_readable=True)

    def read_write_files(self,
                         human_readable=False):
        # type: (OracleSTLTestCase, bool) -> None
        tmpfile = tf.NamedTemporaryFile(delete=False)
        outfile = tmpfile.name

        # Oracle
        ora1 = OracleSTL()
        ora2 = OracleSTL()

        self.assertEqual(ora1, ora2)

        for infile in self.files_to_load:
            print('Reading from {0}'.format(infile))
            print('Writing to {0}'.format(outfile))

            # Read/Write Oracle from file
            ora1 = OracleSTL()
            ora1.from_file(infile, human_readable=True)
            ora1.to_file(outfile, append=False, human_readable=human_readable)

            ora2 = OracleSTL()
            ora2.from_file(outfile, human_readable=human_readable)

            self.assertEqual(ora1, ora2)

        # Remove tempfile
        # os.unlink(nfile)
        self.add_file_to_clean(outfile)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
