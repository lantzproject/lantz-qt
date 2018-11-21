# -*- coding: utf-8 -*-
"""
    lantz.widgets.dialog_units
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Dialog to allow the user to select a new, compatible unit.

    :copyright: 2018 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""


from lantz.core import Q_
from ..utils.qt import QtCore, QtGui


class UnitInputDialog(QtGui.QDialog):
    """Dialog to select new units. Checks compatibility while typing
    and does not allow to continue if incompatible.

    Parameters
    ----------
    units : Quantity
        Quantity with source units.
    parent : PyQt Widget
        parent widget.


    Example
    -------
    >>> new_units = UnitInputDialog.get_units('ms')

    """

    def __init__(self, units, parent=None):
        super().__init__(parent)
        self.setupUi(parent)
        self.units = units
        self.source_units.setText(str(units.units))

    def setupUi(self, parent):
        self.resize(275, 172)
        self.setWindowTitle('Convert units')
        self.layout = QtGui.QVBoxLayout(parent)
        self.layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        align = (QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)

        self.layout1 = QtGui.QHBoxLayout()
        self.label1 = QtGui.QLabel()
        self.label1.setMinimumSize(QtCore.QSize(100, 0))
        self.label1.setText('Convert from:')
        self.label1.setAlignment(align)

        self.layout1.addWidget(self.label1)
        self.source_units = QtGui.QLineEdit()
        self.source_units.setReadOnly(True)
        self.layout1.addWidget(self.source_units)

        self.layout.addLayout(self.layout1)

        self.layout2 = QtGui.QHBoxLayout()
        self.label2 = QtGui.QLabel()
        self.label2.setMinimumSize(QtCore.QSize(100, 0))
        self.label2.setText('to:')
        self.label2.setAlignment(align)
        self.layout2.addWidget(self.label2)

        self.destination_units = QtGui.QLineEdit()
        self.layout2.addWidget(self.destination_units)

        self.layout.addLayout(self.layout2)

        self.message = QtGui.QLabel()
        self.message.setText('')
        self.message.setAlignment(QtCore.Qt.AlignCenter)

        self.layout.addWidget(self.message)

        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.layout.addWidget(self.buttonBox)
        self.buttonBox.setEnabled(False)

        self.buttonBox.accepted.connect(self.accept)
        self.destination_units.textChanged.connect(self.check)

        self.setLayout(self.layout)
        self.destination_units.setFocus()

    def check(self):
        units = self.destination_units.text().strip()
        if not units:
            return
        try:
            new_units = Q_(1, units)
            factor = self.units.to(new_units).magnitude
        except LookupError or SyntaxError:
            self.message.setText('Cannot parse units')
            self.buttonBox.setEnabled(False)
        except ValueError:
            self.message.setText('Incompatible units')
            self.buttonBox.setEnabled(False)
        except AttributeError:
            self.message.setText('Unknown units')
            self.buttonBox.setEnabled(False)
        else:
            self.message.setText('factor {:f}'.format(factor))
            self.buttonBox.setEnabled(True)

    @staticmethod
    def get_units(units):
        """Creates and display a UnitInputDialog and return new units.

        Parameters
        ----------
        units : str
            current units.

        Returns
        -------
        str or None
            output compatible units.
            Returns None if cancelled.

        """

        if isinstance(units, str):
            units = Q_(1, units)

        dialog = UnitInputDialog(Q_(1, units.units))
        if dialog.exec_():
            return dialog.destination_units.text()
        return None