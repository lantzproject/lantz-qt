

def main(args=None):
    """Run simulators.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Run Lantz QtDemo.')
    parser.add_argument('demo', choices=list(CHOICES.keys()))
    args, pending = parser.parse_known_args(args)
    print('Dispatching ' + args.demo)

    CHOICES[args.demo](pending)


def test_panel_demo(args=None):
    """Run simulators.
    """

    from lantz_qt.utils.qt import QtGui
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
    from lantz_qt import start_test_app
    from lantz.drivers.examples import LantzSignalGenerator
    from lantz_qt.objwrapper import wrap_driver_cls
    QLantzSignalGenerator = wrap_driver_cls(LantzSignalGenerator)
    with QLantzSignalGenerator('TCPIP::localhost::5678::SOCKET') as inst:
        start_test_app(inst)


CHOICES = {'testpanel': test_panel_demo}

if __name__ == '__main__':
    main()
