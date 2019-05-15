# -*- coding: utf-8 -*-
"""
    lantz.widgets.numeric
    ~~~~~~~~~~~~~~~~~~~~~

    Numeric widgets.
    - QDoubleSpinBox
    - CheckBox
    - QLineEdit
    - QSlider
    - QDial
    - QProgressBar
    - QScrollBar
    - QLCDNumber

    :copyright: 2018 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from lantz.core import Q_
from lantz.core.helpers import MISSING, UNSET

from ..utils.qt import QtGui
from .dialog_units import UnitInputDialog
from .common import WidgetMixin, register_wrapper


@register_wrapper
class MagnitudeMixin(WidgetMixin):

    _WRAPPED = (QtGui.QDoubleSpinBox, QtGui.QSpinBox)

    abbreviated_units = True
    pretty_units = False

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if self._units and event.text() == 'u':
            self.change_units(request_new_units(self.value()))

    def bind_feat(self, feat):
        super().bind_feat(feat)

        #: self._units are the current units displayed by the widget.
        #: Respects units declared in the suffix

        if feat.units:
            suf = (self.suffix() if hasattr(self, 'suffix') else feat.units) or feat.units
            self._units = Q_(1, suf)
            self.change_units(self._units)
        else:
            self._units = None
            if feat.limits:
                self.change_limits(None)

    def change_units(self, new_units):
        """Update displayed suffix and stored units.
        """
        if new_units is None:
            return
        try:
            rescaled = self.value().to(new_units)
        except ValueError:
            # incompatible units
            return None
        else:
            if hasattr(self, 'setSuffix'):
                if self.abbreviated_units:
                    fmt = '~'
                else:
                    fmt = ''

                if self.pretty_units:
                    fmt += 'P'

                if fmt:
                    fmt = '{:%s}' % fmt
                else:
                    fmt = '{}'

                self.setSuffix(' ' + fmt.format(new_units.units))

            self.change_limits(new_units)
            self._units = new_units

            self.setValue(rescaled)

    def change_limits(self, new_units):
        """Change the limits (range) of the control taking the original values
        from the feat and scaling them to the new_units.
        """
        if not hasattr(self, 'setRange'):
            return

        rng = self._feat.limits

        if not rng:
            return

        if new_units:
            conv = lambda ndx: Q_(rng[ndx], self._feat.units).to(new_units).magnitude
        else:
            conv = lambda ndx: rng[ndx]

        if len(rng) == 1:
            self.setRange(0, conv(0))
        else:
            self.setRange(conv(0), conv(1))
            if len(rng) == 3:
                self.setSingleStep(conv(2))

    def value(self):
        """Get widget value and scale by units."""
        if self._units:
            return Q_(super().value(), self._units)
        return super().value()

    def setValue(self, value):
        """Set widget value scaled by units.
        """
        if value is MISSING or value is UNSET:
            font = QtGui.QFont()
            font.setItalic(True)
            self.setFont(font)
        elif isinstance(value, Q_):
            super().setValue(value.to(self._units).magnitude)
        else:
            super().setValue(value)


@register_wrapper
class SliderMixin(MagnitudeMixin):

    _WRAPPED = (QtGui.QSlider, QtGui.QDial, QtGui.QProgressBar, QtGui.QScrollBar)

    def setReadOnly(self, value):
        super().setEnabled(not value)


@register_wrapper
class LCDNumberMixin(MagnitudeMixin):

    _WRAPPED = (QtGui.QLCDNumber, )

    @classmethod
    def _wrap(cls, widget):
        super()._wrap(widget)
        #TODO: Create a real valueChanged Signal.
        widget.valueChanged = widget.overflow

    def setReadOnly(self, value):
        super().setEnabled(not value)

    def setValue(self, value):
        if value is MISSING or value is UNSET:
            font = QtGui.QFont()
            font.setItalic(True)
            self.setFont(font)
            return
        elif isinstance(value, Q_):
            super().display(value.to(self._units).magnitude)
        else:
            super().display(value)

    def value(self):
        return super().value()


def request_new_units(current_units):
    """Ask for new units using a dialog box and return them.

    Parameters
    ----------
    current_units : Quantity
        current units or magnitude.

    Returns
    -------
    None or Quantity
    """
    new_units = UnitInputDialog.get_units(current_units)
    if new_units is None:
        return None

    try:
        return Q_(1, new_units)
    except LookupError:
        # cannot parse units
        return None

