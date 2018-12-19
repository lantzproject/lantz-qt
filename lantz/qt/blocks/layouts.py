# -*- coding: utf-8 -*-
"""
    lantz.ui.layouts
    ~~~~~~~~~~~~~~~~

    Frontends to automatically locate widgets.

    :copyright: 2015 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""


from ..utils.qt import QtGui
from ..app import Frontend


class _CommonUi:
    """The Loop frontend provides a GUI for the Rich Backend"""

    def _add(self, layout, parts):
        """Add widgets in parts to layout.

        Parameters
        ----------
        layout :
            
        parts :
            

        Returns
        -------

        """
        for part_name in parts:
            if part_name is True:
                layout.addStretch()
                continue

            part = getattr(self, part_name)

            if isinstance(part, Frontend):
                layout.addWidget(part)

            elif isinstance(part, tuple):
                # A tuple found in parts is considered nesting
                if isinstance(layout, self._inner):
                    sublayout = self._outer()
                elif isinstance(layout, self._outer):
                    sublayout = self._inner()
                else:
                    raise ValueError('Unknown parent layout %s' % layout)

                self._add(sublayout, part)

                layout.setLayout(sublayout)

            else:
                raise ValueError('Only Frontend or tuple are valid values '
                                 'valid for parts not %s (%s)' % (part, type(part)))

        return layout


class _PanelsUi(_CommonUi, Frontend):

    gui = 'placeholder.ui'

    auto_connect = False

    #: Tuple with the columns
    #: Each element can be:
    #:   - Frontend class: will be connected to the default backend.
    #:   - Front2Back(Frontend class, backend name): will be connect to a specific backend.
    #:   - tuple: will be iterated to obtain the rows.
    parts = ()

    _inner, _outer = None, None

    def setupUi(self):
        super().setupUi()
        layout = self._outer()
        self._add(layout, self.parts)
        self.widget.placeholder.setLayout(layout)


class VerticalUi(_PanelsUi):
    """Uses a vertical box layout to locate widgets."""

    _inner, _outer = QtGui.QHBoxLayout, QtGui.QVBoxLayout


class HorizonalUi(_PanelsUi):
    """Uses a horizontal box layout to locate widgets."""

    _inner, _outer = QtGui.QVBoxLayout, QtGui.QHBoxLayout


from ..app import Frontend


class ToolbarLeftRightUi(_CommonUi, Frontend):
    """The Loop frontend provides a GUI for the Rich Backend"""

    gui = 'left_main_center.ui'

    auto_connect = False

    #: Tuple with the columns
    #: Each element can be:
    #:   - Frontend class: will be connected to the default backend.
    #:   - Front2Back(Frontend class, backend name): will be connect to a specific backend.
    #:   - tuple: will be iterated to obtain the rows.
    toolbar = ()
    left = ()
    center = ()

    def setupUi(self):
        super().setupUi()

        self.widget.topbar.setLayout(self._add(QtGui.QHBoxLayout(), self.toolbar))
        self.widget.leftbar.setLayout(self._add(QtGui.QVBoxLayout(), self.left))
        self.setCentralWidget(self.center)

