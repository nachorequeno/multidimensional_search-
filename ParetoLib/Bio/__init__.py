# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""Bio package.

This module acts as an interface to all biological models
that are available to OracleBio3D.
"""

import logging

__name__ = 'Bio'
__all__ = ['SSA_LRI_MFPT1']

# Logging configuration
# logging.basicConfig(format='%(message)s', level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
#logger.setLevel(logging.ERROR)

# Create handlers
handler = logging.StreamHandler()

# Create formatter and add it to handler
form = logging.Formatter('%(message)s')
handler.setFormatter(form)

# Add handler to the logger
logger.addHandler(handler)