# -*- coding: utf-8 -*-
"""
    lantz.widgets.test
    ~~~~~~~~~~~~~~~~~~

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

from lantz.core import Driver

from ..utils.qt import QtCore, QtGui

from ..log import LOGGER
from ..config import PRINT_TRACEBACK
from ..utils.qt import QtGui
from .feat import LabeledFeatWidget
from .dialog_action import ArgumentsInputDialog


class DriverTestWidget(QtGui.QWidget):
    """Widget that is automatically filled to control all Feats of a given driver.

    Parameters
    ----------
    parent : PyQt Widget
        parent widget.
    target : Lantz
        driver object to map.

    """

    def __init__(self, parent, target):
        super().__init__(parent)
        self._lantz_target = target

        layout = QtGui.QVBoxLayout(self)

        label = QtGui.QLabel()
        label.setText('%s (%s)' % (target.name, target.__class__.__qualname__))
        layout.addWidget(label)

        recall = QtGui.QPushButton()
        recall.setText('Refresh')
        recall.clicked.connect(lambda x: target.refresh())

        update = QtGui.QPushButton()
        update.setText('Update')
        update.clicked.connect(lambda x: target.update(self.widgets_values_as_dict()))

        auto = QtGui.QCheckBox()
        auto.setText('Update on change')
        auto.setChecked(True)
        auto.stateChanged.connect(self.update_on_change)

        hlayout = QtGui.QHBoxLayout()
        hlayout.addWidget(recall)
        hlayout.addWidget(update)
        hlayout.addWidget(auto)

        layout.addLayout(hlayout)

        self.writable_widgets = []
        self.widgets = []

        # Feat
        for feat_name, feat in sorted(target.feats.items()):
            try:
                feat_widget = LabeledFeatWidget(self, target, feat)

                self.widgets.append(feat_widget)
                if feat_widget.writable:
                    self.writable_widgets.append(feat_widget)

                layout.addWidget(feat_widget)
            except Exception as ex:
                LOGGER.debug('Could not create control for {}: {}'.format(feat_name, ex))
                if PRINT_TRACEBACK:
                    import traceback
                    traceback.print_exc()

        # DictFeats
        for feat_name, feat in sorted(target.dictfeats.items()):
            try:
                feat_widget = LabeledFeatWidget(self, target, feat)

                self.widgets.append(feat_widget)
                if feat_widget.writable:
                    self.writable_widgets.append(feat_widget)

                layout.addWidget(feat_widget)
            except Exception as ex:
                LOGGER.debug('Could not create control for {}: {}'.format(feat_name, ex))
                if PRINT_TRACEBACK:
                    import traceback
                    traceback.print_exc()

        # Actions
        line = QtGui.QFrame(self)
        #self.line.setGeometry(QtCore.QRect(110, 80, 351, 31))
        line.setFrameShape(QtGui.QFrame.HLine)
        line.setFrameShadow(QtGui.QFrame.Sunken)
        layout.addWidget(line)

        actions_label = QtGui.QLabel(self)
        actions_label.setText('Actions:')
        actions_label.setFixedWidth(120)

        self.actions_combo = QtGui.QComboBox(self)
        actions = [n for n in target.actions.keys() if n not in set(Driver._lantz_actions.keys())]
        self.actions_combo.addItems(actions)

        actions_button = QtGui.QPushButton(self)
        actions_button.setFixedWidth(60)
        actions_button.setText('Run')
        actions_button.clicked.connect(self.on_run_clicked)

        alayout = QtGui.QHBoxLayout()
        alayout.addWidget(actions_label)
        alayout.addWidget(self.actions_combo)
        alayout.addWidget(actions_button)

        layout.addLayout(alayout)

        self.statusBar = QtGui.QLabel()
        self.statusBar.setText('Ready ...')
        layout.addWidget(self.statusBar)

    @QtCore.Slot()
    def on_run_clicked(self):
        func = getattr(self._lantz_target, self.actions_combo.currentText())
        args = ArgumentsInputDialog.get_params(func, self)
        self.statusBar.setText('Running ...')
        try:
            out = func(**args)
            out = 'Return value: %s' % out
        except Exception as e:
            out = 'Error: %s' % e

        self.statusBar.setText(out)

    def update_on_change(self, new_state):
        """Set the 'update_on_change' flag to new_state in each writable widget
        within this widget. If True, the driver will be updated after each change.
        """

        for widget in self.writable_widgets:
            widget.update_on_change = new_state

    def widgets_values_as_dict(self):
        return {widget.feat.name: widget._widget._as_update_value()
                for widget in self.writable_widgets}

    @property
    def lantz_target(self):
        """Driver connected to this widget."""
        return self._lantz_target

    @lantz_target.setter
    def lantz_target(self, driver):
        self._lantz_target = driver
        for widget in self.widgets:
            widget.lantz_target = driver


class SetupTestWidget(QtGui.QWidget):
    """Widget to control multiple drivers.

    Parameters
    ----------
    parent :
        parent widget.
    targets :
        iterable of driver object to map.
    """

    def __init__(self, parent, targets):
        super().__init__(parent)

        layout = QtGui.QHBoxLayout(self)

        tab_widget = QtGui.QTabWidget(self)
        tab_widget.setTabsClosable(False)
        for target in targets:
            widget = DriverTestWidget(parent, target)
            tab_widget.addTab(widget, target.name)

        layout.addWidget(tab_widget)
