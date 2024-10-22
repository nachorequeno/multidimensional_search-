# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# File :  LocalTempDir.py
# Last version :  v0.1 ( 10/Oct/2013 )
# Description :  Definition and implementation of the class 'TemporaryDirectory'
#       needed when using Python 2.7 (included in Python 3.3 or newer).
#       Extracted from:
#  http://stackoverflow.com/questions/19296146/with-tempfile-temporarydirectory
# -------------------------------------------------------------------------------
# Historical report :
#
#   DATE :  10/Oct/2013
#   VERSION :  v0.1
#   AUTHOR(s) :  Leonardo.Z
#
# -------------------------------------------------------------------------------

from __future__ import print_function

import warnings as _warnings
import os as _os

from tempfile import mkdtemp


# -------------------------------------------------------------------------------

class TemporaryDirectory(object):
    """Create and return a temporary directory.  This has the same
    behavior as mkdtemp but can be used as a context manager.  For
    example:

        with TemporaryDirectory() as tmpdir:
            ...

    Upon exiting the context, the directory and everything contained
    in it are removed.
    """

    def __init__(self, suffix="", prefix="tmp", dir=None):
        self._closed = False
        self.name = None  # Handle mkdtemp raising an exception
        self.name = mkdtemp(suffix, prefix, dir)

    def __repr__(self):
        return ("<{} {!r}>".format(self.__class__.__name__, self.name))

    def __enter__(self):
        return (self.name)

    def cleanup(self, _warn=False):
        if (self.name and not self._closed):
            try:
                self._rmtree(self.name)
            except (TypeError, AttributeError) as ex:
                # Issue #10188: Emit a warning on stderr
                # if the directory could not be cleaned
                # up due to missing globals
                if "None" not in str(ex):
                    raise
                print("ERROR: {!r} while cleaning up {!r}".format(ex, self, ),
                      file=_sys.stderr)
                return
            self._closed = True
            if (_warn):
                self._warn("Implicitly cleaning up {!r}".format(self))

    def __exit__(self, exc, value, tb):
        self.cleanup()

    def __del__(self):
        # Issue a warning if implicit cleanup needed
        self.cleanup()

    # XXX (ncoghlan): The following code attempts to make
    # this class tolerant of the module nulling out process
    # that happens during CPython interpreter shutdown
    # Alas, it doesn't actually manage it. See issue #10188
    _listdir = staticmethod(_os.listdir)
    _path_join = staticmethod(_os.path.join)
    _isdir = staticmethod(_os.path.isdir)
    _islink = staticmethod(_os.path.islink)
    _remove = staticmethod(_os.remove)
    _rmdir = staticmethod(_os.rmdir)
    _warn = _warnings.warn

    def _rmtree(self, path):
        # Essentially a stripped down version of shutil.rmtree.  We can't
        # use globals because they may be None'ed out at shutdown.
        for name in self._listdir(path):
            fullname = self._path_join(path, name)
            try:
                isdir = self._isdir(fullname) and not self._islink(fullname)
            except OSError:
                isdir = False
            if (isdir):
                self._rmtree(fullname)
            else:
                try:
                    self._remove(fullname)
                except OSError:
                    pass
        try:
            self._rmdir(path)
        except OSError:
            pass

# -------------------------------------------------------------------------------
