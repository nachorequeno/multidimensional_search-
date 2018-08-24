import re
import pickle
import subprocess
import tempfile
import csv
import ast
import io
import sys
import os
import filecmp

import ParetoLib.Oracle as ParOracle
from ParetoLib.Oracle.Oracle import Oracle
from ParetoLib.JAMT.JAMT import JAVA_BIN, JAVA_OPT_JAR, JAMT_BIN, JAMT_OPT_ALIAS, JAMT_OPT_STL, JAMT_OPT_RES, \
    JAMT_OPT_SIGNAL


class OracleSTL(Oracle):
    def __init__(self, stl_prop_file='', vcd_signal_file='', var_alias_file='', stl_param_file=''):
        # type: (OracleSTL, str, str, str, str) -> None
        # assert stl_prop_file != ''
        # assert vcd_signal_file != ''
        # assert var_alias_file != ''
        # assert stl_param_file != ''

        Oracle.__init__(self)

        self.stl_prop_file = stl_prop_file.strip(' \n\t')
        self.vcd_signal_file = vcd_signal_file.strip(' \n\t')
        self.var_alias_file = var_alias_file.strip(' \n\t')

        stl_param_file_trim = stl_param_file.strip(' \n\t')
        self.stl_parameters = OracleSTL.get_parameters_stl(stl_param_file_trim)

    # Printers
    def __repr__(self):
        # type: (OracleSTL) -> str
        return self.to_str()

    def __str__(self):
        # type: (OracleSTL) -> str
        return self.to_str()

    def to_str(self):
        # type: (OracleSTL) -> str
        s = 'STL property file: {0}\n'.format(self.stl_prop_file)
        s += 'STL alias file: {0}\n'.format(self.var_alias_file)
        s += 'STL parameters file: {0}\n'.format(self.stl_parameters)
        s += 'VCD signal file: {0}\n'.format(self.vcd_signal_file)
        return s

    # Equality functions
    def __eq__old(self, other):
        # type: (OracleSTL, OracleSTL) -> bool
        # return hash(self) == hash(other)
        return (self.stl_prop_file == other.stl_prop_file) and \
               (self.vcd_signal_file == other.vcd_signal_file) and \
               (self.var_alias_file == other.var_alias_file) and \
               (self.stl_parameters == other.stl_parameters)

    def __eq__(self, other):
        # type: (OracleSTL, OracleSTL) -> bool
        # return hash(self) == hash(other)
        res = False
        try:
            res = (self.stl_prop_file == other.stl_prop_file) \
                  or filecmp.cmp(self.stl_prop_file, other.stl_prop_file)
            res = res or ((self.vcd_signal_file == other.vcd_signal_file)
                          or filecmp.cmp(self.vcd_signal_file, other.vcd_signal_file))
            res = res or ((self.var_alias_file == other.var_alias_file)
                          or filecmp.cmp(self.var_alias_file, other.var_alias_file))
            res = res or (self.stl_parameters == other.stl_parameters)
        except OSError:
            ParOracle.logger.error(
                'Unexpected error when comparing: {0}\n{1}\n{2}'.format(sys.exc_info()[0], str(self), str(other)))
        return res

    def __ne__(self, other):
        # type: (OracleSTL, OracleSTL) -> bool
        return not self.__eq__(other)

    # Identity function (via hashing)
    def __hash__(self):
        # type: (OracleSTL) -> int
        return hash((self.stl_prop_file, self.vcd_signal_file, self.var_alias_file, self.stl_parameters))

    def dim(self):
        # type: (OracleSTL) -> int
        return len(self.stl_parameters)

    def get_var_names(self):
        # type: (OracleSTL) -> list
        return [str(i) for i in self.stl_parameters]

    @staticmethod
    def get_parameters_stl(stl_param_file):
        # type: (str) -> list
        res = []

        # Each line of the stl_param_file contains the name of a parameter in the STL formula
        try:
            f = open(stl_param_file, 'rb')
            res = [line.replace(' ', '') for line in f]
            f.close()
        except IOError:
            ParOracle.logger.warning('Parameter STL file does not appear to exist.')
        finally:
            return res

    def replace_par_val_stl_formula(self, xpoint):
        # type: (OracleSTL, tuple) -> str
        # The number of parameters in the STL formula should be less or equal than
        # the number of coordinates in the tuple
        assert self.dim() <= len(xpoint)

        def eval_expr(match):
            # Evaluate the arithmetic expression detected by 'match'
            res = 0
            try:
                res = str(eval(match.group(0)))
            except SyntaxError:
                ParOracle.logger.error('Syntax error: {0}'.format(str(match)))
            finally:
                return res
            # return str(eval(match.group(0)))
            # return str(eval(match.group('expr')))

        ####
        # Regex for detecting an arithmetic expression inside a STL formula
        # number = '([+-]?(\d+(\.\d*)?)|(\.\d+))'
        number = '([+-]?(\d+(\.\d*)?)|(\.\d+))([eE][-+]?\d+)?'
        op = '(\*|\/|\+|\-)+'
        math_regex = r'(\b{0}\b({1}\b{2}\b)*)'.format(number, op, number)
        # math_regex = r'(\b%s\b(%s\b%s\b)*)' % (number, op, number)
        # math_regex = r'(?P<expr>\b%s\b(%s\b%s\b)*)' % (number, op, number)
        pattern = re.compile(math_regex)
        ####

        f = open(self.stl_prop_file, 'r')
        stl_prop_file_subst = tempfile.NamedTemporaryFile(mode='w', delete=False)
        stl_prop_file_subst_name = stl_prop_file_subst.name

        for line in f:
            for i, par in enumerate(self.stl_parameters):
                line = re.sub(r'\b{0}\b'.format(par), str(xpoint[i]), line)

            line = pattern.sub(eval_expr, line)
            stl_prop_file_subst.write(line)

        f.close()
        stl_prop_file_subst.close()

        return stl_prop_file_subst_name

    def eval_stl_formula(self, stl_prop_file):
        # type: (OracleSTL, str) -> str

        # File having the result of the STL property evaluation over the signal
        # temp_dir = tempfile.gettempdir()
        # temp_name = next(tempfile._get_candidate_names())
        # result_file_name = os.path.join(temp_dir, temp_name)
        result_file_name = tempfile.mktemp()

        try:
            # java -jar ./jamt.jar -x ./stl_prop_file.stl -s ./vcd_signal_file.vcd -a ./variables.alias -v out

            # command = ['java', '-jar', 'jamt.jar',
            # '-x', stl_prop_file, '-s', vcd_signal_file, '-a', var_alias_file, '-v', result_filename]
            command = [JAVA_BIN, JAVA_OPT_JAR, JAMT_BIN,
                       JAMT_OPT_STL, stl_prop_file,
                       JAMT_OPT_SIGNAL, self.vcd_signal_file,
                       JAMT_OPT_ALIAS, self.var_alias_file,
                       JAMT_OPT_RES, result_file_name]

            DEVNULL = open(os.path.devnull, 'w')
            # subprocess.call(command)
            subprocess.check_output(command, stderr=DEVNULL, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            message = 'Running "{0}" raised an exception'.format(' '.join(e.cmd))
            print(message)
            # raise RuntimeError(message)
        finally:
            # Return the result of evaluating the STL formula
            return result_file_name

    @staticmethod
    def parse_amt_result(res_file):
        # type: (str) -> (bool, bool)
        #
        # CSV format of the AMT result file:
        # Assertion, Verdict
        # assrt1, res1
        # assrt2, res2
        # ...
        # assrtn, resn
        #
        # where 'res_i' in {'violated', 'satisfied', 'unknown'}
        tp_result = {'violated': False, 'satisfied': True, 'unknown': None}

        # Remove empty spaces for each file line
        f = open(res_file, 'rb')
        f2 = (line.replace(' ', '') for line in f)

        # The first line of the CSV file defines the keys for accessing the values in the following entries
        # fieldnames = ['assert', 'result']
        # reader = csv.DictReader(f, fieldnames=fieldnames)
        reader = csv.DictReader(f2)

        # Last column of the CSV file contains the result of the evaluation
        key_veredict = reader.fieldnames[-1]

        # Process the result of the assertions
        # _eval_list = (tp_result[line[key_veredict]] for line in reader)
        _eval_list = [tp_result[line[key_veredict]] for line in reader]

        # All conditions are true (i.e., 'and' policy)
        _eval = all(_eval_list)

        # Any condition is true (i.e., 'or' policy)
        # _eval = any(_eval_list)

        # Check if there is any 'unknown' value
        _unknown_list = [unk for unk in _eval_list if unk is None]
        delete = len(_unknown_list) == 0

        f.close()

        return _eval, delete

    # Membership functions
    def __contains__(self, p):
        # type: (OracleSTL, tuple) -> bool
        return self.member(p) is True

    def member(self, xpoint):
        # type: (OracleSTL, tuple) -> bool

        assert self.stl_prop_file != ''
        assert self.vcd_signal_file != ''
        assert self.var_alias_file != ''
        assert self.stl_parameters != []

        # Invokation example of the monitoring tool (AMT).
        # AMT evaluates a STL formula (.stl) over a signal (.vcd) following a variable aliasing (.alias)
        # and exports the result to an output file (out).
        #
        # java -jar ./jamt.jar -x ./stl_formula.stl -s ./signal.vcd -a ./variables.alias -v out
        #

        # Replace parameters of the STL formula with current values in xpoint tuple
        stl_prop_file_subst_name = self.replace_par_val_stl_formula(xpoint)

        # Invoke AMT for solving the STL formula for the current values for the parameters
        result_file_name = self.eval_stl_formula(stl_prop_file_subst_name)

        # Parse the AMT result
        res, delet = OracleSTL.parse_amt_result(result_file_name)

        # Remove temporal files
        if delet:
            os.remove(stl_prop_file_subst_name)
            os.remove(result_file_name)
        else:
            ParOracle.logger.warning(
                'Evaluation of file {0} returns "unkown" (see {1}).'.format(stl_prop_file_subst_name,
                                                                            result_file_name))

        return res

    def membership(self):
        # type: (OracleSTL) -> callable
        return lambda xpoint: self.member(xpoint)

    # Read/Write file functions
    def from_file_binary(self, finput=None):
        # type: (OracleSTL, io.BinaryIO) -> None
        assert (finput is not None), 'File object should not be null'

        try:
            # self.stl_prop_file = pickle.load(finput)
            # self.vcd_signal_file = pickle.load(finput)
            # self.var_alias_file = pickle.load(finput)
            # self.stl_parameters = pickle.load(finput)

            # self.stl_prop_file = os.path.abspath(pickle.load(finput))
            # self.vcd_signal_file = os.path.abspath(pickle.load(finput))
            # self.var_alias_file = os.path.abspath(pickle.load(finput))
            # self.stl_parameters = pickle.load(finput)

            current_path = os.path.dirname(os.path.abspath(finput.name))
            path = pickle.load(finput)
            self.stl_prop_file = os.path.join(current_path, path) if not os.path.isabs(path) else path
            path = pickle.load(finput)
            self.vcd_signal_file = os.path.join(current_path, path) if not os.path.isabs(path) else path
            path = pickle.load(finput)
            self.var_alias_file = os.path.join(current_path, path) if not os.path.isabs(path) else path
            self.stl_parameters = pickle.load(finput)

            fname_list = (self.stl_prop_file, self.vcd_signal_file, self.var_alias_file)
            for fname in fname_list:
                if not os.path.isfile(fname):
                    ParOracle.logger.info('File {0} does not exists or it is not a file'.format(fname))

        except EOFError:
            ParOracle.logger.error('Unexpected error when loading {0}: {1}'.format(finput, sys.exc_info()[0]))

    def from_file_text(self, finput=None):
        # type: (OracleSTL, io.BinaryIO) -> None
        assert (finput is not None), 'File object should not be null'

        try:
            # self.stl_prop_file = finput.readline().strip(' \n\t')
            # self.vcd_signal_file = finput.readline().strip(' \n\t')
            # self.var_alias_file = finput.readline().strip(' \n\t')
            # self.stl_parameters = ast.literal_eval(finput.readline().strip(' \n\t'))

            # self.stl_prop_file = os.path.abspath(finput.readline().strip(' \n\t'))
            # self.vcd_signal_file = os.path.abspath(finput.readline().strip(' \n\t'))
            # self.var_alias_file = os.path.abspath(finput.readline().strip(' \n\t'))
            # self.stl_parameters = ast.literal_eval(finput.readline().strip(' \n\t'))

            # Each file line contains the path to a configuration file required by JAMT.
            # If it is a relative path, we calculate the absolute path.
            # If it is a absolute path, we do nothing.

            current_path = os.path.dirname(os.path.abspath(finput.name))
            path = finput.readline().strip(' \n\t')
            self.stl_prop_file = os.path.join(current_path, path) if not os.path.isabs(path) else path
            path = finput.readline().strip(' \n\t')
            self.vcd_signal_file = os.path.join(current_path, path) if not os.path.isabs(path) else path
            path = finput.readline().strip(' \n\t')
            self.var_alias_file = os.path.join(current_path, path) if not os.path.isabs(path) else path
            self.stl_parameters = ast.literal_eval(finput.readline().strip(' \n\t'))

            fname_list = (self.stl_prop_file, self.vcd_signal_file, self.var_alias_file)
            for fname in fname_list:
                if not os.path.isfile(fname):
                    ParOracle.logger.info('File {0} does not exists or it is not a file'.format(fname))

        except EOFError:
            ParOracle.logger.error('Unexpected error when loading {0}: {1}'.format(finput, sys.exc_info()[0]))

    def to_file_binary(self, foutput=None):
        # type: (OracleSTL, io.BinaryIO) -> None
        assert (foutput is not None), 'File object should not be null'

        pickle.dump(os.path.abspath(self.stl_prop_file), foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(os.path.abspath(self.vcd_signal_file), foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(os.path.abspath(self.var_alias_file), foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(self.stl_parameters, foutput, pickle.HIGHEST_PROTOCOL)

    def to_file_text(self, foutput=None):
        # type: (OracleSTL, io.BinaryIO) -> None
        assert (foutput is not None), 'File object should not be null'

        foutput.write(os.path.abspath(self.stl_prop_file) + '\n')
        foutput.write(os.path.abspath(self.vcd_signal_file) + '\n')
        foutput.write(os.path.abspath(self.var_alias_file) + '\n')
        foutput.write(str(self.stl_parameters) + '\n')
