# -*- coding: utf-8 -*-
"""
    lantz.widgets.dialog_action
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    PyQt Dialog that inspect a function and opens a dialog to ask
    for values for each argument.

    :copyright: 2018 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

import inspect
import json

from ..log import LOGGER
from ..utils.docscrape import NumpyDocString
from ..utils.qt import QtCore, QtGui


class ArgumentsInputDialog(QtGui.QDialog):
    """Dialog to select values for arguments.

    Parameters
    ----------
    func : callable

    parent : PyQt Widget
        parent widget.

    Example
    -------
    You can call it to get the parameters of a function:
    >>> args = ArgumentsInputDialog.get_params(func, parent)
    >>> func(*args)

    Or you can call it to enter the parameters of a function and run it:
    >>> args = ArgumentsInputDialog.run(func, parent)

    """
    def __init__(self, argspec, parent=None, window_title='Function arguments', doc=None):
        super().__init__(parent)

        vlayout = QtGui.QVBoxLayout(self)

        layout = QtGui.QFormLayout()

        widgets = []

        defaults = argspec.defaults if argspec.defaults else ()
        defaults = ('', ) * (len(argspec.args[1:]) - len(defaults)) + defaults

        self.arguments = {}
        for arg, default in zip(argspec.args[1:], defaults):
            wid = QtGui.QLineEdit(self)
            wid.setObjectName(arg)
            wid.setText(json.dumps(default))
            self.arguments[arg] = default

            layout.addRow(arg, wid)
            widgets.append(wid)
            wid.textChanged.connect(self.on_widget_change(wid))
            if doc and arg in doc:
                wid.setToolTip(doc[arg])

        self.widgets = widgets

        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        buttonBox.setEnabled(True)
        buttonBox.accepted.connect(self.accept)

        vlayout.addLayout(layout)

        label = QtGui.QLabel()
        label.setText('Values are decoded from text using as JSON.')
        vlayout.addWidget(label)

        vlayout.addWidget(buttonBox)

        self.buttonBox = buttonBox
        self.valid = {wid.objectName(): True for wid in self.widgets}

        self.setWindowTitle(window_title)

    def on_widget_change(self, widget):
        name = widget.objectName()
        def validate(value):
            try:
                if value:
                    value = json.loads(value)
                else:
                    value = None
                palette = QtGui.QPalette()
                palette.setColor(widget.backgroundRole(), QtGui.QColor('white'))
                widget.setPalette(palette)
                self.arguments[name] = value
                self.valid[name] = True
            except:
                palette = QtGui.QPalette()
                palette.setColor(widget.backgroundRole(), QtGui.QColor(255, 102, 102))
                widget.setPalette(palette)
                self.valid[name] = False

            self.buttonBox.setEnabled(all(self.valid.values()))

        return validate

    def accept(self):
        super().accept()

    @staticmethod
    def run(func, parent=None):
        """Display a dialog for a function and run
        """

        wrapped = getattr(func, '__wrapped__', func)
        name = wrapped.__name__

        arguments = ArgumentsInputDialog.get_params(func, parent)

        try:
            return func(**arguments)
        except Exception as e:
            LOGGER.exception(e)
            QtGui.QMessageBox.critical(parent, 'Lantz',
                                       'Instrument error while calling {}'.format(name),
                                       QtGui.QMessageBox.Ok,
                                       QtGui.QMessageBox.NoButton)

    @staticmethod
    def get_params(func, parent=None):
        """Creates and display a UnitInputDialog and return new units.
        """

        wrapped = getattr(func, '__wrapped__', func)
        name = wrapped.__name__
        doc = wrapped.__doc__
        argspec = inspect.getargspec(wrapped)

        arguments = {}
        if len(argspec.args) > 1:
            doc = NumpyDocString(doc).get('Parameters', [])
            doc = {k: '\n'.join(v) for (k, _, v) in doc}

            dialog = ArgumentsInputDialog(argspec, parent,
                                          window_title=name + ' arguments',
                                          doc=doc)
            if not dialog.exec_():
                return None

            arguments = dialog.arguments

        return arguments
