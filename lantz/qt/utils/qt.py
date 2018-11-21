# -*- coding: utf-8 -*-
"""
    lantz.utils.qt
    ~~~~~~~~~~~~~~

    A Qt API selector that can be used to switch between PyQt and PySide.

    This uses the ETS 4.0 selection pattern of:
    PySide first, PyQt with API v2. second.

    Do not use this if you need PyQt with the old QString/QVariant API.

    Copied with modifications from the IPython Project.
    http://ipython.scipy.org/

    :copyright: IPython
    :license: BSD, see the IPython Project for more details.
"""

from .qt_loaders import (load_qt, QT_API_PYQT5, QT_API_PYSIDE2, QT_API_MOCK)
from .uic import build_loadUi

from ..config import QT_API

if QT_API:

    VALID = [QT_API_PYSIDE2, QT_API_PYQT5, QT_API_MOCK]

    if QT_API not in VALID:
        raise RuntimeError("Invalid Qt API %r, valid values are: %r or empty for system default." %
                           (QT_API, VALID))

    api_opts = [QT_API]
else:
    api_opts = [QT_API_PYQT5, ]

QtCore, QtGui, QtSvg, QT_API = load_qt(api_opts)

QtGui.loadUi, QtGui.loadUiType = build_loadUi(QT_API)

QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))


def superQ(QClass):
    """ Permits the use of super() in class hierarchies that contain Qt classes.
    Unlike QObject, SuperQObject does not accept a QObject parent. If it did,
    super could not be emulated properly (all other classes in the heierarchy
    would have to accept the parent argument--they don't, of course, because
    they don't inherit QObject.)
    This class is primarily useful for attaching signals to existing non-Qt
    classes. See QtKernelManagerMixin for an example.
    """
    class SuperQClass(QClass):

        def __new__(cls, *args, **kw):
            # We initialize QClass as early as possible. Without this, Qt complains
            # if SuperQClass is not the first class in the super class list.
            inst = QClass.__new__(cls)
            QClass.__init__(inst)
            return inst

        def __init__(self, *args, **kw):
            # Emulate super by calling the next method in the MRO, if there is one.
            mro = self.__class__.mro()
            for qt_class in QClass.mro():
                mro.remove(qt_class)
            next_index = mro.index(SuperQClass) + 1
            if next_index < len(mro):
                mro[next_index].__init__(self, *args, **kw)

    return SuperQClass


SuperQObject = superQ(QtCore.QObject)
MetaQObject = type(QtCore.QObject)
