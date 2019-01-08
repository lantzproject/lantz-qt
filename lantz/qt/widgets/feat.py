# -*- coding: utf-8 -*-
"""
    lantz.widgets.feat
    ~~~~~~~~~~~~~~~~~~

    Widgets to wrap Feat and DictFeat

    :copyright: 2018 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

import inspect

from lantz.core.feat import DictFeat, DictFeatProxy
from lantz.core.helpers import UNSET, MISSING

from ..utils.qt import QtCore, QtGui
from .common import WidgetMixin


class FeatWidget(object):
    """Widget to show a Feat.

    Parameters
    ----------
    parent :
        parent widget.
    target :
        driver object to connect.
    feat :
        DictFeat to connect.
    """


    def __new__(cls, parent, target, feat):
        widget = WidgetMixin.from_feat(feat, parent)
        widget.bind_feat(feat)
        widget.lanz_target = target
        return widget


class DictFeatWidget(QtGui.QWidget):
    """Widget to show a DictFeat.

    Parameters
    ----------
    parent :
        parent widget.
    target :
        driver object to connect.
    feat :
        DictFeat to connect.
    """

    def __init__(self, parent, target, feat):
        super().__init__(parent)

        if isinstance(feat, DictFeatProxy):
            self._feat = feat.proxied
        elif isinstance(feat, DictFeat):
            self._feat = feat
        else:
            raise ValueError('feat argument must be an instance of DictFeat or DictFeatProxy, not %s' % feat.__class__)

        layout = QtGui.QHBoxLayout(self)

        if feat.keys:
            self._key_widget = QtGui.QComboBox()
            if isinstance(feat.keys, dict):
                self._keys = list(feat.keys.keys())
            else:
                self._keys = list(feat.keys)

            self._key_widget.addItems([str(key) for key in self._keys])
            self._key_widget.currentIndexChanged.connect(self._combobox_changed)
        else:
            self._key_widget = QtGui.QLineEdit()
            self._key_widget.textChanged.connect(self._lineedit_changed)

        layout.addWidget(self._key_widget)

        self._value_widget = WidgetMixin.from_feat(feat)
        self._value_widget.bind_feat(feat)
        self._value_widget.feat_key = self._keys[0] if self._keys else MISSING
        self._value_widget.lantz_target = target

        layout.addWidget(self._value_widget)

        self.widgets = (self._key_widget, self._value_widget)

    @QtCore.Slot(int)
    def _combobox_changed(self, value):
        self._value_widget.feat_key = self._keys[self._key_widget.currentIndex()]

    @QtCore.Slot(str)
    def _lineedit_changed(self, value):
        self._value_widget.feat_key = self._key_widget.text()

    def value(self):
        """Get widget value."""
        return self._value_widget.value()

    def setValue(self, value):
        """Set widget value."""
        if value is MISSING:
            return
        self._value_widget.setValue(value)

    def setReadOnly(self, value):
        """Set read only."""
        self._value_widget.setReadOnly(value)

    @property
    def lantz_target(self):
        """Driver connected to this widget."""
        return self._value_widget._lantz_target

    @lantz_target.setter
    def lantz_target(self, driver):
        self._value_widget._lantz_target = driver

    @property
    def update_on_change(self):
        return self._value_widget.update_on_change()

    @update_on_change.setter
    def update_on_change(self, value):
        self._value_widget.update_on_change = value

    @property
    def readable(self):
        """If the Feat associated with the widget can be read (get)."""
        return self._value_widget.readable

    @property
    def writable(self):
        """If the Feat associated with the widget can be written (set)."""
        return self._value_widget.writable

    def value_from_feat(self):
        return self._value_widget.value_from_feat()

    def value_to_feat(self):
        return self._value_widget.value_to_feat()

    @property
    def feat(self):
        return self._value_widget.feat

    def _as_update_value(self):
        # TODO: it would be nice to change this to `value`.
        return {self._value_widget.feat_key: self._value_widget.value()}


class LabeledFeatWidget(QtGui.QWidget):
    """Widget containing a label, a control, and a get a set button.

    Parameters
    ----------
    parent :
        parent widget.
    target :
        driver object to connect.
    feat :
        Feat to connect.
    """

    def __init__(self, parent, target, feat):
        super().__init__(parent)

        layout = QtGui.QHBoxLayout(self)

        self._label = QtGui.QLabel()
        self._label.setText(feat.name)
        self._label.setFixedWidth(120)
        self._label.setToolTip(inspect.getdoc(feat))
        layout.addWidget(self._label)

        if isinstance(feat, DictFeatProxy):
            self._widget = DictFeatWidget(parent, target, feat)
        else:
            self._widget = WidgetMixin.from_feat(feat)
            self._widget.bind_feat(feat)
            self._widget.lantz_target = target

        layout.addWidget(self._widget)

        self._get = QtGui.QPushButton()
        self._get.setText('get')
        self._get.setEnabled(self._widget.readable)
        self._get.setFixedWidth(60)
        layout.addWidget(self._get)

        self._set = QtGui.QPushButton()
        self._set.setText('set')
        self._set.setEnabled(self._widget.writable)
        self._set.setFixedWidth(60)
        layout.addWidget(self._set)

        self._get.clicked.connect(self.on_get_clicked)
        self._set.clicked.connect(self.on_set_clicked)
        self._widget._update_on_change = self._widget.writable

        self.widgets = (self._label, self._widget, self._get, self._set)

    @property
    def update_on_change(self):
        return self._widget.update_on_change()

    @update_on_change.setter
    def update_on_change(self, value):
        self._widget.update_on_change = value

    @property
    def feat(self):
        return self._widget.feat

    @property
    def label_width(self):
        """Width of the label"""
        return self._label.width

    @label_width.setter
    def label_width(self, value):
        self._label.setFixedWidth(value)

    @property
    def lantz_target(self):
        """Driver connected to this widget."""
        return self._widget._lantz_target

    @lantz_target.setter
    def lantz_target(self, driver):
        self._widget._lantz_target = driver

    @QtCore.Slot()
    def on_get_clicked(self):
        self._widget.value_from_feat()

    @QtCore.Slot()
    def on_set_clicked(self):
        font = QtGui.QFont()
        font.setItalic(False)
        self._widget.setFont(font)
        self._widget.value_to_feat()

    @property
    def readable(self):
        """If the Feat associated with the widget can be read (get)."""
        return self._widget.readable

    @property
    def writable(self):
        """If the Feat associated with the widget can be written (set)."""
        return self._widget.writable
