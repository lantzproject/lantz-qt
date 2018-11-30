# -*- coding: utf-8 -*-
"""
    lantz.qt.app
    ~~~~~~~~~~~~

    Implements base classes for graphical applications:
    - Backend
    - Frontend



    Backend
    -------

    Upon class definition
    - Declares InstrumentSlots
    - Declares BackendSlots

    Upon construction:
    - takes kwargs linking names to actual instruments or backends instances
      and assign them to the Instrument and BackendSlots
    - Iterates over all backends instantiating them with the appropriate items
      from this backend




    :copyright: 2018 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

import os
import sys
import inspect
import collections

from pimpmyclass.mixins import LogMixin

from lantz.core.driver import Driver, Base
from lantz.core.flock import initialize_many, finalize_many

from .connect import connect_setup, connect_driver, connect_feat
from .widgets import DriverTestWidget, SetupTestWidget
from .objwrapper import QDriver
from .utils.qt import QtCore, QtGui, SuperQObject, MetaQObject
from .log import get_logger, LOGGER


ICON_FEDORA = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets', 'fedora.png')


class InstrumentSlot(object):

    def __str__(self):
        return '<InstrumentSlot>'

    def initialize(self):
        LOGGER.warning('The Instrument slot {} has not been assigned '
                       'to an actual instrument', self._slot_name )

    def finalize(self):
        pass


Front2Back = collections.namedtuple('Front2Back', 'frontend_class backend_name')


class Back2Back(collections.namedtuple('Back2Back', 'backend_class local_attribute foreign_attribute')):

    def link(self, local_name, foreign_name=None):
        return Back2Back(self.backend_class, local_name, foreign_name or local_name)


class _BackendType(MetaQObject):

    def create_instrument_property(cls, key):
        def getter(self):
            return self.instruments[key]
        def setter(self, instrument):
            instrument.name = key
            self.instruments[key] = instrument

        return property(getter, setter)

    def create_backend_property(cls, key):
        def getter(self):
            return self.backends[key]
        def setter(self, backend):
            self.backends[key] = backend

        return property(getter, setter)

    def __init__(cls, classname, bases, class_dict):
        super().__init__(classname, bases, class_dict)

        cls.instruments = dict()
        cls.backends = dict()

        for key, value in class_dict.items():
            if isinstance(value, InstrumentSlot):
                cls.instruments[key] = value
                cls.instruments[key]._slot_name = key
                setattr(cls, key, cls.create_instrument_property(key))
                LOGGER.debug('In {}, adding instrument named {} of type {}'.format(cls, key, value))
            elif value is InstrumentSlot:
                value = value()
                cls.instruments[key] = value
                cls.instruments[key]._slot_name = key
                setattr(cls, key, cls.create_instrument_property(key))
                LOGGER.debug('In {}, adding instrument named {} of type {}'.format(cls, key, value))
            elif isinstance(value, (Backend, Back2Back)):
                cls.backends[key] = value
                cls.backends[key]._slot_name = key
                setattr(cls, key, cls.create_backend_property(key))
                LOGGER.debug('In {}, adding backend named {} of type {}'.format(cls, key, value))
            else:
                LOGGER.debug('In {}, unhandled attribute named {} = {}'.format(cls, key, value))

    def __str__(cls):
        return cls.__name__


class _FrontendType(MetaQObject):

    def create_frontend_property(cls, key):
        def getter(self):
            return self.frontends[key]
        def setter(self, frontend):
            self.frontends[key] = frontend

        return property(getter, setter)

    def __init__(cls, classname, bases, class_dict):
        super().__init__(classname, bases, class_dict)

        cls.frontends = dict()

        for key, value in class_dict.items():
            if isinstance(value, Front2Back) or hasattr(value, 'frontends'):
                cls.frontends[key] = value
                setattr(cls, key, cls.create_frontend_property(key))
                LOGGER.debug('{}, adding frontend named {} of type {}'.format(cls, key, value))

    def __str__(cls):
        return cls.__name__


class Frontend(LogMixin, QtGui.QMainWindow, metaclass=_FrontendType):

    logger_name = None
    _get_logger = get_logger

    frontends = {}

     # a declarative way to indicate the user interface file to use.
    gui = None

    # connect widgets to instruments using connect_setup
    auto_connect = True

    def __init__(self, parent=None, backend=None):
        super().__init__(parent)

        self._backend = None

        if self.logger_name is None:
            self.logger_name = 'lantz.qt.frontend.' + str(self)

        if self.gui:
            for cls in self.__class__.__mro__:
                if cls is object:
                    raise ValueError('{}: loading gui file {}, reached object parent'.format(self, self.gui))

                filename = os.path.dirname(inspect.getfile(cls))
                if isinstance(self.gui, tuple):
                    filename = os.path.join(filename, *self.gui)
                else:
                    filename = os.path.join(filename, self.gui)
                if os.path.exists(filename):
                    self.log_debug('loading gui file {}'.format(filename))
                    self.widget = QtGui.loadUi(filename)
                    if isinstance(self.widget, QtGui.QMainWindow):
                        QtGui.loadUi(filename, self)
                        break
                    self.setCentralWidget(self.widget)
                    break
            else:
                raise ValueError('{}: loading gui file {}'.format(self, self.gui))

        # Iterate over all frontend items in the current frontend
        # and instantiate each of them.
        # Note: a frontend declares which sub frontend requires
        # but instantation is delegated to lantz

        for name, frontend in self.frontends.items():

            if isinstance(frontend, Front2Back):

                # The item is a frontend that requires a backend.

                cls = frontend.frontend_class
                if backend is None:
                    # If the current backend is None, then we cannot give
                    # anything to the sub frontend item
                    widget = cls()
                    self.log_debug('{} ({}) requires a backend but no backend defined'.format(name, cls))
                else:
                    # If the current backend exists then we get which of its attribute
                    # is the backend of the subfrontend
                    sub_backend_name = frontend.backend_name
                    if sub_backend_name is None:
                        # Is the same backend
                        widget = cls(backend=backend)
                        self.log_debug('{} ({}) connected to parent backend'.format(name, cls))
                    else:
                        # Is in an attribute
                        try:
                            widget = cls(backend=getattr(backend, sub_backend_name))
                        except AttributeError:
                            raise ValueError("{} ({}) requires a '{}' attribute which is not provided by {}".format(name, cls, sub_backend_name, backend))
                        self.log_debug('{} ({}) connected to backend.{}'.format(name, cls, sub_backend_name))
            else:
                # This backend does not declare a required backend
                self.log_debug('{} ({}) created'.format(name, frontend))
                widget = frontend()

            widget.setParent(self)
            setattr(self, name, widget)

        self.setupUi()
        self.backend = backend

    def __str__(self):
        return self.__class__.__name__

    def setupUi(self):
        pass

    def connect_backend(self):
        print('Connect backend %s' % repr(self))
        pass

    @property
    def backend(self):
        return self._backend

    @backend.setter
    def backend(self, backend):
        print('calling setter', self, backend, type(backend))
        if self._backend:
            self.log_debug('disconnecting backend: {}'.format(backend))
            self.disconnect(backend)

        self._backend = backend

        if backend:
            self.log_debug('connecting backend: {}'.format(backend))
            if self.auto_connect:
                connect_setup(self.widget, backend.instruments.values())

            self.connect_backend()

    @classmethod
    def using(cls, backend_name):
        return Front2Back(cls, backend_name)

    @classmethod
    def using_parent_backend(cls):
        return Front2Back(cls, backend_name=None)


class Backend(Base, SuperQObject, metaclass=_BackendType):

    _observer_signal_init = QtCore.pyqtSignal

    backends = {}
    instruments = {}

    def __init__(self, parent=None, **instruments_and_backends):

        invalid = set(dir(Base)) | set(dir(SuperQObject)) | set(dir(_BackendType))
        for name in instruments_and_backends.keys():
            if name in invalid:
                raise ValueError('{} is an invalid instrument or backend name as it collides with attribute of parent class'.format(name))

        if self.logger_name is None:
            self.logger_name = 'lantz.qt.backend.' + str(self)

        Base.__init__(self, self.logger_name)
        super().__init__(parent)

        print(self, '-->', instruments_and_backends, self.backends)
        for name, app in self.backends.items():
            if name not in instruments_and_backends:
                continue

            self.log_debug('creating sub-backend named {} with {}'.format(name, app))

            if app is Backend:
                setattr(self, name, app(parent=self))
            elif isinstance(app, Back2Back):
                cls = app.backend_class
                d = {key: }
                setattr(self, name, app(parent=self))
            d = {key: inst for key, inst in instruments_and_backends.items()
                 if key in app.instruments.keys()}
            if name in instruments_and_backends:
                d.update(instruments_and_backends[name])


        for name in self.instruments.keys():
            if name not in instruments_and_backends:
                continue

            inst = instruments_and_backends[name]
            self.log_debug('relating instrument named {} with {}'.format(name, inst))
            setattr(self, name, inst)
            inst.setParent(self)

        # TODO: Check for all instruments exists

    def __str__(self):
        return self.__class__.__name__

    def initialize(self, register_finalizer=False):
        initialize_many(self.instruments.values(), register_finalizer=register_finalizer)

    def finalize(self):
        finalize_many(self.instruments.values())

    def __enter__(self):
        self.initialize(register_finalizer=False)
        return self

    def __exit__(self, *args):
        self.finalize()

    def invoke(self, func, *args, **kwargs):
        QtCore.QTimer.singleShot(0, lambda: func(*args, **kwargs))

    @classmethod
    def link(self, cls, local_name, foreign_name=None):
        return Back2Back(cls, local_name, foreign_name or local_name)


def start_gui_app(backend, frontend_class, qapp_or_args=None):
    if isinstance(qapp_or_args, QtGui.QApplication):
        qapp = qapp_or_args
    else:
        qapp = QtGui.QApplication(qapp_or_args or [''])
        qapp.setWindowIcon(QtGui.QIcon(ICON_FEDORA))

    background_thread = QtCore.QThread()
    backend.moveToThread(background_thread)
    background_thread.start()

    frontend = frontend_class(backend=backend)
    frontend.show()

    qapp.aboutToQuit.connect(background_thread.quit)

    if sys.platform.startswith('darwin'):
        frontend.raise_()

    sys.exit(qapp.exec_())


def start_test_app(target, width=500, qapp_or_args=None):
    """Start a single window test application with a form automatically
    generated for the driver.

    Parameters
    ----------
    target :
        a driver object or a collection of drivers.
    width :
        to be used as minimum width of the window. (Default value = 500)
    qapp_or_args :
        arguments to be passed to QApplication. (Default value = None)

    Returns
    -------

    """

    if isinstance(qapp_or_args, QtGui.QApplication):
        qapp = qapp_or_args
    else:
        qapp = QtGui.QApplication(qapp_or_args or [''])
        qapp.setWindowIcon(QtGui.QIcon(ICON_FEDORA))

    if isinstance(target, (Driver, QDriver)):
        main = DriverTestWidget(None, target)
    else:
        main = SetupTestWidget(None, target)

    main.setMinimumWidth(width)
    main.setWindowTitle('Lantz Driver Test Panel')
    main.show()
    if sys.platform.startswith('darwin'):
        main.raise_()
    qapp.exec_()


def start_gui(ui_filename, drivers, qapp_or_args=None):
    """Start a single window application with a form generated from
    a designer file.

    Parameters
    ----------
    ui_filename :
        the full path of a file generated with QtDesigner.
    drivers :
        a driver object or a collection of drivers.
    qapp_or_args :
        arguments to be passed to QApplication. (Default value = None)

    Returns
    -------

    """

    if isinstance(qapp_or_args, QtGui.QApplication):
        qapp = qapp_or_args
    else:
        qapp = QtGui.QApplication(qapp_or_args or [''])
        qapp.setWindowIcon(QtGui.QIcon(ICON_FEDORA))

    main = QtGui.loadUi(ui_filename)

    if isinstance(drivers, Driver):
        connect_driver(main, drivers)
    else:
        connect_setup(main, drivers)

    main.show()
    if sys.platform.startswith('darwin'):
        main.raise_()
    qapp.exec_()


def start_frontend(frontend_class, qapp_or_args=None):
    if isinstance(qapp_or_args, QtGui.QApplication):
        qapp = qapp_or_args
    else:
        qapp = QtGui.QApplication(qapp_or_args or [''])
        qapp.setWindowIcon(QtGui.QIcon(ICON_FEDORA))

    frontend = frontend_class()
    frontend.show()

    if sys.platform.startswith('darwin'):
        frontend.raise_()

    sys.exit(qapp.exec_())

