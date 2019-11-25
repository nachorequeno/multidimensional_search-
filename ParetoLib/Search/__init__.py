# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""Search package.

This package implements the algorithms for discovering the
Pareto front.
"""

import logging

__name__ = 'Search'
__all__ = ['CommonSearch', 'SeqSearch', 'ParSearch', 'Search', 'ResultSet', 'ParResultSet']

# Logging configuration
# logging.basicConfig(format='%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handlers
handler = logging.StreamHandler()

# Create formatter and add it to handler
form = logging.Formatter('%(message)s')
handler.setFormatter(form)

# Add handler to the logger
logger.addHandler(handler)
