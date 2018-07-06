import re
import pickle
import subprocess
import tempfile
import csv
import ast

from ParetoLib.Oracle.Oracle import Oracle
from ParetoLib.JAMT.JAMT import *

# from ParetoLib.Oracle import vprint
from . import vprint, eprint

class OracleSTL(Oracle):
    def __init__(self, stl_prop_file="", vcd_signal_file="", var_alias_file="", stl_param_file=""):
        # type: (OracleSTL, str, str, str, str) -> None
        #assert stl_prop_file != ""
        #assert vcd_signal_file != ""
        #assert var_alias_file != ""
        #assert stl_param_file != ""

        Oracle.__init__(self)

        self.stl_prop_file = stl_prop_file.strip(' \n\t')
        self.vcd_signal_file = vcd_signal_file.strip(' \n\t')
        self.var_alias_file = var_alias_file.strip(' \n\t')
        #self.stl_parameters = self.get_parameters_stl(stl_param_file) if stl_param_file != "" else []
        self.stl_parameters = self.get_parameters_stl(stl_param_file.strip(' \n\t'))

    # Printers
    def __repr__(self):
        # type: (OracleSTL) -> str
        return self.toStr()

    def __str__(self):
        # type: (OracleSTL) -> str
        return self.toStr()

    def toStr(self):
        # type: (OracleSTL) -> str
        s = "STL property file: %s\n" % self.stl_prop_file
        s += "STL alias file: %s\n" % self.var_alias_file
        s += "STL parameters file: %s\n" % self.stl_parameters
        s += "VCD signal file: %s\n" % self.vcd_signal_file
        return s

    # Equality functions
    def __eq__(self, other):
        # type: (OracleSTL, OracleSTL) -> bool
        # return hash(self) == hash(other)
        return (self.stl_prop_file == other.stl_prop_file) and \
               (self.vcd_signal_file == other.vcd_signal_file) and \
               (self.var_alias_file == other.var_alias_file) and \
               (self.stl_parameters == other.stl_parameters)

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

    def get_parameters_stl(self, stl_param_file):
        # type: (OracleSTL, str) -> list

        # Each line of the stl_param_file contains the name of a parameter in the STL formula
        try:
            f = open(stl_param_file, 'rb')
            res = [line.replace(" ", "") for line in f]
            f.close()
        except IOError:
            print "Warning: Parameter STL file does not appear to exist."
            res = []

        return res

    def replace_par_val_STL_formula(self, xpoint):
        # type: (OracleSTL, tuple) -> str
        # The number of parameters in the STL formula should be less or equal than the number of coordinates in the tuple
        assert self.dim() <= len(xpoint)

        def eval_expr(match):
            # Evaluate the arithmetic expression detected by 'match'
            try:
                res = str(eval(match.group(0)))
            except:
                print "Unexpected error:", match
                raise
            else:
                return res
            #return str(eval(match.group(0)))
            #return str(eval(match.group('expr')))

        ####
        # Regex for detecting an arithmetic expression inside a STL formula
        #number = '([+-]?(\d+(\.\d*)?)|(\.\d+))'
        number = '([+-]?(\d+(\.\d*)?)|(\.\d+))([eE][-+]?\d+)?'
        op = '(\*|\/|\+|\-)+'
        math_regex = r'(\b%s\b(%s\b%s\b)*)' % (number, op, number)
        # math_regex = r'(?P<expr>\b%s\b(%s\b%s\b)*)' % (number, op, number)
        pattern = re.compile(math_regex)
        ####

        f = open(self.stl_prop_file, 'r')
        stl_prop_file_subst = tempfile.NamedTemporaryFile(mode='w', delete=False)
        stl_prop_file_subst_name = stl_prop_file_subst.name

        for line in f:
            for i, par in enumerate(self.stl_parameters):
                line = re.sub(r"\b%s\b" % par, str(xpoint[i]), line)

            line = pattern.sub(eval_expr, line)
            stl_prop_file_subst.write(line)

        f.close()
        stl_prop_file_subst.close()

        return stl_prop_file_subst_name


    def eval_STL_formula(self, stl_prop_file):
        # type: (OracleSTL, str) -> str

        # File having the result of the STL property evaluation over the signal
        temp_dir = tempfile._get_default_tempdir()
        temp_name = next(tempfile._get_candidate_names())
        result_file_name = os.path.join(temp_dir, temp_name)

        try:
            # java -jar ./jamt.jar - x ./stab/stabilization.stl -s ./stab/stabilization.vcd -a ./stab/stabilization.alias -v out

            #command = ["java", "-jar", "jamt.jar", "-x", stl_prop_file, "-s", self.vcd_signal_file, "-a",
            command = [JAVA_BIN, JAVA_OPT_JAR, JAMT_BIN,
                       JAMT_OPT_STL, stl_prop_file,
                       JAMT_OPT_SIGNAL, self.vcd_signal_file,
                       JAMT_OPT_ALIAS, self.var_alias_file,
                       JAMT_OPT_RES, result_file_name]

            DEVNULL = open(os.path.devnull, 'w')
            #subprocess.call(command)
            output = subprocess.check_output(command, stderr=DEVNULL, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            message = 'Running "{}" raised an exception'.format(' '.join(e.cmd))
            raise RuntimeError(message)
        else:
            # Return the result of evaluating the STL formula
            return result_file_name


    def parse_AMT_result(self, res_file):
        # type: (OracleSTL, str) -> (bool, bool)
        #
        # CSV format of the AMT result file:
        # Assertion, Verdict
        # assrt1, res1
        # assrt2, res2
        # ...
        # assrtn, resn
        #
        # where 'res_i' in {"violated", "satisfied"}
        tp_result = {"violated": False, "satisfied": True, "unknown": None}

        # Remove empty spaces for each file line
        f = open(res_file, 'rb')
        f2 = (line.replace(" ", "") for line in f)

        # The first line of the CSV file defines the keys for accessing the values in the following entries
        # fieldnames = ['assert', 'result']
        # reader = csv.DictReader(f, fieldnames=fieldnames)
        reader = csv.DictReader(f2)

        # Last column of the CSV file contains the result of the evaluation
        key_veredict = reader.fieldnames[-1]

        # Process the result of the assertions
        #_eval_list = (tp_result[line[key_veredict]] for line in reader)
        _eval_list = [tp_result[line[key_veredict]] for line in reader]

        # All conditions are true (i.e., 'and' policy)
        _eval = all(_eval_list)

        # Any condition is true (i.e., 'or' policy)
        # _eval = any(_eval_list)

        # Check if there is any "unknown" value
        _unknown_list = [unk for unk in _eval_list if unk is None]
        delet = len(_unknown_list) == 0

        f.close()

        return _eval, delet

    # Membership functions
    def __contains__(self, p):
        # type: (OracleSTL, tuple) -> bool
        return self.member(p) is True

    def member(self, xpoint):
        # type: (OracleSTL, tuple) -> bool

        assert self.stl_prop_file != ""
        assert self.vcd_signal_file != ""
        assert self.var_alias_file != ""
        assert self.stl_parameters != []

        # Invokation example of the monitoring tool (AMT).
        # AMT evaluates a STL formula (.stl) over a signal (.vcd) following a variable aliasing (.alias)
        # and exports the result to an output file (out).
        #
        # java -jar ./jamt.jar -x ./stab/stabilization.stl -s ./stab/stabilization.vcd -a ./stab/stabilization.alias -v out
        #

        # Replace parameters of the STL formula with current values in xpoint tuple
        stl_prop_file_subst_name = self.replace_par_val_STL_formula(xpoint)

        # Invoke AMT for solving the STL formula for the current values for the parameters
        result_file_name = self.eval_STL_formula(stl_prop_file_subst_name)

        # Parse the AMT result
        res, delet = self.parse_AMT_result(result_file_name)

        #
        # print res
        # Remove temporal files
        if delet:
            os.remove(stl_prop_file_subst_name)
            os.remove(result_file_name)
        else:
            print "Warning! Evaluation of file %s returns 'unkown' (see %s)." % (stl_prop_file_subst_name, result_file_name)

        return res

    def membership(self):
        # type: (OracleSTL) -> function
        return lambda xpoint: self.member(xpoint)

    # Read/Write file functions
    def fromFileNonHumRead(self, finput=None):
        # type: (OracleSTL, BinaryIO) -> None
        assert (finput is not None), "File object should not be null"

        self.stl_prop_file = pickle.load(finput)
        self.vcd_signal_file = pickle.load(finput)
        self.var_alias_file = pickle.load(finput)
        self.stl_parameters = pickle.load(finput)

    def fromFileHumRead(self, finput=None):
        # type: (OracleSTL, BinaryIO) -> None
        assert (finput is not None), "File object should not be null"

        self.stl_prop_file = finput.readline().strip(' \n\t')
        self.vcd_signal_file = finput.readline().strip(' \n\t')
        self.var_alias_file = finput.readline().strip(' \n\t')
        self.stl_parameters = ast.literal_eval(finput.readline().strip(' \n\t'))


    def toFileNonHumRead(self, foutput=None):
        # type: (OracleSTL, BinaryIO) -> None
        assert (foutput is not None), "File object should not be null"

        pickle.dump(self.stl_prop_file, foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(self.vcd_signal_file, foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(self.var_alias_file, foutput, pickle.HIGHEST_PROTOCOL)
        pickle.dump(self.stl_parameters, foutput, pickle.HIGHEST_PROTOCOL)

    def toFileHumRead(self, foutput=None):
        # type: (OracleSTL, BinaryIO) -> None
        assert (foutput is not None), "File object should not be null"

        foutput.write(self.stl_prop_file + '\n')
        foutput.write(self.vcd_signal_file + '\n')
        foutput.write(self.var_alias_file + '\n')
        foutput.write(str(self.stl_parameters) + '\n')