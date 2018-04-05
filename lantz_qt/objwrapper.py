# -*- coding: utf-8 -*-
"""
    lantz.qt.app
    ~~~~~~~~~~~~

    Wraps a Lantz Driver in a PyQt object connecting `_changed` signals.

    :copyright: 2018 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from .utils.qt import QtCore, SuperQObject


class QDriver(QtCore.QObject):
    pass


def wrap_driver(wrapped_obj, parent_qobj=None):

    SUFFIX = '_changed'
    PYSUFFIX = '_py_changed'

    class QObj(QDriver):

        def __init__(self, obj, parent):
            super().__init__(parent)
            self.wrapped_obj = obj

        # Qt Signals need to be added to the class before it is created.
        # We loop through all members of the class and add a changed event
        # for each Feat/DictFeat.

        # We do the same thing for all base classes which are not derived from
        # Driver (checking for the attribute _lantz_feats) to enable base clases
        # for drivers that do not derive from Driver.

        def __getattr__(self, item):
            if item in self.__dict__:
                return getattr(self, item)

            return getattr(self.wrapped_obj, item)

        for feat_name in wrapped_obj.feats.keys():
            #locals()[feat_name + PYSUFFIX] = getattr(wrapped_obj, feat_name + SUFFIX)
            locals()[feat_name + SUFFIX] = QtCore.pyqtSignal(object, object)

        for feat_name in wrapped_obj.dictfeats.keys():
            #locals()[feat_name + PYSUFFIX] = getattr(wrapped_obj, feat_name + SUFFIX)
            locals()[feat_name + SUFFIX] = QtCore.pyqtSignal(object, object, object)

    obj = QObj(wrapped_obj, parent_qobj)

    return obj


def wrap_driver_cls(wrapped_cls):

    SUFFIX = '_changed'
    PYSUFFIX = '_py_changed'

    class WrappedCLS(wrapped_cls, SuperQObject):

        # Qt Signals need to be added to the class before it is created.
        # We loop through all members of the class and add a changed event
        # for each Feat/DictFeat.

        for feat_name in wrapped_cls._lantz_feats.keys():
            #locals()[feat_name + PYSUFFIX] = getattr(wrapped_obj, feat_name + SUFFIX)
            locals()[feat_name + SUFFIX] = QtCore.pyqtSignal(object, object)

        for feat_name in wrapped_cls._lantz_dictfeats.keys():
            #locals()[feat_name + PYSUFFIX] = getattr(wrapped_obj, feat_name + SUFFIX)
            locals()[feat_name + SUFFIX] = QtCore.pyqtSignal(object, object, object)

    WrappedCLS.__name__ = 'Qt' + wrapped_cls.__name__

    return WrappedCLS
