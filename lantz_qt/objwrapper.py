# -*- coding: utf-8 -*-
"""
    lantz.qt.app
    ~~~~~~~~~~~~

    Wraps a Lantz Driver in a PyQt object connecting `_changed` signals.

    :copyright: 2018 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from .utils.qt import QtCore


def wrap_driver(wrapped_obj, parent_qobj=None):

    class QObj(QtCore.QObject):

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
            return getattr(self.wrapped_obj, item)

        for feat_name in wrapped_obj.feats.keys():
            locals()[feat_name + '_py_on_changed'] = getattr(wrapped_obj, feat_name + '_on_changed')
            locals()[feat_name + '_on_changed'] = QtCore.pyqtSignal(object, object, object)

        for feat_name in wrapped_obj.dictfeats.keys():
            locals()[feat_name + '_py_on_changed'] = getattr(wrapped_obj, feat_name + '_on_changed')
            locals()[feat_name + '_on_changed'] = QtCore.pyqtSignal(object, object)


    obj = QObj(wrapped_obj, parent_qobj)

    for feat_name in wrapped_obj.lantz_features.keys():
        getattr(obj, feat_name + '_on_changed').connect(lambda x: getattr(obj, feat_name + '_py_on_changed').emit(x))

    return obj
