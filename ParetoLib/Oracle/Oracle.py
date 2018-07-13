import os
import io


# Oracle template

class Oracle:

    # Dimension = [0,..,n-1]
    def __init__(self):
        pass

    # Printers
    def __repr__(self):
        # type: (Oracle) -> str
        return ''

    def __str__(self):
        # type: (Oracle) -> str
        return ''

    # Equality functions
    def __eq__(self, other):
        # type: (Oracle, Oracle) -> bool
        return False

    def __ne__(self, other):
        # type: (Oracle, Oracle) -> bool
        return not self.__eq__(other)

    # Identity function (via hashing)
    def __hash__(self):
        # type: (Oracle) -> int
        return 0

    def dim(self):
        # type: (Oracle) -> int
        return 0

    # Name of the parameters/variables whose validity domain the Pareto search wants to infer
    def get_var_names(self):
        # type: (Oracle) -> list
        # If parameter names are not provided, then we use lexicographic characters by default.
        return [chr(i) for i in range(ord('a'), ord('z') + 1)]

    # Membership functions
    def __contains__(self, point):
        # type: (Oracle, tuple) -> bool
        return self.member(point) is True

    def member(self, point):
        # type: (Oracle, tuple) -> bool
        return False

    def membership(self):
        # type: (Oracle) -> callable
        return lambda point: self.member(point)

    # Read/Write file functions
    def from_file(self, fname='', human_readable=False):
        # type: (Oracle, str, bool) -> None
        assert (fname != ''), 'Filename should not be null'
        assert os.path.isfile(fname), 'File {0} does not exists or it is not a file'.format(fname)

        mode = 'r'
        if human_readable:
            finput = open(fname, mode)
            self.from_file_text(finput)
        else:
            mode = mode + 'b'
            finput = open(fname, mode)
            self.from_file_binary(finput)
        finput.close()

    def from_file_binary(self, finput=None):
        # type: (Oracle, io.BinaryIO) -> None
        pass

    def from_file_text(self, finput=None):
        # type: (Oracle, io.BinaryIO) -> None
        pass

    def to_file(self, fname='', append=False, human_readable=False):
        # type: (Oracle, str, bool, bool) -> None
        assert (fname != ''), 'Filename should not be null'

        if append:
            mode = 'a'
        else:
            mode = 'w'

        if human_readable:
            foutput = open(fname, mode)
            self.to_file_text(foutput)
        else:
            mode = mode + 'b'
            foutput = open(fname, mode)
            self.to_file_binary(foutput)
        foutput.close()

    def to_file_binary(self, foutput=None):
        # type: (Oracle, io.BinaryIO) -> None
        pass

    def to_file_text(self, foutput=None):
        # type: (Oracle, io.BinaryIO) -> None
        pass
