# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""Oracle package.

This package introduces a set of Oracles supported by ParetoLib.
Class Oracle is a template that is instantiated by every Oracle
of the module.
"""

import logging

__name__ = 'Oracle'
__all__ = ['NDTree', 'Oracle', 'OracleFunction', 'OraclePoint', 'OracleSTL', 'OracleSTLe', 'OracleBio']

# Logging configuration
logging.basicConfig(format='%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
