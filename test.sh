#!/usr/bin/env bash
#pip2 uninstall ParetoLib
python setup.py clean --all
python setup.py build
python setup.py install --force --user
python setup.py test