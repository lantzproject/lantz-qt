# -*- coding: utf-8 -*-
"""
    lantz.ui.connect
    ~~~~~~~~~~~~~~~~

    Implements UI widgets based on Qt widgets. To achieve functionality,
    instances of QtWidgets are patched.

    :copyright: 2015 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

import time

from lantz.core import initialize_many
from lantz.core import Driver
from lantz.core.driver import Base
from lantz.core.helpers import MISSING

from .log import LOGGER
from .utils.qt import QtCore, QtGui
from .widgets import WidgetMixin, ChildrenWidgets


def connect_feat(widget, target, feat_name=None, feat_key=MISSING):
    """Connect a feature from a given driver to a widget. Calling this
    function also patches the widget is necessary.
    
    If applied two times with the same widget, it will connect to the target
    provided in the second call. This behaviour can be useful to change the
    connection target without rebuilding the whole UI. Alternative, after
    connect has been called the first time, widget will have a property
    `lantz_target` that can be used to achieve the same thing.

    Parameters
    ----------
    widget : QtWidget
        widget instance.
    target : Driver
        driver instance.
    feat_name : str
        feature name. If None, connect using widget name. (Default value = None)
    feat_key : str
        For a DictFeat, this defines which key to show. (Default value = MISSING)

    """

    LOGGER.debug('Connecting {} to {}, {}, {}'.format(widget, target, feat_name, feat_key))

    if not isinstance(target, Base):
        raise TypeError('Connect target must be an instance of Driver or Backend, not {}'.format(target))

    if not feat_name:
        feat_name = widget.objectName()

    #: Reconnect
    if hasattr(widget, '_feat.name') and widget._feat.name == feat_name:
        widget.lantz_target = target
        return

    try:
        feat = target.feats[feat_name]
    except KeyError:
        try:
            feat = target.dictfeats[feat_name]
        except KeyError:
            raise KeyError("Cannot find feat/dictfeat '{}' in {}".format(feat_name, target))

    WidgetMixin.wrap(widget)
    widget.bind_feat(feat)
    widget.feat_key = feat_key

    widget.lantz_target = target
    widget.setValue(widget.value_from_feat())


def connect_driver(parent, target, *, prefix='', sep='__'):
    """Connect all children widgets to their corresponding lantz feature
    matching by name. Non-matching names are ignored.

    Parameters
    ----------
    parent : QtWidget
        parent widget.
    target : driver
        the driver.
    prefix : str
        prefix to be prepended to the lantz feature (default = '')
    sep : str
        separator between prefix, name and suffix (Default value = '__')

    """

    LOGGER.debug('Connecting {} to {}, {}, {}'.format(parent, target, prefix, sep))

    ChildrenWidgets.patch(parent)

    if prefix:
        prefix += sep

    for name, _, wid in parent.widgets:
        if prefix and name.startswith(prefix):
            name = name[len(prefix):]
        if sep in name:
            name, _ = name.split(sep, 1)
        if name in target.feats:
            connect_feat(wid, target, name)


def connect_setup(parent, targets, *, prefix=None, sep='__'):
    """Connect all children widget to their corresponding

    Parameters
    ----------
    parent : QtWidget
        parent widget.
    targets : iterable of Driver
        iterable of drivers.
    prefix : str
        prefix to be prepended to the lantz feature name
        if None, the driver name will be used (default)
        if it is a dict, the driver name will be used to obtain
        he prefix.
    sep : str
         (Default value = '__')

    """

    LOGGER.debug('Connecting {} to {}, {}, {}'.format(parent, targets, prefix, sep))

    ChildrenWidgets.patch(parent)
    for target in targets:
        name = target.name
        if isinstance(prefix, dict):
            name = prefix[name]
        connect_driver(parent, target, prefix=name, sep=sep)


def connect_initialize_flock(widget, flock, register_finalizer=True,
                             initializing_msg='Initializing ...', initialized_msg='Initialized',
                             concurrent=True):
    """Initialize drivers while reporting the status in a QtWidget.

    Parameters
    ----------
    widget : QtWidget
        Qt Widget where the status information is going to be shown.
    flock : Flock object

    register_finalizer : bool
        register driver.finalize method to be called at python exit. (Default value = True)
    initializing_msg : str
        message to be displayed while initializing. (Default value = 'Initializing ...')
    initialized_msg : str
        message to be displayed after successful initialization. (Default value = 'Initialized')
    concurrent : bool
        indicates that drivers with satisfied dependencies
        should be initialized concurrently. (Default value = True)

    Returns
    -------
    type
        the QThread doing the initialization.

    """
    return connect_initialize(widget, flock.values(), register_finalizer,
                              initializing_msg, initialized_msg,
                              concurrent, flock.dependencies)


def connect_initialize(widget, drivers, register_finalizer=True,
                       initializing_msg='Initializing ...', initialized_msg='Initialized',
                       concurrent=True, dependencies=None):
    """Initialize drivers while reporting the status in a QtWidget.

    Parameters
    ----------
    widget : QtWidget
        Qt Widget where the status information is going to be shown.
    drivers : iterable of drivers
        iterable of drivers to initialize.
    register_finalizer : bool
        register driver.finalize method to be called at python exit. (Default value = True)
    initializing_msg : str
        message to be displayed while initializing. (Default value = 'Initializing ...')
    initialized_msg : str
        message to be displayed after successful initialization. (Default value = 'Initialized')
    concurrent : bool
        indicates that drivers with satisfied dependencies
        should be initialized concurrently. (Default value = True)
    dependencies : dict
        indicates which drivers depend on others to be initialized.
        each key is a driver name, and the corresponding
        value is an iterable with its dependencies. (Default value = None)

    Returns
    -------
    type
        the QThread doing the initialization.

    """
    timing = {}

    thread = QtCore.QThread()
    helper = InitializerHelper(drivers, register_finalizer, concurrent, dependencies)
    helper.moveToThread(thread)
    thread.helper = helper

    if isinstance(widget, QtGui.QTableWidget):
        def _initializing(driver):
            timing[driver] = time.perf_counter()
            row = drivers.index(driver)
            widget.setItem(row, 2, QtGui.QTableWidgetItem(initializing_msg))

        def _initialized(driver):
            delta = time.perf_counter() - timing[driver]
            row = drivers.index(driver)
            widget.setItem(row, 2, QtGui.QTableWidgetItem(initialized_msg + ' ({:.1f} sec)'.format(delta)))

        def _exception(driver, e):
            delta = time.perf_counter() - timing[driver]
            row = drivers.index(driver)
            widget.setItem(row, 2, QtGui.QTableWidgetItem('{} ({:.1f} sec)'.format(e, delta)))

        def _done(duration):
            widget.setItem(len(drivers), 2, QtGui.QTableWidgetItem('{:.1f} sec'.format(duration)))
            thread.quit()

        widget.clearContents()
        widget.setRowCount(len(drivers) + 1)
        for ndx, onedriver in enumerate(drivers):
            widget.setItem(ndx, 0, QtGui.QTableWidgetItem(onedriver.name))
            widget.setItem(ndx, 1, QtGui.QTableWidgetItem(onedriver.__class__.__name__))
            widget.setItem(ndx, 2, QtGui.QTableWidgetItem(''))

        widget.resizeColumnToContents(0)
        widget.horizontalHeader().setStretchLastSection(True)

    elif isinstance(widget, QtGui.QLineEdit):
        def _initializing(driver):
            timing[driver] = time.perf_counter()
            widget.setText('{} ({}) > {}'.format(driver.name, driver.__class__.__name__,
                                                 initializing_msg))

        def _initialized(driver):
            delta = time.perf_counter() - timing[driver]
            widget.setText('{} ({}) > {} ({:.1f} sec)'.format(driver.name, driver.__class__.__name__,
                                                              initialized_msg, delta))

        def _exception(driver, e):
            delta = time.perf_counter() - timing[driver]
            widget.setText('{} ({}) > {} ({:.1f} sec)'.format(driver.name, driver.__class__.__name__,
                                                              e, delta))

        def _done(duration):
            widget.setText('Initialized in {:.1f} sec'.format(duration))
            thread.quit()

        widget.setReadOnly(True)

    elif isinstance(widget, QtGui.QTextEdit):

        def _initializing(driver):
            timing[driver] = time.perf_counter()
            widget.append('{} ({}) > {}'.format(driver.name, driver.__class__.__name__,
                                                initializing_msg))

        def _initialized(driver):
            delta = time.perf_counter() - timing[driver]
            widget.append('{} ({}) > {} ({:.1f} sec)'.format(driver.name, driver.__class__.__name__,
                                                             initialized_msg, delta))

        def _exception(driver, e):
            delta = time.perf_counter() - timing[driver]
            widget.append('{} ({}) > {} ({:.1f} sec)'.format(driver.name, driver.__class__.__name__,
                                                             e, delta))

        def _done(duration):
            widget.append('Initialized in {:.1f} sec'.format(duration))
            thread.quit()

        widget.setReadOnly(True)

    else:
        raise TypeError('Unknown widget type {}.'.format(type(widget)))

    thread.started.connect(helper.process)
    helper.initializing.connect(_initializing)
    helper.initialized.connect(_initialized)
    helper.exception.connect(_exception)
    helper.finished.connect(_done)

    thread.start()
    return thread, helper


class InitializerHelper(QtCore.QObject):

    initializing = QtCore.Signal(object)
    initialized = QtCore.Signal(object)
    exception = QtCore.Signal(object, object)
    finished = QtCore.Signal(float)

    def __init__(self, drivers, register_finalizer, parallel, dependencies):
        super().__init__()
        self.drivers = drivers
        self.register_finalizer = register_finalizer
        self.parallel = parallel
        self.dependencies = dependencies

    def process(self):
        start = time.perf_counter()
        initialize_many(drivers=self.drivers, register_finalizer=self.register_finalizer,
                        on_initializing=self.on_initializing,
                        on_initialized=self.on_initialized,
                        on_exception=self.on_exception,
                        concurrent=self.parallel,
                        dependencies=self.dependencies)
        self.finished.emit(time.perf_counter() - start)

    def on_initializing(self, driver):
        self.initializing.emit(driver)

    def on_initialized(self, driver):
        self.initialized.emit(driver)

    def on_exception(self, driver, ex):
        self.exception.emit(driver, ex)
