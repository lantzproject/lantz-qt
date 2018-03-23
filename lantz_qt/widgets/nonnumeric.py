# -*- coding: utf-8 -*-
"""
    lantz.widgets.nonnumeric
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Non-umeric widgets.
    - QComboBox
    - QCheckBox
    - QQLineEdit

    :copyright: 2018 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from lantz_core.helpers import MISSING

from ..utils.qt import QtGui
from .common import WidgetMixin, register_wrapper


@register_wrapper
class QComboBoxMixin(WidgetMixin):

    _WRAPPED = (QtGui.QComboBox, )

    @classmethod
    def _wrap(cls, widget):
        super()._wrap(widget)
        widget.valueChanged = widget.currentIndexChanged

    def value(self):
        return self.currentText()

    def setValue(self, value):
        if value is MISSING:
            font = QtGui.QFont()
            font.setItalic(True)
            self.setFont(font)
            return
        self.setCurrentIndex(self.__values.index(value))

    def setReadOnly(self, value):
        self.setEnabled(not value)

    def bind_feat(self, feat):
        super().bind_feat(feat)
        if isinstance(self._feat.values, dict):
            self.__values = list(self._feat.values.keys())
        else:
            self.__values = list(self.__values)
        self.clear()
        self.addItems([str(value) for value in self.__values])


@register_wrapper
class QCheckBoxMixin(WidgetMixin):

    _WRAPPED = (QtGui.QCheckBox, )

    @classmethod
    def _wrap(cls, widget):
        super()._wrap(widget)
        widget.valueChanged = widget.stateChanged

    def setReadOnly(self, value):
        self.setCheckable(not value)

    def value(self):
        return self.isChecked()

    def setValue(self, value):
        if value is MISSING:
            return
        self.setChecked(value)


@register_wrapper
class QLineEditMixin(WidgetMixin):

    _WRAPPED = (QtGui.QLineEdit, )

    @classmethod
    def _wrap(cls, widget):
        super()._wrap(widget)
        widget.valueChanged = widget.textChanged

    def value(self):
        return self.text()

    def setValue(self, value):
        if value is MISSING:
            return
        return self.setText(value)


