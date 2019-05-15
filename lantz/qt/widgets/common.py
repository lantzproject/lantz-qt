# -*- coding: utf-8 -*-
"""
    lantz.widgets.common
    ~~~~~~~~~~~~~~~~~~~~

    Common methods and classes to make PyQt widgets compatible with Lantz.

    :copyright: 2018 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from lantz.core.helpers import UNSET, MISSING

from lantz.core.feat import FeatProxy, DictFeatProxy, Feat, DictFeat
from ..log import LOGGER
from ..utils import LANTZ_BUILDING_DOCS
from ..utils.qt import QtGui


def register_wrapper(cls):
    """Register a class as lantz wrapper for QWidget subclasses.
    
    The class must contain a field (_WRAPPERS) with a tuple of the
    QWidget subclasses that it wraps.

    Parameters
    ----------

    Returns
    -------

    """
    for wrapped in cls._WRAPPED:
        if wrapped in cls._WRAPPERS:
            LOGGER.warn('{} is already registered to {}.'.format(wrapped, cls._WRAPPERS[wrapped]))

        if LANTZ_BUILDING_DOCS:
            cls._WRAPPERS[wrapped] = type(wrapped.__name__ + 'Wrapped',
                                          (cls, ), {'_IS_LANTZ_WRAPPER': True})
        else:
            cls._WRAPPERS[wrapped] = type(wrapped.__name__ + 'Wrapped',
                                          (cls, wrapped), {'_IS_LANTZ_WRAPPER': True})

    return cls


@register_wrapper
class WidgetMixin(object):
    """Mixin class to provide extra functionality to QWidget derived controls.
    
    Derived class must override _WRAPPED to indicate with which classes it
    can be mixed.
    
    To wrap an existing widget object use::
    
    
    If you want lantz to provide an appropriate wrapped widget for a given feat::
    
    
    In any case, after wrapping a widget you need to bind it to a feat::
    
    
    Finally, you need to

    Parameters
    ----------

    Returns
    -------

    >>> widget = QComboBox()
    >>> WidgetMixin.wrap(widget)
    
    >>> widget = WidgetMixin.from_feat(feat)
    
    >>> feat = driver.feats[feat_name]
    >>> widget.bind_feat(feat)
    
    >>> widget.lantz_target = driver
    """

    _WRAPPED = (QtGui.QWidget, )

    #: Dictionary linking Widget types with the function to patch them
    _WRAPPERS = {}

    _update_on_change = False

    def keyPressEvent(self, event):
        """When 'u' is pressed, request new units.
        When 'r' is pressed, get new value from the driver.
        """
        super().keyPressEvent(event)

        if event.text() == 'r':
            # This should also trigger a widget update if necessary.
            self.value_from_feat()

    def value(self):
        """Get widget value."""
        return super().value()

    def _as_update_value(self):
        # TODO: it would be nice to remove this.
        return self.value()

    def setValue(self, value):
        """Set widget value.
        """
        if value is MISSING:
            return
        super().setValue(value)

    def setReadOnly(self, value):
        """Set read only
        """
        super().setReadOnly(value)

    def value_from_feat(self):
        """Update the widget value with the current Feat value of the driver."""
        if self._feat is None or self._lantz_target is None:
            return

        if isinstance(self._feat, DictFeat):
            return getattr(self._lantz_target, self.feat.name)[self._feat_key]
        else:
            return getattr(self._lantz_target, self.feat.name)

    def value_to_feat(self):
        """Update the Feat value of the driver with the widget value."""
        if self._feat is None or self._lantz_target is None:
            return

        if isinstance(self._feat, DictFeat):
            getattr(self._lantz_target, self.feat.name)[self._feat_key] = self.value()
        else:
            setattr(self._lantz_target, self.feat.name, self.value())

    @property
    def update_on_change(self):
        return self._update_on_change

    @update_on_change.setter
    def update_on_change(self, value):
        self._update_on_change = value

    @property
    def readable(self):
        """If the Feat associated with the widget can be read (get)."""
        if self._feat is None:
            return False
        return self._feat.fget not in (None, MISSING)

    @property
    def writable(self):
        """If the Feat associated with the widget can be written (set)."""
        if self._feat is None:
            return False
        return self._feat.fset is not None

    def on_widget_value_changed(self, value, old_value=UNSET, key=MISSING):
        """When the widget is changed by the user, update the driver with
        the new value.
        """
        if key is not MISSING and key != self._feat_key:
            return
        if self._update_on_change:
            self.value_to_feat()

    def on_feat_value_changed(self, value, old_value=UNSET, key=MISSING):
        """When the driver value is changed, update the widget if necessary.
        """
        if key is not MISSING and key != self._feat_key:
            return
        if self.value() != value:
            self.setValue(value)

    @property
    def feat_key(self):
        """Key associated with the DictFeat."""
        return self._feat_key

    @feat_key.setter
    def feat_key(self, value):
        if self._lantz_target:
            getattr(self._lantz_target, self._feat.name + '_changed').disconnect(self.on_feat_value_changed)
        self._feat_key = value
        if self._lantz_target:
            getattr(self._lantz_target, self._feat.name + '_changed').connect(self.on_feat_value_changed)
        self.value_from_feat()

    @property
    def lantz_target(self):
        """Driver connected to the widget."""
        return self._lantz_target

    @lantz_target.setter
    def lantz_target(self, target):
        if self._lantz_target:
            self._feat_signal.disconnect(self.on_feat_value_changed)
            self.valueChanged.disconnect()

        if target is not None:
            self._lantz_target = target

            self._feat_signal = getattr(self._lantz_target, self._feat.name + '_changed')
            self._feat_signal.connect(self.on_feat_value_changed)

            self.value_from_feat()
            self.valueChanged.connect(self.on_widget_value_changed)

    def bind_feat(self, feat):
        if isinstance(feat, (FeatProxy, DictFeatProxy)):
            self._feat = feat.proxied

        elif isinstance(feat, (Feat, DictFeat)):
            self._feat = feat

        else:
            raise ValueError('feat argument must be an instance of Feat, DictFeat, FeatProxy or DictFeatProxy, not %s' % feat.__class__)

        if isinstance(self._feat, DictFeat):
            keys = feat.keys
        else:
            keys = None

        if keys:
            self._feat_key = keys[0]
        else:
            self._feat_key = MISSING

        self.setReadOnly(not self.writable)

    @property
    def feat(self):
        return self._feat

    @classmethod
    def _wrap(cls, widget):
        ChildrenWidgets.patch(widget)
        widget._lantz_target = None
        widget._feat = None
        widget._update_on_change = True

    @classmethod
    def wrap(cls, widget):
        if hasattr(widget, '_lantz_wrapped'):
            return

        if getattr(widget, '_IS_LANTZ_WRAPPER', False):
            widget._wrap(widget)
        else:
            wrapper_class = cls._WRAPPERS.get(type(widget), cls)
            wrapper_class._wrap(widget)
            widget.__class__ = wrapper_class

        widget._lantz_wrapped = True

    @classmethod
    def from_feat(cls, feat, parent=None):
        """Return a widget appropriate to represent a lantz feature.

        Parameters
        ----------
        feat :
            a lantz feature proxy, the result of inst.feats[feat_name].
        parent :
            parent widget. (Default value = None)
        """

        _get = cls._WRAPPERS.get

        if feat.values:
            if isinstance(feat.values, dict):
                tmp = set(feat.values.keys())
            else:
                tmp = set(feat.values)

            if tmp == {True, False}:
                widget = _get(QtGui.QCheckBox)
            else:
                widget = _get(QtGui.QComboBox)
        elif not feat.units is None or feat.limits:
            widget = _get(QtGui.QDoubleSpinBox)
        else:
            widget= _get(QtGui.QLineEdit)

        widget = widget(parent)
        cls.wrap(widget)

        return widget


class ChildrenWidgets(object):
    """Convenience class to iterate children.

    Parameters
    ----------
    parent :
        parent widget.

    """

    def __init__(self, parent):
        self.parent = parent

    def __getattr__(self, item):
        return self.parent.findChild((QtGui.QWidget, ), item)

    def __iter__(self):
        pending = [self.parent, ]
        qualname = {self.parent: self.parent.objectName()}
        while pending:
            obj = pending.pop()
            for child in obj.children():
                if not isinstance(child, QtGui.QWidget):
                    continue
                qualname[child] = qualname[obj] + '.' + child.objectName()
                pending.append(child)
                yield child.objectName(), qualname[child], child

    @classmethod
    def patch(cls, parent):
        if not hasattr(parent, 'widgets'):
            parent.widgets = cls(parent)