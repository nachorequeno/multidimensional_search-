# Oracle template

class Oracle:

    # Dimension = [0,..,n-1]
    def __init__(self):
        None

    # Printers
    def __repr__(self):
        # type: (Oracle) -> str
        return ""

    def __str__(self):
        # type: (Oracle) -> str
        return ""

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

    # Membership functions
    def __contains__(self, point):
        # type: (Oracle, tuple) -> bool
        return self.member(point) is True

    def member(self, point):
        # type: (Oracle, tuple) -> bool
        return False

    def membership(self):
        # type: (Oracle) -> function
        return lambda point: self.member(point)

    # Read/Write file functions
    def fromFile(self, fname='', human_readable=False):
        # type: (Oracle, str, bool) -> None
        assert (fname != ''), "Filename should not be null"

        mode = 'rb'
        finput = open(fname, mode)
        if human_readable:
            self.fromFileHumRead(finput)
        else:
            self.fromFileNonHumRead(finput)
        finput.close()

    def fromFileNonHumRead(self, finput=None):
        # type: (Oracle, BinaryIO) -> None
        return None

    def fromFileHumRead(self, finput=None):
        # type: (Oracle, BinaryIO) -> None
        return None

    def toFile(self, fname='', append=False, human_readable=False):
        # type: (Oracle, str, bool, bool) -> None
        assert (fname != ''), "Filename should not be null"

        if append:
            mode = 'ab'
        else:
            mode = 'wb'

        foutput = open(fname, mode)
        if human_readable:
            self.toFileHumRead(foutput)
        else:
            self.toFileNonHumRead(foutput)
        foutput.close()

    def toFileNonHumRead(self, foutput=None):
        # type: (Oracle, BinaryIO) -> None
        return None

    def toFileHumRead(self, foutput=None):
        # type: (Oracle, BinaryIO) -> None
        return None
