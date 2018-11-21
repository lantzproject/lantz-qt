

from lantz import ArgumentParserSC


def main(args=None):
    """Run simulators.
    """
    parser = ArgumentParserSC('demo', CHOICES, description='Run Lantz QtDemo.')
    parser.dispatch(args)


def testpanel_demo(args=None):
    """Run simulators.
    """

    from lantz.qt.utils.qt import QtGui
    """
    QtGui.QMessageBox.information(None,
                                  'Lantz Test Panel Demo'
                                  'Please run the following command in the console\n'
                                  'to start the simulator:\n\n'
                                  '    lantz sims fungen tcp')
    """
    print('Please make sure that the simulator is running.\n'
          'You can start it by running the following command in another terminal:\n\n'
          'lantz sims fungen tcp')

    from lantz.drivers.examples import LantzSignalGenerator

    from lantz.qt import start_test_app, wrap_driver_cls

    QLantzSignalGenerator = wrap_driver_cls(LantzSignalGenerator)
    with QLantzSignalGenerator('TCPIP::localhost::5678::SOCKET') as inst:
        start_test_app(inst)


def uifile_demo(args=None):
    print('Please make sure that the simulator is running.\n'
          'You can start it by running the following command in another terminal:\n\n'
          'lantz sims fungen tcp')

    import os

    UIFILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets', 'fungen.ui')

    from lantz.drivers.examples import LantzSignalGenerator

    from lantz.qt import start_gui, wrap_driver_cls

    QLantzSignalGenerator = wrap_driver_cls(LantzSignalGenerator)
    with QLantzSignalGenerator('TCPIP::localhost::5678::SOCKET') as inst:
        start_gui(UIFILE, inst)


def featscan_demo(args=None):

    print('Please make sure that the simulator is running.\n'
          'You can start it by running the following command in another terminal:\n\n'
          'lantz sims fungen tcp')

    # We import a helper function to start the app
    from lantz.qt import start_gui_app, wrap_driver_cls

    # The block consists of two parts the backend and the frontend
    from lantz.qt.blocks import FeatScan, FeatScanUi

    # An this you know already
    from lantz.drivers.examples import LantzSignalGenerator

    QLantzSignalGenerator = wrap_driver_cls(LantzSignalGenerator)

    with QLantzSignalGenerator('TCPIP::localhost::5678::SOCKET') as fungen:

        # Here we instantiate the backend setting 'frequency' as the Feat to scan
        # and specifying in which instrument
        app = FeatScan('frequency', instrument=fungen)

        # Now we use the helper to start the app.
        # It takes a Backend instance and a FrontEnd class
        start_gui_app(app, FeatScanUi)


def flock_demo(args=None):

    # TODO: Make this an actual flock

    print('Please make sure that the simulator is running.\n'
          'You can start it by running the following command in another terminal:\n\n'
          'lantz sims fungen tcp')

    # We import a helper function to start the app
    from lantz.qt import start_gui_app, wrap_driver_cls

    # The block consists of two parts the backend and the frontend
    from lantz.qt.blocks import FeatScan, FeatScanUi

    # An this you know already
    from lantz.drivers.examples import LantzSignalGenerator

    QLantzSignalGenerator = wrap_driver_cls(LantzSignalGenerator)

    with QLantzSignalGenerator('TCPIP::localhost::5678::SOCKET') as fungen:

        # Here we instantiate the backend setting 'frequency' as the Feat to scan
        # and specifying in which instrument
        app = FeatScan('frequency', instrument=fungen)

        # Now we use the helper to start the app.
        # It takes a Backend instance and a FrontEnd class
        start_gui_app(app, FeatScanUi)



CHOICES = {'testpanel': testpanel_demo,
           'uifile': uifile_demo,
           'featscan': featscan_demo}

if __name__ == '__main__':
    main()
