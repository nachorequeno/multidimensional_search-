#!/usr/bin/env bash
#pip2 uninstall ParetoLib
pip install -r requirements.txt
python setup.py clean --all
python setup.py build
python setup.py install --force --user
python setup.py test