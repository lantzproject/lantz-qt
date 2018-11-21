# -*- coding: utf-8 -*-
"""
    lantz.qt.config
    ~~~~~~~~~~~~~~~

    :copyright: 2018 by The Lantz Authors
    :license: BSD, see LICENSE for more details.
"""

import os

from lantz.core.config import register_and_get


# ====================================
# Configuration Values for lantz_sims
# ====================================

# Print the traceback when is not possible to create or bind a qt control.
# valid values: true, false
PRINT_TRACEBACK = register_and_get('qt.print_traceback', 'false') == 'true'

# Qt API wrapper to use in lantz.
# valid values: mock, pyqt, pyqt5, pyqtv1, pyqtdefault, pyside, pyside2
QT_API = register_and_get('qt.api', os.environ.get('QT_API', ''))
